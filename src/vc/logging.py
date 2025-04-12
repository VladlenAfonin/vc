import typing


def function_begin(function_name: str) -> str:
    return f"begin function {function_name}()"


def function_end(function_name: str, result: typing.Any | None = None) -> str:
    return f"end function {function_name}()" + (
        "" if result is None else f". execution result: {result}"
    )


def parameter_received(name: str, value: typing.Any) -> str:
    return f"received parameter {name} = {value}"
