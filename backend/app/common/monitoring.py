from prometheus_client import Counter, Summary
import functools
import asyncio

FUNCTION_CALLS = Counter(
    'function_calls_total', 'Total number of function calls',
    ['module', 'function']
)

FUNCTION_DURATION = Summary(
    'function_duration_seconds', 'Function execution time in seconds',
    ['module', 'function']
)

def monitor(func):
    module = func.__module__
    name = func.__name__

    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            FUNCTION_CALLS.labels(module=module, function=name).inc()
            with FUNCTION_DURATION.labels(module=module, function=name).time():
                return await func(*args, **kwargs)
        return async_wrapper

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        FUNCTION_CALLS.labels(module=module, function=name).inc()
        with FUNCTION_DURATION.labels(module=module, function=name).time():
            return func(*args, **kwargs)
    return sync_wrapper
