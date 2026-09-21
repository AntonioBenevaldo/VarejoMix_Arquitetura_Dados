from pathlib import Path
import os
from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env', override=False)
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg://varejomix:varejomix@127.0.0.1:5434/varejomix')
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://127.0.0.1:27018')
CUTOFF_DATE = os.getenv('MODEL_CUTOFF_DATE', '2025-10-01')
def connection():
    import psycopg
    conn = psycopg.connect(DATABASE_URL.replace('postgresql+psycopg://', 'postgresql://'), autocommit=True, options='-c timezone=UTC')
    conn.execute("SET TIME ZONE 'UTC'")
    return conn
