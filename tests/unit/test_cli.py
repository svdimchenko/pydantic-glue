import json
from pathlib import Path
from unittest import TestCase

from cli_test_helpers import shell
from pydantic_glue.cli import parse_args


def test_parse_args():

    args = parse_args(["-f", "foo/bar/file.py", "-c", "Test"])
    assert args.module_file == "foo/bar/file"
    assert args.class_name == "Test"
    assert args.output_file is None
    assert args.log_result is False
    assert args.json_schema_by_alias is True


def test_parse_args_schema_by_name():

    args = parse_args(["-f", "foo/bar/file.py", "-c", "Test", "--schema-by-name"])
    assert args.module_file == "foo/bar/file"
    assert args.class_name == "Test"
    assert args.output_file is None
    assert args.log_result is False
    assert args.json_schema_by_alias is False


def test_cli():
    shell("pydantic-glue -f tests/data/input.py -c A -o tests/tmp/actual.json")
    actual = json.loads(Path("tests/tmp/actual.json").read_text())
    expected = json.loads(Path("tests/data/expected.json").read_text())
    TestCase().assertDictEqual(actual["columns"], expected["columns"])


def test_cli_schema_by_name():
    shell("pydantic-glue -f tests/data/input.py -c A -o tests/tmp/actual_by_name.json --schema-by-name")
    actual = json.loads(Path("tests/tmp/actual_by_name.json").read_text())
    expected = json.loads(Path("tests/data/expected_by_name.json").read_text())
    TestCase().assertDictEqual(actual["columns"], expected["columns"])
