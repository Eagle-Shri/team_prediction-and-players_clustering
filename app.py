from flask import Flask, render_template, request, redirect, url_for
from config import Config
import csv
from sqlalchemy.exc import SQLAlchemyError

# SQLAlchemy models
from models import db, Player, Coach

from flask import flash, session
# MongoDB logger
from mongo import log_activity
from mongo.mongo_logs import logs as mongo_logs
# Clustering utility
from ml.clustering import predict_cluster_and_performance

# -------------------- APP INIT --------------------
app = Flask(__name__)
app.config.from_object(Config)

# Optimize database settings
app.config['SQLALCHEMY_POOL_SIZE'] = 10
app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600
app.config['SQLALCHEMY_POOL_PRE_PING'] = True

db.init_app(app)

# -------------------- DATASET LOADER --------------------
def load_players_from_csv():
    """Load players from CSV with batch commits and rating-based clustering"""
    try:
        with open("data/fifa_players_clustered_output.csv", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            batch_size = 100
            batch = []

            for row in reader:
                try:
                    if row.get("overall_rating") in ("", None):
                        continue

                    rating = float(row.get("overall_rating", 0))
                    
                    # Use predict_cluster_and_performance to calculate based on rating
                    prediction = predict_cluster_and_performance(rating)

                    player = Player(
                        name=row.get("name", "Unknown"),
                        age=int(float(row.get("age", 0))),
                        positions=row.get("positions", "Unknown"),
                        overall_rating=rating,
                        cluster=prediction['cluster'],
                        performance_label=prediction['performance_label']
                    )
                    batch.append(player)

                    if len(batch) >= batch_size:
                        db.session.add_all(batch)
                        db.session.commit()
                        batch = []

                except (ValueError, TypeError):
                    continue

            # Commit remaining items
            if batch:
                db.session.add_all(batch)
                db.session.commit()
        
        print(f"✅ Loaded players from CSV successfully")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        db.session.rollback()

# -------------------- ROUTES --------------------

# Home
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Validate against database
        if not username or not password:
            return render_template(
                "login.html",
                error="Please enter username and password"
            )

        # Query database for user
        coach = Coach.query.filter_by(username=username).first()

        if coach and coach.check_password(password):
            # Password is correct
            session["user"] = username
            session["user_id"] = coach.id
            log_activity(username, "Coach logged in")
            return redirect(url_for("dashboard"))
        else:
            # User not found or password incorrect
            return render_template(
                "login.html",
                error="Invalid username or password"
            )

    return render_template("login.html", error=None)



#register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")

        if password != confirm:
            flash("Passwords do not match", "danger")
            return render_template("register.html")

        # Check if username already exists
        existing_user = Coach.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists", "danger")
            return render_template("register.html")

        # Check if email already exists
        existing_email = Coach.query.filter_by(email=email).first()
        if existing_email:
            flash("Email already registered", "danger")
            return render_template("register.html")

        # Create new coach and save to database
        coach = Coach(username=username, email=email)
        coach.set_password(password)
        
        db.session.add(coach)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        log_activity(username, "Coach registered")
        return redirect(url_for("login"))

    return render_template("register.html")

#logout
@app.route("/logout")
def logout():
    session.clear()   # clears login session
    return redirect(url_for("login"))


# Dashboard
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    try:
        # Use cached counts instead of multiple queries
        total = Player.query.count()
        top = Player.query.filter_by(performance_label="Top Performer").count()
        avg = Player.query.filter_by(performance_label="Average Performer").count()
        low = Player.query.filter_by(performance_label="Low Performer").count()

        return render_template(
            "dashboard.html",
            user=session["user"],
            total=total,
            top=top,
            avg=avg,
            low=low
        )
    except SQLAlchemyError as e:
        print(f"❌ Database error in dashboard: {e}")
        flash("Database connection error", "danger")
        return render_template(
            "dashboard.html",
            user=session["user"],
            total=0, top=0, avg=0, low=0
        )


# View Players with Pagination
@app.route("/players")
def players():
    try:
        performance = request.args.get("performance", "all")
        min_rating = request.args.get("min_rating", type=float)
        max_rating = request.args.get("max_rating", type=float)
        page = request.args.get("page", 1, type=int)
        per_page = 20  # Limit results per page
        
        query = Player.query
        
        if performance != "all":
            query = query.filter_by(performance_label=performance)
        
        if min_rating is not None:
            query = query.filter(Player.overall_rating >= min_rating)
        
        if max_rating is not None:
            query = query.filter(Player.overall_rating <= max_rating)
        
        # Paginate instead of loading all
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        players = pagination.items
        
        filter_info = {
            "performance": performance,
            "min_rating": min_rating,
            "max_rating": max_rating,
            "total_pages": pagination.pages,
            "current_page": page
        }
        
        return render_template("players.html", players=players, search_query=None, filter_info=filter_info)
    except SQLAlchemyError as e:
        print(f"❌ Database error in players: {e}")
        flash("Error loading players", "danger")
        return render_template("players.html", players=[], search_query=None, filter_info={})

# Search Players with Limit
@app.route("/players/search", methods=["POST", "GET"])
def search_players():
    if "user" not in session:
        return redirect(url_for("login"))
    
    try:
        # Handle both POST and GET requests
        if request.method == "POST":
            name = request.form.get("name", "").strip()
        else:
            name = request.args.get("name", "").strip()
        
        if name:
            # Limit search results to prevent blocking
            players = Player.query.filter(
                Player.name.ilike(f"%{name}%")
            ).limit(50).all()
            search_query = name
        else:
            players = []
            search_query = None

        if name:
            log_activity(session.get("user", "Unknown"), f"Searched player: {name}")
        
        filter_info = {
            "performance": "all",
            "min_rating": None,
            "max_rating": None,
            "total_pages": 1,
            "current_page": 1
        }
        
        return render_template("players.html", players=players, search_query=search_query, filter_info=filter_info)
    except SQLAlchemyError as e:
        print(f"❌ Database error in search: {e}")
        flash("Error searching players", "danger")
        return render_template("players.html", players=[], search_query=None, filter_info={"total_pages": 1, "current_page": 1})

# Starting 11 Prediction Route
@app.route("/starting-11")
def starting_eleven():
    """Predict best starting 11 based on position and rating - 4-3-3 formation"""
    try:
        # Get top players only instead of all players
        players = Player.query.filter(
            Player.overall_rating > 0
        ).order_by(
            Player.overall_rating.desc()
        ).limit(500).all()
        
        # Categorize by position
        position_map = {
            'GK': [],
            'DEF': [],
            'MID': [],
            'FWD': []
        }
        
        for player in players:
            if not player.positions:
                continue
            
            positions = [p.strip() for p in player.positions.split(',')]
            
            for pos in positions:
                if 'GK' in pos:
                    if player not in position_map['GK']:
                        position_map['GK'].append(player)
                elif 'DEF' in pos or 'CB' in pos or 'LB' in pos or 'RB' in pos:
                    if player not in position_map['DEF']:
                        position_map['DEF'].append(player)
                elif 'MID' in pos or 'CM' in pos or 'CAM' in pos or 'CDM' in pos:
                    if player not in position_map['MID']:
                        position_map['MID'].append(player)
                elif 'FWD' in pos or 'ST' in pos or 'CF' in pos or 'LW' in pos or 'RW' in pos:
                    if player not in position_map['FWD']:
                        position_map['FWD'].append(player)
        
        # Select best players from each position (4-3-3 formation)
        starting_11 = []
        selected_ids = set()
        
        formation = {
            'GK': 1,
            'DEF': 4,
            'MID': 3,
            'FWD': 3
        }
        
        for position, count in formation.items():
            available = [p for p in position_map[position] if p.id not in selected_ids]
            selected = available[:count]
            starting_11.extend(selected)
            selected_ids.update([p.id for p in selected])
        
        log_activity(session.get("user", "Unknown"), "Generated Starting 11 Prediction")
        
        return render_template("starting_11.html", players=starting_11)
    except SQLAlchemyError as e:
        print(f"❌ Database error in starting_eleven: {e}")
        flash("Error generating team", "danger")
        return render_template("starting_11.html", players=[])

# Add Player with Dynamic Clustering
@app.route("/players/add", methods=["POST"])
def add_player():
    try:
        # Get player data from form
        name = request.form["name"]
        age = int(request.form["age"])
        positions = request.form["positions"]
        overall_rating = float(request.form["overall_rating"])
        
        # Predict cluster and performance based on overall rating
        prediction = predict_cluster_and_performance(overall_rating)
        cluster = prediction['cluster']
        performance_label = prediction['performance_label']
        
        # Create new player with predicted cluster and performance
        player = Player(
            name=name,
            age=age,
            positions=positions,
            overall_rating=overall_rating,
            cluster=cluster,
            performance_label=performance_label
        )

        db.session.add(player)
        db.session.commit()

        log_activity(session.get("user", "Unknown"), f"Added player {player.name} with rating {overall_rating} ({performance_label})")
        flash(f"Player {player.name} added successfully as {performance_label}", "success")
        return redirect(url_for("players"))
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"❌ Error adding player: {e}")
        flash("Error adding player", "danger")
        return redirect(url_for("players"))
    except (KeyError, ValueError) as e:
        print(f"❌ Invalid form data: {e}")
        flash("Invalid form data", "danger")
        return redirect(url_for("players"))

