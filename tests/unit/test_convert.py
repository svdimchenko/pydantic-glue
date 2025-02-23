from __future__ import annotations

import datetime
import json
from typing import Optional, Union

import pytest
from pydantic import BaseModel, Field, field_serializer

from pydantic_glue import convert
from pydantic_glue.errors import ObjectWithoutPropertiesError


def test_empty():
    assert convert("") == []


def test_single_string_column():
    class A(BaseModel):
        name: str

    expected = [("name", "string")]
    assert convert(json.dumps(A.model_json_schema())) == expected


def test_single_float_column():
    class A(BaseModel):
        name: float

    expected = [("name", "float")]
    assert convert(json.dumps(A.model_json_schema())) == expected


def test_single_boolean_column():
    class A(BaseModel):
        name: bool

    expected = [("name", "boolean")]
    assert convert(json.dumps(A.model_json_schema())) == expected


def test_single_dict_as_string_column():
    class A(BaseModel):
        as_string: dict

        @field_serializer("as_string")
        def dump_json(self, value: dict) -> str:
            return json.dumps(value)

    expected = [("as_string", "string")]
    assert convert(json.dumps(A.model_json_schema(mode="serialization"))) == expected


def test_single_type_override_column():
    class A(BaseModel):
        special: int = Field(
            ...,
            json_schema_extra={
                "glue_type": "gluetype",
            },
        )

    expected = [("special", "gluetype")]
    assert convert(json.dumps(A.model_json_schema())) == expected


def test_single_date_column():
    class A(BaseModel):
        modified_on: datetime.date

    expected = [("modified_on", "date")]
    assert convert(json.dumps(A.model_json_schema())) == expected


def test_single_datetime_column():
    class A(BaseModel):
        modified_on: datetime.datetime

    expected = [("modified_on", "timestamp")]
    assert convert(json.dumps(A.model_json_schema())) == expected


def test_multiple_string_column():
    class A(BaseModel):
        hey: str
        ho: str
        lets: str
        go: str

    expected = [
        ("hey", "string"),
        ("ho", "string"),
        ("lets", "string"),
        ("go", "string"),
    ]

    assert convert(json.dumps(A.model_json_schema())) == expected


def test_multiple_string_and_int_column():
    class A(BaseModel):
        hey: str
        ho: int
        lets: str
        go: int

    expected = [
        ("hey", "string"),
        ("ho", "int"),
        ("lets", "string"),
        ("go", "int"),
    ]

    assert convert(json.dumps(A.model_json_schema())) == expected


def test_nested_object_with_strings():
    class B(BaseModel):
        foo: str
        bar: str

    class A(BaseModel):
        some_b: B

    expected = [("some_b", "struct<foo:string,bar:string>")]

    assert convert(json.dumps(A.model_json_schema())) == expected


def test_nested_object_with_strings_and_ints():
    class B(BaseModel):
        foo: str
        x: int

    class A(BaseModel):
        one_b: B
        another_b: B
        some_number: int

    expected = [
        ("one_b", "struct<foo:string,x:int>"),
        ("another_b", "struct<foo:string,x:int>"),
        ("some_number", "int"),
    ]

    assert convert(json.dumps(A.model_json_schema())) == expected


def test_list_of_ints():
    class A(BaseModel):
        nums: list[int]

    expected = [("nums", "array<int>")]
    assert convert(json.dumps(A.model_json_schema())) == expected


def test_list_of_ints_and_strings():
    class A(BaseModel):
        nums: list[int]
        strs: list[str]
        other: str

    expected = [
        ("nums", "array<int>"),
        ("strs", "array<string>"),
        ("other", "string"),
    ]

    assert convert(json.dumps(A.model_json_schema())) == expected


def test_list_of_objects():
    class B(BaseModel):
        foo: str
        x: int

    class A(BaseModel):
        nums: list[int]
        boos: list[B]
        other: str

    expected = [
        ("nums", "array<int>"),
        ("boos", "array<struct<foo:string,x:int>>"),
        ("other", "string"),
    ]

    assert (
        convert(
            json.dumps(A.model_json_schema()),
        )
        == expected
    )


def test_custom_type():
    class A(BaseModel):
        unixtime: int = Field(
            ...,
            json_schema_extra={
                "glue_type": "timestamp",
            },
        )
        optional_unixtime: Optional[int] = Field(
            ...,
            json_schema_extra={
                "glue_type": "timestamp",
            },
        )
        clobber_union_unixtime: Optional[Union[int, str]] = Field(
            ...,
            json_schema_extra={
                "glue_type": "timestamp",
            },
        )
        correct_union_unixtime: Optional[Union[int, str]] = Field(
            ...,
            json_schema_extra={
                "glue_type": "union<timestamp,string>",
            },
        )

    expected = [
        ("unixtime", "timestamp"),
        ("optional_unixtime", "timestamp"),
        ("clobber_union_unixtime", "timestamp"),
        ("correct_union_unixtime", "union<timestamp,string>"),
    ]

    assert (
        convert(
            json.dumps(A.model_json_schema(mode="serialization")),
        )
        == expected
    )


def test_invalid_object_raises():
    class A(BaseModel):
        map_serialized_as_object: dict

    with pytest.raises(ObjectWithoutPropertiesError):
        convert(json.dumps(A.model_json_schema()))


def test_union_of_string_and_int():
    class A(BaseModel):
        stuff: Union[str, int]

    expected = [("stuff", "union<string,int>")]
    assert convert(json.dumps(A.model_json_schema())) == expected


def test_union_of_complex_types():
    class B(BaseModel):
        hey: str
        ho: str

    class C(BaseModel):
        lets: int
        go: int

    class A(BaseModel):
        stuff: Union[B, C]

    expected = [("stuff", "union<struct<hey:string,ho:string>,struct<lets:int,go:int>>")]
    assert convert(json.dumps(A.model_json_schema())) == expected


def test_single_optional_column():
    class A(BaseModel):
        name: Optional[str] = None

    expected = [("name", "string")]
    actual = json.dumps(A.model_json_schema())
    assert convert(actual) == expected


def test_map_object():
    class A(BaseModel):
        some_a: dict[str, int]

    expected = [("some_a", "map<string,int>")]
    assert convert(json.dumps(A.model_json_schema())) == expected


def test_nested_map_object():
    class A(BaseModel):
        hey: str
        ho: str

    class B(BaseModel):
        some_b: dict[str, dict[str, A]]

    expected = [("some_b", "map<string,map<string,struct<hey:string,ho:string>>>")]
    assert convert(json.dumps(B.model_json_schema())) == expected
