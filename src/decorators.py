from exceptions import TooManyTries


def retry(times):

    def func_wrapper(func):

        async def wrapper(*args, **kwargs):

            for _ in range(times):
                try:
                    values = await func(*args, **kwargs)
                except Exception as e:
                    pass

                try:
                    # return value iterable?
                    if any([val is None for val in values]):
                        pass
                except TypeError:
                    # return value not iterable
                    if values is None:
                        pass

                return values

            raise TooManyTries(f"Function {func} executed {times} times, never worked.")

        return wrapper

    return func_wrapper
