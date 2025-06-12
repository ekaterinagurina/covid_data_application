import asyncio
import json

from nats.aio.client import Client as NATS
from psycopg2 import DatabaseError

from database.db_connect import query_db
from common.config import logger
from common.errors import ErrorCode
from common.settings import settings


async def run():
    nc = NATS()
    try:
        await nc.connect(settings.NATS_URL)
        logger.info(f"Connected to NATS at {settings.NATS_URL}")
    except Exception as e:
        logger.error(f"Unable to connect to NATS: {e}")
        return

    async def handle_cfr(msg):
        try:
            payload = msg.data.decode()
            req = json.loads(payload)
            country = req.get("country")
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            logger.error(f"Invalid payload: {e}")
            err = ErrorCode.INVALID_INPUT
            await msg.respond(
                json.dumps({
                    "error_code": err.code,
                    "error_message": err.message
                }).encode()
            )
            return

        def sum_for(record_type: str) -> int:
            sql = (
                "SELECT SUM(cases) AS total "
                "FROM public.coronavirus_daily "
                "WHERE type ILIKE %s"
            )
            params = [record_type]
            if country:
                sql += " AND country ILIKE %s"
                params.append(country)
            sql += ";"
            rows = query_db(sql, tuple(params))
            return rows[0]["total"] or 0

        try:
            total_cases = sum_for("confirmed")
            total_deaths = sum_for("death")
        except DatabaseError as e:
            logger.error(f"Database error: {e}")
            err = ErrorCode.DATABASE_ERROR
            await msg.respond(
                json.dumps({
                    "error_code": err.code,
                    "error_message": err.message
                }).encode()
            )
            return

        cfr = (total_deaths / total_cases * 100) if total_cases else None

        reply = {
            "country": country,
            "total_cases": total_cases,
            "total_deaths": total_deaths,
            "cfr": cfr,
        }

        try:
            await msg.respond(json.dumps(reply).encode())
            logger.info(f"Replied to request: {reply}")
        except Exception as e:
            logger.error(f"Failed to respond: {e}")

        try:
            await nc.publish("stats.events.cfr", json.dumps(reply).encode())
            logger.info("Broadcasted stats.events.cfr")
        except Exception as e:
            logger.error(f"Broadcast failed: {e}")

    await nc.subscribe("stats.calculate.cfr", cb=handle_cfr)
    logger.info("Subscribed to subject stats.calculate.cfr")

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(run())
