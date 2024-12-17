import redis
import logging
from settings import Settings

settings = Settings()

redis_client = redis.StrictRedis(
    host="redis",
    port=6379,
    db=0,
    decode_responses=False
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("main")