# Delete Player
@app.route("/players/delete/<int:player_id>")
def delete_player(player_id):
    try:
        player = Player.query.get(player_id)
        if player:
            player_name = player.name
            db.session.delete(player)
            db.session.commit()
            log_activity(session.get("user", "Unknown"), f"Deleted player {player_name}")
            flash(f"Player {player_name} deleted successfully", "success")
        else:
            flash("Player not found", "warning")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"❌ Error deleting player: {e}")
        flash("Error deleting player", "danger")

    return redirect(url_for("players"))

# Reload Dataset (Non-blocking)
@app.route("/players/reload")
def reload_players():
    try:
        Player.query.delete()
        db.session.commit()
        load_players_from_csv()
        log_activity(session.get("user", "Unknown"), "Reloaded player dataset")
        flash("Dataset reloaded successfully", "success")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error reloading dataset: {e}")
        flash("Error reloading dataset", "danger")
    
    return redirect(url_for("players"))

# Activity Log (MongoDB) with Pagination
@app.route("/activity_log")
def activity_log():
    try:
        page = request.args.get("page", 1, type=int)
        per_page = 25
        skip = (page - 1) * per_page
        
        # Get total count
        total_logs = mongo_logs.count_documents({})
        total_pages = (total_logs + per_page - 1) // per_page
        
        # Get paginated logs
        activity_logs = list(
            mongo_logs.find().sort("timestamp", -1).skip(skip).limit(per_page)
        )
        
        return render_template(
            "activity_log.html", 
            logs=activity_logs,
            current_page=page,
            total_pages=total_pages
        )
    except Exception as e:
        print(f"❌ Error loading activity logs: {e}")
        flash("Error loading activity logs", "danger")
        return render_template("activity_log.html", logs=[], current_page=1, total_pages=0)

# -------------------- INIT DB --------------------
with app.app_context():
    db.create_all()
    if Player.query.count() == 0:
        load_players_from_csv()

# -------------------- RUN --------------------
if __name__ == "__main__":
    app.run(debug=True)
