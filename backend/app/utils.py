import time
from functools import wraps
from numpy import isinf
from pandas import isna
import json
from datetime import datetime, date
from config import logger


def track_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        logger.info(f"Function '{func.__name__}' executed in {execution_time:.6f} seconds")
        return result

    return wrapper


def clean_data(data):
    return [
        {
            k: (
                serialize_date(v) if isinstance(v, (datetime, date)) else
                None if isinstance(v, (float, int)) and (isna(v) or isinf(v)) else v
            )
            for k, v in row.items()
        }
        for row in data
    ]

def serialize_date(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        serialized_obj = serialize_date(obj)
        if serialized_obj is not obj:
            return serialized_obj
        return super().default(obj)