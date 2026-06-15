import os
from pathlib import Path
from sqlalchemy import create_engine
try:
    from sqlalchemy.orm import declarative_base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    # Search for .env in the backend directory
    env_file = Path(__file__).resolve().parent.parent.parent / ".env"
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
    else:
        load_dotenv()
except ImportError:
    # Fallback to manual parsing if python-dotenv is not installed
    env_file = Path(__file__).resolve().parent.parent.parent / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip().strip("'\"")

# Read database credentials with default fallback values
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
# Default DB_NAME should match the actual MySQL database used in production
DB_NAME = os.getenv("DB_NAME", "memorycart_ai")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Construct the SQLAlchemy database URL using mysql+pymysql
# Build the SQLAlchemy database URL. Keep credentials in env for flexibility.
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine with production-ready connection pooling configurations
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # Verify connection health before issuing queries to prevent stale connections
    pool_recycle=3600,       # Recycle connections older than 1 hour to prevent MySQL disconnect errors
    pool_size=10,            # Maintain a pool of up to 10 persistent connections
    max_overflow=20          # Allow up to 20 temporary connections overflow
)

# Create the SessionLocal session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the Base model class for SQLAlchemy models
Base = declarative_base()

# Dependency function to get database session context
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
