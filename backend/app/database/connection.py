import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Fallbacks to support older DB_ variables as well
MYSQL_HOST = os.getenv("MYSQL_HOST") or os.getenv("DB_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT") or os.getenv("DB_PORT", "3306")
MYSQL_USER = os.getenv("MYSQL_USER") or os.getenv("DB_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD") or os.getenv("DB_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE") or os.getenv("DB_NAME", "memorycart_ai")

if not all([MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_DATABASE]):
    raise ValueError("Missing database configuration variables. Ensure MYSQL_HOST, MYSQL_PORT, MYSQL_USER, and MYSQL_DATABASE are set.")

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
