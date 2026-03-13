import os
from urllib.parse import quote_plus


class Config:
    # 🔐 Flask secret key
    SECRET_KEY = "0c2d64de11653406c70ce2c6bcf4a9ab870c68cdba3b332b448e5e440f9e300c"

    # ======================
    # 🐬 MySQL Configuration
    # ======================
    MYSQL_USER = "root"
    MYSQL_PASSWORD = quote_plus("Shrikant@7676")
    MYSQL_HOST = "localhost"
    MYSQL_PORT = 3306
    MYSQL_DB = "label_dbms"

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqldb://{MYSQL_USER}:{MYSQL_PASSWORD}@"
        f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ⚙️ Connection Pool Optimization
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_RECYCLE = 3600
    SQLALCHEMY_POOL_PRE_PING = True
    SQLALCHEMY_ECHO = False

    # ======================
    #  MongoDB Atlas Configuration
    # ======================
    MONGO_URI = (
        "mongodb+srv://shrikanth123:shrikanth123@cluster0.wsoiviz.mongodb.net/"
        "?retryWrites=true&w=majority&appName=Cluster0"
    )

    
    MONGO_DB = "label_dbms_logs"
