from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date, datetime
import simplejson as json
import io
import matplotlib.pyplot as plt
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
DB_NAME = os.getenv('DB_NAME', 'covid_database')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor
    )


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

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                if country:
                    query = f"SELECT * FROM public.{table_name} WHERE country_region ILIKE %s LIMIT 100;"
                    cursor.execute(query, (country,))
                else:
                    query = f"SELECT * FROM public.{table_name} LIMIT 100;"
                    cursor.execute(query)

                data = cursor.fetchall()
                if not data:
                    return {"message": "No data available"}

                return json.loads(json.dumps(data, default=custom_json_serializer, ignore_nan=True))

    except psycopg2.errors.UndefinedColumn:
        return {"message": "No data available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/plot/{table_name}/{column_name}")
def plot_data(table_name: str, column_name: str, country: str = Query(None, description="Filter by country")):
    plot_columns = ["confirmed", "deaths", "recovered", "active"]

    if column_name not in plot_columns:
        raise HTTPException(status_code=400, detail="Invalid column name for plotting")

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM public.{table_name} LIMIT 0;")
                columns = [desc[0] for desc in cursor.description]

                if "date" not in columns or column_name not in columns:
                    return {"message": "Required columns for plotting not found"}

                if country:
                    query = f"SELECT date, {column_name} FROM public.{table_name} WHERE country_region ILIKE %s ORDER BY date LIMIT 100;"
                    cursor.execute(query, (country,))
                else:
                    query = f"SELECT date, {column_name} FROM public.{table_name} ORDER BY date LIMIT 100;"
                    cursor.execute(query)

                data = cursor.fetchall()
                if not data:
                    return {"message": "No data available"}

                dates = [row["date"] for row in data]
                values = [row[column_name] for row in data]

                plt.figure(figsize=(10, 6))
                plt.bar(dates, values)
                plt.xlabel("Date")
                plt.ylabel(column_name.capitalize())
                plt.title(f"{column_name.capitalize()} over Time")
                plt.xticks(rotation=45)
                plt.tight_layout()

                buf = io.BytesIO()
                plt.savefig(buf, format="png")
                buf.seek(0)
                plt.close()

                return Response(content=buf.getvalue(), media_type="image/png")

    except psycopg2.errors.UndefinedColumn:
        return {"message": "No data available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))