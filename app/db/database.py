
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration with environment variable fallbacks
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "project_dashboard")

DATABASE_URL = os.getenv(
	"DATABASE_URL",
	f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)

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


if __name__ == "__main__":
	# simple test connection
	try:
		conn = engine.connect()
		print("Connected to database")
		conn.close()
	except Exception as e:
		print("Failed to connect to database:", e)
