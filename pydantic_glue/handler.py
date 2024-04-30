from typing import Any

import jsonref


def dispatch(v: dict[str, Any]) -> str:
    if "anyOf" in v:
        return handle_union(v)

    t = v["type"]

    if t == "object":
        if "additionalProperties" in v:
            return handle_map(v)
        return handle_object(v)

    if t == "array":
        return handle_array(v)

    if t == "string":
        return "string"

    if t == "boolean":
        return "boolean"

    if t == "integer":
        return "int"

    if t == "number":
        return "float"

    raise Exception(f"unknown type: {t}")


def handle_map(o: dict[str, Any]) -> str:
    t = o["additionalProperties"]
    res = dispatch(t)
    return f"map<{res}, {res}>"


def handle_union(o: dict[str, Any]) -> str:
    res = [dispatch(v) for v in o["anyOf"]]
    return f"union<{','.join(res)}>"


def map_dispatch(o: dict[str, Any]) -> list[tuple[str, str]]:
    return [(k, dispatch(v)) for k, v in o["properties"].items()]


def handle_object(o: dict[str, Any]) -> str:
    res = [f"{k}:{v}" for (k, v) in map_dispatch(o)]
    return f"struct<{','.join(res)}>"


def handle_array(o: dict[str, Any]) -> str:
    t = dispatch(o["items"])
    return f"array<{t}>"


def handle_root(o: dict[str, Any]) -> list[tuple[str, str]]:
    return map_dispatch(o)


def convert(schema: dict[str, Any]) -> list[Any] | list[tuple[str, str]]:
    if not schema:
        return []

    schema = jsonref.loads(schema)
    return handle_root(schema)
