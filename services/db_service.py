import os
from contextlib import contextmanager

import psycopg2
from psycopg2 import sql
from psycopg2.pool import ThreadedConnectionPool
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "songlytics")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

_pool = None

def validate_config():
    if not DB_PASSWORD:
        raise RuntimeError(
            "DB_PASSWORD is missing. Please check your .env file."
        )

def create_database_if_not_exists():
    validate_config()

    connection = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname="postgres",
        user=DB_USER,
        password=DB_PASSWORD
    )

    connection.autocommit = True

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (DB_NAME,)
            )

            exists = cursor.fetchone()

            if not exists:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(DB_NAME)
                    )
                )

                print(f"Database created: {DB_NAME}")

    finally:
        connection.close()

def initialize_pool():
    global _pool

    if _pool is not None:
        return

    validate_config()

    _pool = ThreadedConnectionPool(
        minconn=1,
        maxconn=10,
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def get_connection():
    if _pool is None:
        initialize_pool()

    return _pool.getconn()

def release_connection(connection):
    if _pool is not None and connection is not None:
        _pool.putconn(connection)

@contextmanager
def db_cursor(commit=False):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            yield cursor

        if commit:
            connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        release_connection(connection)

def initialize_tables():
    queries = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMPTZ
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS prediction_history (
            id BIGSERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            display_name TEXT NOT NULL,
            label VARCHAR(30) NOT NULL,
            predicted_score NUMERIC(6, 2) NOT NULL,
            input_source VARCHAR(30),
            features JSONB,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT fk_prediction_user
                FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS simulation_history (
            id BIGSERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            display_name TEXT NOT NULL,
            original_score NUMERIC(6, 2) NOT NULL,
            new_score NUMERIC(6, 2) NOT NULL,
            changes JSONB,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT fk_simulation_user
                FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_prediction_user
        ON prediction_history(user_id)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_prediction_created
        ON prediction_history(created_at DESC)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_simulation_user
        ON simulation_history(user_id)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_simulation_created
        ON simulation_history(created_at DESC)
        """
    ]

    with db_cursor(commit=True) as cursor:
        for query in queries:
            cursor.execute(query)

def initialize_database():
    try:
        create_database_if_not_exists()
        initialize_pool()
        initialize_tables()

        print("PostgreSQL database initialized successfully.")

        return True

    except Exception as e:
        print(f"Database initialization failed: {e}")
        return False

def test_connection():
    try:
        with db_cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]

        print("PostgreSQL connection successful.")
        print(version)

        return True

    except Exception as e:
        print(f"PostgreSQL connection failed: {e}")
        return False

def close_pool():
    global _pool

    if _pool is not None:
        _pool.closeall()
        _pool = None