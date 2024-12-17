from config import redis_client, logger


def get_cache_key(*args: str) -> str:
    from hashlib import sha256
    return sha256(":".join(args).encode()).hexdigest()


def cache_get(cache_key: str):
    try:
        return redis_client.get(cache_key)
    except Exception as e:
        logger.error(f"Error accessing Redis: {e}")
        return None


def cache_set(cache_key: str, data, ttl: int = 300):
    try:
        redis_client.setex(cache_key, ttl, data)
    except Exception as e:
        logger.error(f"Error writing to Redis: {e}")
