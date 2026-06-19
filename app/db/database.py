
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Helper to treat unset, empty, or literal 'None' values as missing
def _env_or_default(name: str, default: str) -> str:
    value = os.getenv(name)
    return default if value is None or value.strip() == "" or value.strip().lower() == "none" else value

# Helper to validate a provided DATABASE_URL before accepting it

def _valid_database_url(url: str) -> bool:
    if url is None:
        return False
    placeholder = url.strip().lower()
    if placeholder == "" or placeholder == "none":
        return False
    if "none" in url:
        return False
    from sqlalchemy.engine.url import make_url

    try:
        make_url(url)
        return True
    except Exception:
        return False

# Configuration with environment variables and safe defaults
DB_USER = _env_or_default("DB_USER", "postgres")
DB_PASSWORD = _env_or_default("DB_PASSWORD", "postgres")
DB_HOST = _env_or_default("DB_HOST", "localhost")
DB_PORT = _env_or_default("DB_PORT", "5432")
DB_NAME = _env_or_default("DB_NAME", "project_db")

DATABASE_URL = os.getenv("DATABASE_URL")
if not _valid_database_url(DATABASE_URL):
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
	"""Yield a database session, to be used with dependency injection."""
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()
