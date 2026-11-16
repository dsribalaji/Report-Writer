"""Strict, data-only chart schema. Never interpret model output as Python."""
import math

MAX_POINTS = 200
TEXT_LIMIT = 200


def validate_chart_spec(spec):
    if not isinstance(spec, dict):
        raise ValueError("Chart spec must be an object, not executable code")
    allowed = {"kind", "x", "y", "title", "xlabel", "ylabel"}
    if set(spec) - allowed:
        raise ValueError("Unsupported chart fields")
    kind = spec.get("kind")
    if kind not in ("bar", "line", "scatter", "pie"):
        raise ValueError("Chart kind must be bar, line, scatter, or pie")
    x, y = spec.get("x"), spec.get("y")
    if not isinstance(x, list) or not isinstance(y, list):
        raise ValueError("Chart x and y must be arrays")
    if not 1 <= len(x) <= MAX_POINTS or len(x) != len(y):
        raise ValueError("Chart arrays must have equal lengths of 1 to 200")

    def number(value):
        return (type(value) in (int, float) and abs(value) <= 1e12
                and math.isfinite(value))

    if not all(number(v) for v in y):
        raise ValueError("Chart y values must be finite numbers within +/-1e12")
    if kind == "pie" and (any(v < 0 for v in y) or sum(y) <= 0):
        raise ValueError("Pie values must be nonnegative with a positive sum")
    for value in x:
        if kind == "scatter":
            if not number(value):
                raise ValueError("Scatter x values must be finite numbers")
        elif not (number(value) or (isinstance(value, str) and len(value) <= TEXT_LIMIT)):
            raise ValueError("Chart x values must be short labels or finite numbers")
    for field in ("title", "xlabel", "ylabel"):
        if field in spec and (not isinstance(spec[field], str) or len(spec[field]) > TEXT_LIMIT):
            raise ValueError("Chart titles and axis labels must be short strings")
    return dict(spec, x=list(x), y=list(y))
