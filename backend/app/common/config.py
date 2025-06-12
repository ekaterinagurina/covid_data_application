import redis
import logging
from common.settings import redis_settings

redis_client = redis.StrictRedis(
    host=redis_settings.REDIS_HOST,
    port=redis_settings.REDIS_PORT,
    db=0,
    decode_responses=False
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)