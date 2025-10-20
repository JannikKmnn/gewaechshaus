import asyncio

from exceptions import TooManyTries
from typing import Callable
from functools import wraps


def retry(times, logger=None):

    def func_wrapper(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):

            for iteration in range(times):
                if iteration > 0 and logger:
                    logger.info(f"Retried function {func} {iteration} times.")
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if iteration < times:
                        await asyncio.sleep(0.1)
                    else:
                        if logger:
                            logger.warning(f"Measuring via {func} failed due to: {e}")
                        return None

        return wrapper

    return func_wrapper
