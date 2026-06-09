import os
import re
from mysql.connector.pooling import MySQLConnectionPool
from dotenv import load_dotenv

load_dotenv()

_pool = None


def get_pool():
    global _pool
    if _pool is not None:
        return _pool
    db_url = os.getenv('DATABASE_URL')
    config = {'charset': 'utf8mb4', 'use_pure': True}
    if db_url:
        match = re.match(r'mysql://([^:]+):([^@]+)@([^:]+):(\d+)/([^?]+)', db_url)
        if match:
            config.update(host=match.group(3), user=match.group(1),
                          password=match.group(2), port=int(match.group(4)),
                          database=match.group(5))
        else:
            config.update(host=os.getenv('DB_HOST', 'localhost'),
                          user=os.getenv('DB_USER', 'root'),
                          password=os.getenv('DB_PASSWORD', 'senai123'),
                          database=os.getenv('DB_NAME', 'aqualog'))
    else:
        config.update(host=os.getenv('DB_HOST', 'localhost'),
                      user=os.getenv('DB_USER', 'root'),
                      password=os.getenv('DB_PASSWORD', 'senai123'),
                      database=os.getenv('DB_NAME', 'aqualog'))
    _pool = MySQLConnectionPool(pool_name='aqualog', pool_size=10, **config)
    return _pool


def get_connection():
    pool = get_pool()
    return pool.get_connection()
