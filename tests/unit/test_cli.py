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
