import os
from urllib.parse import quote_plus


class Config:
    # 🔐 Flask secret key
    SECRET_KEY = "0c2d64de11653406c70ce2c6bcf4a9ab870c68cdba3b332b448e5e440f9e300c"

    # ======================
    # 🐬 MySQL Configuration
    # ======================
    MYSQL_USER = "username"
    MYSQL_PASSWORD = quote_plus("your password")
    MYSQL_HOST = "localhost"
    MYSQL_PORT = 3306
    MYSQL_DB = "label_dbms"

    SQLALCHEMY_DATABASE_URI = (
      your url;
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
        your url;
    )

    
    MONGO_DB = "label_dbms_logs"
