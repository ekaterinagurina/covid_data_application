import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from fastapi import HTTPException, status
from config import settings, logger
from models import Base
from database import load_data

DATABASE_URI = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_connection():
    try:
        return psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            cursor_factory=RealDictCursor
        )
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not connect to the database."
        )


def query_db(query: str, params: tuple = None):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
    except Exception as e:
        logger.error(f"Database query error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database query error."
        )


def setup_database():
    try:
        Base.metadata.create_all(bind=engine)

        with SessionLocal() as session:
            load_data(session)

        logger.info("Database setup and data loading completed successfully.")
    except Exception as e:
        logger.error(f"Error during database setup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database setup error."
        )
