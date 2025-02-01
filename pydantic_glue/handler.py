"""Convert Json schema to glue."""

from __future__ import annotations

from typing import Any, Union

import jsonref

from pydantic_glue.errors import GlueMapWithoutTypesError, ObjectWithoutPropertiesError, UnknownTypeError


def dispatch(v: dict[str, Any]) -> str:  # noqa: PLR0911
    """Dispatch json schema element as glue type."""
    if glue_type := v.get("glue_type"):
        return str(glue_type)

    if "anyOf" in v:
        return _handle_union(v)

    t = v["type"]

    if t == "object":
        return _handle_object(v)

    if t == "array":
        return _handle_array(v)

    if t == "string":
        if v.get("format") == "date-time":
            return "timestamp"
        if v.get("format") == "date":
            return "date"
        return "string"

    if t == "boolean":
        return "boolean"

    if t == "integer":
        return "int"

    if t == "number":
        return "float"

    raise UnknownTypeError(t)


def _handle_map(o: dict[str, Any]) -> str:
    t = o["additionalProperties"]
    res = dispatch(t)
    return f"map<string,{res}>"


def _handle_union(o: dict[str, Any]) -> str:
    types = [i for i in o["anyOf"] if i["type"] != "null"]
    if len(types) > 1:
        res = [dispatch(v) for v in types]
        return f"union<{','.join(res)}>"
    return dispatch(types[0])


def _map_dispatch(o: dict[str, Any]) -> list[tuple[str, str]]:
    return [(k, dispatch(v)) for k, v in o["properties"].items()]


def _handle_object(o: dict[str, Any]) -> str:
    if "additionalProperties" in o:
        if o["additionalProperties"] is True:
            raise GlueMapWithoutTypesError
        if o["additionalProperties"]:
            if "properties" in o:
                msg = "Merging types of properties and additionalProperties"
                raise NotImplementedError(msg)
            return _handle_map(o)

    if "properties" not in o:
        raise ObjectWithoutPropertiesError

    res = [f"{k}:{v}" for (k, v) in _map_dispatch(o)]
    return f"struct<{','.join(res)}>"


def _handle_array(o: dict[str, Any]) -> str:
    t = dispatch(o["items"])
    return f"array<{t}>"


def _handle_root(o: dict[str, Any]) -> list[tuple[str, str]]:
    return _map_dispatch(o)


def convert(schema: str) -> Union[list[Any], list[tuple[str, str]]]:
    """Convert json schema to glue."""
    if not schema:
        return []
    return _handle_root(jsonref.loads(schema))
