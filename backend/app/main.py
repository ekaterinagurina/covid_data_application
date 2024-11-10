from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import simplejson as json
from datetime import date, datetime
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'covid_db')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')


def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor
    )
    return conn


def custom_json_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


@app.get("/data/{table_name}")
def read_table_data(table_name: str, country: str = Query(None, description="Filter by country")):
    allowed_tables = [
        "country_wise_latest", "covid_19_clean_complete", "day_wise",
        "full_grouped", "usa_county_wise", "worldometer_data"
    ]
    if table_name not in allowed_tables:
        raise HTTPException(status_code=400, detail="Invalid table name")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if country:
            query = f"SELECT * FROM public.{table_name} WHERE country_region ILIKE %s LIMIT 100;"
            cursor.execute(query, (country,))
        else:
            query = f"SELECT * FROM public.{table_name} LIMIT 100;"
            cursor.execute(query)

        data = cursor.fetchall()

        if not data:
            return {"message": "No data available"}

        conn.close()
        return json.loads(json.dumps(data, default=custom_json_serializer, ignore_nan=True))

    except psycopg2.errors.UndefinedColumn:
        conn.close()
        return {"message": "No data available"}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))