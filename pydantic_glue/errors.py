"""Errors."""


class ObjectWithoutPropertiesError(Exception):
    def __init__(self) -> None:
        super().__init__("Object without properties or additionalProperties can't be represented")


class UnknownTypeError(Exception):
    def __init__(self, type_name: str) -> None:
        super().__init__(f"Unknown type: {type_name}")


class GlueMapWithoutTypesError(Exception):
    def __init__(self) -> None:
        super().__init__("Glue Cannot Support a Map Without Types")
