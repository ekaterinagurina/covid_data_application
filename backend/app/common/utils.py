import time
from functools import wraps
from numpy import isinf
from pandas import isna
import json
from datetime import datetime, date
from common.config import logger


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

def serialize_value(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, (float, int)) and (isna(value) or isinf(value)):
        return None
    return value

def clean_data(data):
    return [
        {k: serialize_value(v) for k, v in row.items()}
        for row in data
    ]

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        serialized_obj = serialize_value(obj)
        if serialized_obj is not obj:
            return serialized_obj
        return super().default(obj)