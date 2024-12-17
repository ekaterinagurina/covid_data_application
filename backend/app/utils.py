import time
import logging
from functools import wraps
import numpy as np
import pandas as pd
from datetime import datetime, date

logger = logging.getLogger("performance")

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
    cleaned_data = []
    for row in data:
        cleaned_row = {
            k: None if isinstance(v, (float, int)) and (pd.isna(v) or np.isinf(v)) else v
            for k, v in row.items()
        }
        cleaned_data.append(cleaned_row)
    return cleaned_data


def custom_json_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")
