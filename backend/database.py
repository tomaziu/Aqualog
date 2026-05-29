import os
import re
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        match = re.match(r'mysql://([^:]+):([^@]+)@([^:]+):(\d+)/([^?]+)', db_url)
        if match:
            return mysql.connector.connect(
                host=match.group(3),
                user=match.group(1),
                password=match.group(2),
                port=int(match.group(4)),
                database=match.group(5),
                charset='utf8mb4',
                use_pure=True
            )
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'senai123'),
        database=os.getenv('DB_NAME', 'aqualog'),
        charset='utf8mb4'
    )
