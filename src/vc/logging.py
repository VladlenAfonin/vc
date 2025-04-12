import timeit
import typing


def function_begin(function_name: str) -> str:
    return f"begin function {function_name}()"


def _execution_result(result: typing.Any | None) -> str:
    return "" if result is None else f". execution result = {result}"


def _elapsed(elapsed: float | None) -> str:
    return "" if elapsed is None else f". elapsed = {elapsed*1_000:.0f} ms"


def function_end(
    function_name: str,
    result: typing.Any | None = None,
    elapsed: float | None = None,
) -> str:
    return (
        f"end function {function_name}()"
        + _execution_result(result)
        + _elapsed(elapsed)
    )


def current_value(name: str, value: typing.Any) -> str:
    return f"{name} = {value}"


def parameter_received(name: str, value: typing.Any) -> str:
    return f"received parameter {name} = {value}"


# MAYBE: Add arguments logging to this function.
def logging_mark(logger):
    def wrapper1(function):
        def wrapper(*args, **kwargs):
            logger.debug(function_begin(function.__name__))
            debug_begin = timeit.default_timer()

            result = function(*args, **kwargs)

            debug_end = timeit.default_timer()
            logger.debug(
                function_end(
                    function.__name__,
                    result=result,
                    elapsed=debug_end - debug_begin,
                )
            )

            return result

        return wrapper

    return wrapper1
