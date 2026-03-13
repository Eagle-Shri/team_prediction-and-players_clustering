# LABEL_DBMS - Football Player Performance Label Management System

A Flask-based web application for managing FIFA player data with machine learning clustering and performance labeling capabilities. The system integrates MySQL for persistent storage, MongoDB for activity logging, and K-means clustering for player classification.

## 📋 Project Overview

LABEL_DBMS is a database management system designed to:
- Load and manage FIFA player datasets with clustering-based performance labels
- Provide user authentication and role-based access (Coach accounts)
- Visualize player statistics and classifications
- Track system activity through MongoDB logging
- Support team composition (Starting 11 selection)
- Generate performance-based player recommendations

## 🏗️ Project Structure

```
LABEL_DBMS/
├── app.py                           # Main Flask application & routes
├── config.py                        # Configuration (MySQL, MongoDB, secrets)
├── requirements.txt                 # Python dependencies
├── load_sample_players.py           # CSV data loader script
│
├── data/
│   └── fifa_players_clustered_output.csv    # FIFA player dataset with cluster labels
│
├── ml/
│   ├── kmeans_model.joblib          # Pre-trained K-means clustering model
│   └── scaler.joblib                # Feature scaler for normalization
│
├── models/
│   ├── __init__.py
│   └── mysql_models.py              # SQLAlchemy ORM models (Coach, Player)
│
├── mongo/
│   ├── __init__.py
│   └── mongo_logs.py                # MongoDB activity logging
│
├── static/
│   └── style.css                    # Application styling
│
└── templates/
    ├── index.html                   # Home/welcome page
    ├── login.html                   # Coach login
    ├── register.html                # Coach registration
    ├── dashboard.html               # Main dashboard with analytics
    ├── players.html                 # Player list & search
    ├── activity_log.html            # Activity history
    └── starting_11.html             # Team composition builder
```

## 🔧 Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Flask 2.x |
| **Database (Relational)** | MySQL |
| **Database (NoSQL)** | MongoDB Atlas |
| **ORM** | SQLAlchemy |
| **Authentication** | Flask-Login, Werkzeug (password hashing) |
| **ML** | scikit-learn, joblib |
| **Data Processing** | pandas, numpy |
| **Frontend** | HTML5, CSS3, Jinja2 templates |

## 📦 Dependencies

- `flask` - Web framework
- `flask-login` - User session management
- `flask-cors` - Cross-origin requests
- `flask-sqlalchemy` - ORM integration
- `pymongo` / `flask-pymongo` - MongoDB integration
- `pandas` / `numpy` - Data analysis
- `scikit-learn` / `joblib` - Machine learning models
- `mysqlclient` - MySQL adapter
- `werkzeug` - Security utilities

## 🗄️ Database Models

### Coach (MySQL)
```python
- id (Primary Key)
- username (Unique)
- email (Unique)
- password (Hashed)
- created_at (Timestamp)
```
**Features:** Password hashing, account creation tracking

### Player (MySQL)
```python
- id (Primary Key)
- name
- age
- positions
- overall_rating
- cluster (K-means cluster assignment)
- performance_label (Top/Average/Low Performer)
```

### Activity Logs (MongoDB)
```json
{
  "_id": ObjectId,
  "user": "username",
  "action": "description",
  "timestamp": ISODate
}
```

## 🚀 Features Implemented

### ✅ User Management
- **Registration:** New coach account creation with email validation
- **Login:** Secure authentication with password hashing
- **Session Management:** Flask-Login session tracking
- **Activity Logging:** All user actions tracked in MongoDB

### ✅ Player Management
- **Data Loading:** CSV import from FIFA dataset with performance categorization
- **Clustering:** K-means model-based player classification into 3 clusters
- **Performance Labeling:** Automatic categorization as Top/Average/Low Performer
- **Player Database:** Full CRUD operations on player records

### ✅ Dashboard & Analytics
- Player statistics and overview
- Cluster distribution visualization
- Performance category breakdown
- Real-time activity monitoring

