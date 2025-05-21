import asyncio
import json

from nats.aio.client import Client as NATS

from db_connect import query_db
from settings import settings

NATS_URL = settings.NATS_URL

async def handle_cfr(msg):

    req = json.loads(msg.data.decode())
    country = req.get("country")

    def sum_for(record_type: str) -> int:
        sql = "SELECT SUM(cases) AS total FROM public.coronavirus_daily WHERE type ILIKE %s"
        params = [record_type]
        if country:
            sql += " AND country ILIKE %s"
            params.append(country)
        sql += ";"
        res = query_db(sql, tuple(params))
        return res[0]["total"] or 0

    try:
        total_cases  = sum_for("confirmed")
        total_deaths = sum_for("death")
        cfr = (total_deaths / total_cases * 100) if total_cases else None
    except Exception:
        total_cases = total_deaths = cfr = None

    reply = {
        "country": country,
        "total_cases": total_cases,
        "total_deaths": total_deaths,
        "cfr": cfr,
    }
    await msg.respond(json.dumps(reply).encode())

async def run():
    nc = NATS()
    await nc.connect(NATS_URL)
    await nc.subscribe("stats.calculate.cfr", cb=handle_cfr)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(run())
