import io
import json
from typing import Optional
import matplotlib.pyplot as plt
from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from cache import cache_get, cache_set, get_cache_key
from config import logger, settings
from db_connect import setup_database, query_db
from errors import ErrorCode
from utils import clean_data, CustomJSONEncoder

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_database()

ALLOWED_TABLES = [
    "country_wise_latest", "covid_19_clean_complete", "day_wise",
    "full_grouped", "usa_county_wise", "worldometer_data"
]
PLOT_COLUMNS = ["confirmed", "deaths", "recovered", "active"]


@app.get("/data/{table_name}")
def read_table_data(table_name: str, country: Optional[str] = Query(None, description="Filter by country")):
    if table_name not in ALLOWED_TABLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid table name")

    cache_key = get_cache_key(table_name, country or "all")
    cached_data = cache_get(cache_key)
    if cached_data:
        logger.info(f"Cache hit for table: {table_name}, country: {country}")
        return JSONResponse(content=json.loads(cached_data.decode("utf-8")))

    logger.info(f"Cache miss for table: {table_name}, country: {country}")
    query = f"SELECT * FROM public.{table_name} WHERE country_region ILIKE %s LIMIT 100;" \
        if country else f"SELECT * FROM public.{table_name} LIMIT 100;"
    params = (country,) if country else None

    data = query_db(query, params)
    if not data:
        ErrorCode.NOT_FOUND.raise_exception()

    cleaned_data = clean_data(data)
    cache_set(cache_key, json.dumps(cleaned_data, cls=CustomJSONEncoder))
    return JSONResponse(content=cleaned_data)


@app.get("/plot/{table_name}/{column_name}")
def plot_data(table_name: str, column_name: str, country: Optional[str] = Query(None, description="Filter by country")):
    if table_name not in ALLOWED_TABLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid table name")

    if column_name not in PLOT_COLUMNS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid column name for plotting")

    cache_key = get_cache_key(table_name, column_name, country or "all", "plot")
    cached_plot = cache_get(cache_key)
    if cached_plot:
        logger.info(f"Cache hit for plot: {table_name}, column: {column_name}, country: {country}")
        return Response(content=cached_plot, media_type="image/png")

    logger.info(f"Cache miss for plot: {table_name}, column: {column_name}, country: {country}")
    query = f"SELECT date, {column_name} FROM public.{table_name} WHERE country_region ILIKE %s ORDER BY date LIMIT 100;" \
        if country else f"SELECT date, {column_name} FROM public.{table_name} ORDER BY date LIMIT 100;"
    params = (country,) if country else None

    data = query_db(query, params)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No data available for plotting")

    data = clean_data(data)

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

    cache_set(cache_key, buf.getvalue())
    return Response(content=buf.getvalue(), media_type="image/png")