### ✅ Features
- **Player Search:** Find players by name, position, or performance level
- **Starting 11:** Build and manage football team compositions
- **Activity Log:** View complete history of system actions
- **Data Persistence:** Dual database strategy (relational + NoSQL)

## 📊 Machine Learning Pipeline

The system uses a pre-trained K-means clustering model to classify players:

1. **Feature Scaling:** Standardization using `scaler.joblib`
2. **Clustering:** K-means algorithm (pre-fitted) with player attributes
3. **Labeling:** Cluster-to-performance mapping:
   - High cluster scores → Top Performer
   - Medium cluster scores → Average Performer
   - Low cluster scores → Low Performer

## 🔐 Security Features

- Password hashing using Werkzeug security
- Session-based authentication
- Database connection with credentials in config
- Activity audit trail via MongoDB
- Flask secret key configuration

## 🛠️ Key Implementation Details

### Data Loading Flow
1. CSV file parsed from `data/fifa_players_clustered_output.csv`
2. Data categorized by performance labels
3. Players inserted into MySQL database
4. Activity logged to MongoDB

### Authentication Flow
1. User registers with username/email/password
2. Password hashed and stored in MySQL
3. Login validates credentials against database
4. Session created upon successful auth
5. Activity logged to MongoDB
6. User redirected to dashboard

### Clustering Integration
- Pre-trained models loaded from `ml/` directory
- Player features normalized using stored scaler
- Cluster assignments used for performance prediction

## 📝 API Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Home page |
| `/login` | GET, POST | Coach login |
| `/register` | GET, POST | Coach registration |
| `/dashboard` | GET | Main dashboard |
| `/players` | GET | Player list/search |
| `/activity_log` | GET | Activity history |
| `/starting_11` | GET, POST | Team builder |

## 💾 Configuration

Edit `config.py` to modify:

```python
# MySQL Connection
MYSQL_USER = "root"
MYSQL_PASSWORD = "your_password"
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DB = "label_dbms"

# MongoDB Connection
MONGO_URI = "mongodb+srv://user:pass@cluster.mongodb.net/"
MONGO_DB = "label_dbms_logs"

# Flask Secret
SECRET_KEY = "your_secret_key"
```

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Databases
- Create MySQL database: `label_dbms`
- MongoDB Atlas cluster configured (connection string in config.py)

### 3. Initialize Database
```bash
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
```

### 4. Load Sample Data
```bash
python load_sample_players.py
```

### 5. Run Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 📈 Performance Metrics

- **Data:** 18,278+ FIFA players (clustered)
- **Clusters:** 3 K-means clusters
- **Categories:** Top Performer, Average Performer, Low Performer
- **Database:** MySQL (relational) + MongoDB (logging)

## 🔄 Data Flow

```
CSV Data
   ↓
load_sample_players.py
   ↓
Performance Categorization
   ↓
MySQL Database (Player records)
   ↓
Flask Web Interface
   ↓
K-means Clustering Assignment
   ↓
Dashboard Visualization
   ↓
MongoDB Logs (Activity tracking)
```

## 📌 Key Files Summary

| File | Purpose |
|------|---------|
| `app.py` | Flask app, routes, authentication |
| `config.py` | Database credentials & configuration |
| `models/mysql_models.py` | Coach & Player ORM models |
| `mongo/mongo_logs.py` | MongoDB activity logging |
| `load_sample_players.py` | Data import pipeline |
| `data/fifa_players_clustered_output.csv` | Source dataset |
| `ml/*.joblib` | Pre-trained ML models |

## 🔍 Future Enhancements

- Advanced player statistics and metrics
- Real-time performance updates
- API endpoints for external integration
- Player comparison tools
- Batch operations and exports
- Advanced analytics dashboard
- Performance prediction models

## 📞 Support

For issues or questions regarding the LABEL_DBMS system, refer to the configuration files and template documentation.

---

**Project Status:** ✅ Active Development  
**Last Updated:** January 6, 2026  
**Version:** 1.0.0
=======
# team_prediction-and-players_clustering
Hybrid Database System for Predictive Sports Analysis that combines structured and unstructured data to perform team outcome prediction and player clustering using machine learning techniques.