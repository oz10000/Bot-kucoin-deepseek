import asyncio
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def async_retry(max_retries=3, base_delay=1, backoff=2, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Max retries reached for {func.__name__}: {e}")
                        raise
                    logger.warning(f"Retry {attempt+1}/{max_retries} for {func.__name__} due to {e}. Waiting {delay}s")
                    await asyncio.sleep(delay)
                    delay *= backoff
            return None
        return wrapper
    return decorator
