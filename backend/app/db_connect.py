import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config import logger
from errors import ErrorCode
from settings import database_settings
from models import Base
from database import load_data


DATABASE_URI = (
    f"postgresql://{database_settings.DB_USER}:"
    f"{database_settings.DB_PASSWORD}@"
    f"{database_settings.DB_HOST}:"
    f"{database_settings.DB_PORT}/"
    f"{database_settings.DB_NAME}"
)
engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_connection():
    try:
        return psycopg2.connect(
            host=database_settings.DB_HOST,
            port=database_settings.DB_PORT,
            database=database_settings.DB_NAME,
            user=database_settings.DB_USER,
            password=database_settings.DB_PASSWORD,
            cursor_factory=RealDictCursor
        )
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        ErrorCode.DATABASE_ERROR.raise_exception()


def query_db(query: str, params: tuple = None):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
    except Exception as e:
        logger.error(f"Database query error: {e}")
        ErrorCode.DATABASE_ERROR.raise_exception()


def setup_database():
    try:
        Base.metadata.create_all(bind=engine)

        with SessionLocal() as session:
            load_data(session)

        logger.info("Database setup and data loading completed successfully.")
    except Exception as e:
        logger.error(f"Error during database setup: {e}")
        ErrorCode.DATABASE_ERROR.raise_exception()
