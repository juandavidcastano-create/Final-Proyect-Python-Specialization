"""Alembic environment configuration."""
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
from dotenv import load_dotenv, find_dotenv

# Ensure repository root is on Python path so `app` imports resolve
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables from the nearest .env file in the repo tree
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)

# Helper to treat unset, empty, or literal 'None' values as missing

def _env_or_default(name: str, default: str) -> str:
    value = os.getenv(name)
    return default if value is None or value.strip() == "" or value.strip().lower() == "none" else value

# this is the Alembic Config object, which provides
# the values of the alembic.ini file, and in addition
# values that can be supplied programmatically into the
# EnvironmentContext.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override the sqlalchemy.url with environment variables if available
# and treat literal 'None' values as missing.
db_user = _env_or_default("DB_USER", "postgres")
db_password = _env_or_default("DB_PASSWORD", "postgres")
db_host = _env_or_default("DB_HOST", "localhost")
db_port = _env_or_default("DB_PORT", "5432")
db_name = _env_or_default("DB_NAME", "project_db")

# Prefer an explicit DATABASE_URL when provided, otherwise build from DB_* values.
raw_database_url = os.getenv("DATABASE_URL")
if raw_database_url is not None and raw_database_url.strip().lower() != "none":
    database_url = raw_database_url
else:
    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

config.set_main_option("sqlalchemy.url", database_url)

# Get the target metadata for autogenerate support
from app.db.database import Base
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
