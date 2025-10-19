from exceptions import TooManyTries


def retry(times):

    def func_wrapper(func):

        async def wrapper(*args, **kwargs):

            for _ in range(times):
                try:
                    values = await func(*args, **kwargs)
                except Exception as e:
                    pass

                if any([val is None for val in values]):
                    pass

                return values

            raise TooManyTries(f"Function {func} executed {times} times, never worked.")

        return wrapper

    return func_wrapper
