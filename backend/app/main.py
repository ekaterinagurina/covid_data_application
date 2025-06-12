import io
import json

from typing import Optional

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from nats.aio.client import Client as NATS
from nats.errors import TimeoutError, NoRespondersError


from auth import auth_router
from common.cache import cache_get, cache_set, get_cache_key
from common.config import logger
from database.db_connect import setup_database, query_db
from common.errors import ErrorCode
from common.settings import settings
from common.utils import clean_data, CustomJSONEncoder

app = FastAPI()

@app.on_event("startup")
async def startup_nats():
    nc = NATS()
    try:
        await nc.connect(settings.NATS_URL)
        app.state.nats = nc
        logger.info(f"Connected to NATS at {settings.NATS_URL}")
    except Exception as e:
        logger.error(f"Unable to connect to NATS: {e}")
        raise

    async def on_stats_event(msg):
        try:
            payload = json.loads(msg.data.decode())
        except Exception as e:
            logger.error(f"Invalid stats event payload: {e}")
            return
        logger.info(f"Received broadcast on {msg.subject}: {payload}")

    await nc.subscribe("stats.events.*", cb=on_stats_event)
    logger.info("Subscribed to stats.events.*")


@app.on_event("shutdown")
async def shutdown_nats():
    nc: NATS = app.state.nats
    try:
        await nc.drain()
        logger.info("NATS connection drained")
    except Exception as e:
        logger.error(f"Error shutting down NATS: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

setup_database()

app.include_router(auth_router)

ALLOWED_TABLES = [
    "coronavirus_2020", "coronavirus_2021", "coronavirus_2022", "coronavirus_2023",
    "coronavirus_daily", "covid19_vaccine", "world_population"
]

PLOT_COLUMNS = "cases"


def build_query(table_name: str, column_name: Optional[str] = None, country: Optional[str] = None):
    is_corona_table = table_name.startswith("coronavirus_")

    if column_name:
        if is_corona_table:
            query = f"SELECT date, SUM({column_name}) as {column_name} FROM public.{table_name} "
        else:
            query = f"SELECT date, {column_name} FROM public.{table_name} "
    else:
        query = f"SELECT * FROM public.{table_name} "

    if country:
        if is_corona_table:
            query += "WHERE country ILIKE %s "
            params = (country,)
        elif table_name == "covid19_vaccine":
            query += "WHERE country_region ILIKE %s "
            params = (country,)
        elif table_name == "world_population":
            query += "WHERE country_name ILIKE %s "
            params = (country,)
        else:
            params = None
    else:
        params = None

    if column_name:
        if is_corona_table:
            query += "GROUP BY date ORDER BY date "
        else:
            query += "ORDER BY date "
        query += "LIMIT 100;"
    else:
        query += "LIMIT 100;"

    return query, params


def fetch_and_cache_data(cache_key: str, query: str, params: Optional[tuple]):
    cached_data = cache_get(cache_key)
    if cached_data:
        logger.info(f"Cache hit for {cache_key}")
        return json.loads(cached_data.decode("utf-8"))

    logger.info(f"Cache miss for {cache_key}")
    data = query_db(query, params)
    if not data:
        ErrorCode.NOT_FOUND.raise_exception()

    cleaned_data = clean_data(data)
    cache_set(cache_key, json.dumps(cleaned_data, cls=CustomJSONEncoder))
    return cleaned_data


def generate_plot(dates, values, column_name):
    parsed_dates = []
    for d in dates:
        try:
            parsed_dates.append(pd.to_datetime(d))
        except Exception:
            continue

    if not parsed_dates:
        raise ValueError("No valid date values for plotting")

    plt.figure(figsize=(12, 6))
    plt.plot(parsed_dates, values[:len(parsed_dates)], marker='o', linestyle='-', linewidth=2)

    plt.xlabel("Date")
    plt.ylabel(column_name.replace("_", " ").title())
    plt.title(f"{column_name.replace('_', ' ').title()} Over Time")
    plt.xticks(rotation=45)
    plt.tight_layout()

    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    return buf.getvalue()


@app.get("/data/{table_name}")
def read_table_data(table_name: str, country: Optional[str] = Query(None, description="Filter by country")):
    if table_name not in ALLOWED_TABLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid table name")

    cache_key = get_cache_key(table_name, country or "all")
    query, params = build_query(table_name, country=country)
    return JSONResponse(content=fetch_and_cache_data(cache_key, query, params))


@app.get("/plot/{table_name}/{column_name}")
def plot_data(table_name: str, column_name: str, country: Optional[str] = Query(None, description="Filter by country")):
    if table_name not in ALLOWED_TABLES or column_name not in PLOT_COLUMNS:
        ErrorCode.INVALID_INPUT.raise_exception()

    cache_key = get_cache_key(table_name, column_name, country or "all", "plot")
    cached_plot = cache_get(cache_key)
    if cached_plot:
        logger.info(f"Cache hit for plot: {cache_key}")
        return Response(content=cached_plot, media_type="image/png")

    logger.info(f"Cache miss for plot: {cache_key}")
    query, params = build_query(table_name, column_name, country)
    data = fetch_and_cache_data(cache_key, query, params)

    dates = [row["date"] for row in data if row.get("date") and row.get(column_name) is not None]
    values = [row[column_name] for row in data if row.get("date") and row.get(column_name) is not None]

    plot_image = generate_plot(dates, values, column_name)
    cache_set(cache_key, plot_image)
    return Response(content=plot_image, media_type="image/png")

@app.get("/stats/cfr")
async def get_cfr(country: Optional[str] = Query(None, description="Country name")):
    nc: NATS = app.state.nats
    payload = {"country": country}

    try:
        msg = await nc.request(
            "stats.calculate.cfr",
            json.dumps(payload).encode(),
            timeout=5
        )
    except TimeoutError:
        logger.error(f"CFR request timed out for country={country}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Statistics service timeout"
        )
    except NoRespondersError:
        logger.error("No stats service responders available")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Statistics service unavailable"
        )
    except Exception as e:
        logger.error(f"Unexpected NATS error on CFR request: {e}")
        ErrorCode.SERVER_ERROR.raise_exception()

    try:
        data = json.loads(msg.data.decode())
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        logger.error(f"Failed to decode CFR response: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid response from statistics service"
        )

    if isinstance(data, dict) and data.get("error_code"):
        code = data["error_code"]
        message = data.get("error_message", "")
        logger.error(f"Stats service error: {code} – {message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": code, "error_message": message}
        )

    return data