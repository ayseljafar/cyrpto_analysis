import os
from dotenv import load_dotenv


load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'crypto_prices'),
    'user': os.getenv('DB_USER', 'crypto_user'),
    'password': os.getenv('DB_PASSWORD', '')
}

# SQLAlchemy connection string
def get_connection_string():
    return f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}" 