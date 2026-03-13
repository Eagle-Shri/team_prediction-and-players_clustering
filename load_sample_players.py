"""
Script to load ALL players from the FIFA dataset
"""

import csv
from app import app, db
from models.mysql_models import Player

def load_sample_players():
    """Load ALL players from the dataset"""
    
    categories = {
        "Top Performer": [],
        "Average Performer": [],
        "Low Performer": []
    }
    
    # Read CSV and categorize players
    print("Reading CSV file...")
    with open("data/fifa_players_clustered_output.csv", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            try:
                performance = row.get("performance_label", "Unlabeled").strip()
                
                if performance in categories:
                    categories[performance].append(row)
                    
            except Exception as e:
                print(f"Error reading row: {e}")
                continue
    
    # Log what we found
    print(f"\nFound players by category:")
    for category, players in categories.items():
        print(f"  {category}: {len(players)} players")
    
    # Clear existing players
    print("\nClearing existing players...")
    Player.query.delete()
    db.session.commit()
    
    # Load ALL players from each category
    print("\nLoading ALL players from dataset...\n")
    
    total_added = 0
    
    for category, players_list in categories.items():
        count = 0
        for row in players_list:  # Load ALL players
            try:
                player = Player(
                    name=row.get("name", "Unknown"),
                    age=int(float(row.get("age", 0))),
                    positions=row.get("positions", "Unknown"),
                    overall_rating=float(row.get("overall_rating", 0)),
                    cluster=int(float(row.get("cluster", 0))),
                    performance_label=category
                )
                
                db.session.add(player)
                count += 1
                
            except (ValueError, TypeError) as e:
                print(f"  Skipped player: {row.get('name')} - {e}")
                continue
        
        db.session.commit()
        print(f"Added {count} {category}s")
        total_added += count
    
    print(f"\nSuccessfully loaded {total_added} players!")
    print(f"   - Top Performers: {len(categories['Top Performer'])}")
    print(f"   - Average Performers: {len(categories['Average Performer'])}")
    print(f"   - Low Performers: {len(categories['Low Performer'])}")

if __name__ == "__main__":
    with app.app_context():
        load_sample_players()
