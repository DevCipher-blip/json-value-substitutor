import json
from pathlib import Path

import pytest

from json_value_substitutor.cli import main

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def test_example_matches_committed_output(tmp_path: Path) -> None:
    out = tmp_path / "out.json"
    assert main([str(EXAMPLES / "input.json"), str(out)]) == 0
    expected = json.loads((EXAMPLES / "output.json").read_text(encoding="utf-8"))
    assert json.loads(out.read_text(encoding="utf-8")) == expected


def test_top_level_array_is_rejected(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    src = tmp_path / "list.json"
    src.write_text("[1, 2]", encoding="utf-8")
    assert main([str(src), str(tmp_path / "out.json")]) == 1
    assert "must be an object" in capsys.readouterr().err


@pytest.mark.parametrize("argv", [[], ["only-one.json"], ["a.json", "b.json", "--depth", "-1"]])
def test_bad_arguments_exit_with_usage(argv: list[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(argv)
    assert exc.value.code == 2


def test_existing_output_is_not_overwritten(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "out.json"
    out.write_text("keep me", encoding="utf-8")
    assert main([str(EXAMPLES / "input.json"), str(out)]) == 1
    assert "--force" in capsys.readouterr().err
    assert out.read_text(encoding="utf-8") == "keep me"


def test_force_replaces_output_in_place(tmp_path: Path) -> None:
    src = tmp_path / "data.json"
    src.write_text('{"a": 1}', encoding="utf-8")
    assert main([str(src), str(src), "--force"]) == 0
    assert json.loads(src.read_text(encoding="utf-8")) == {
        "a": {"_content": 1, "_type": "<class 'int'>"}
    }
    assert [p.name for p in tmp_path.iterdir()] == ["data.json"]


@pytest.mark.parametrize("literal", ["NaN", "Infinity", "-Infinity"])
def test_non_standard_numbers_are_rejected(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], literal: str
) -> None:
    src = tmp_path / "nan.json"
    src.write_text(f'{{"a": {literal}}}', encoding="utf-8")
    out = tmp_path / "out.json"
    assert main([str(src), str(out)]) == 1
    assert "not allowed in strict JSON" in capsys.readouterr().err
    assert not out.exists()


def test_unicode_is_written_as_utf8(tmp_path: Path) -> None:
    src = tmp_path / "in.json"
    src.write_text('{"név": "Ünïcødé 東京"}', encoding="utf-8")
    out = tmp_path / "out.json"
    assert main([str(src), str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    assert "Ünïcødé 東京" in text
    assert json.loads(text) == {"név": {"_content": "Ünïcødé 東京", "_type": "<class 'str'>"}}


@pytest.mark.parametrize("content", ['{"a": 1', "", "{'a': 1}", '{"a": 1,}'])
def test_invalid_json_is_reported(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], content: str
) -> None:
    src = tmp_path / "bad.json"
    src.write_text(content, encoding="utf-8")
    out = tmp_path / "out.json"
    assert main([str(src), str(out)]) == 1
    assert "is not valid JSON" in capsys.readouterr().err
    assert not out.exists()


def test_non_utf8_input_is_reported(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    src = tmp_path / "latin1.json"
    src.write_bytes('{"a": "café"}'.encode("latin-1"))
    assert main([str(src), str(tmp_path / "out.json")]) == 1
    assert "is not valid JSON" in capsys.readouterr().err


def test_missing_input_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    out = tmp_path / "out.json"
    assert main([str(tmp_path / "nope.json"), str(out)]) == 1
    assert "cannot read" in capsys.readouterr().err
    assert not out.exists()


def test_missing_output_directory(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    out = tmp_path / "no-such-dir" / "out.json"
    assert main([str(EXAMPLES / "input.json"), str(out)]) == 1
    assert "cannot write" in capsys.readouterr().err


def test_depth_option(tmp_path: Path) -> None:
    out = tmp_path / "out.json"
    assert main([str(EXAMPLES / "input.json"), str(out), "--depth", "1"]) == 0
    result = json.loads(out.read_text(encoding="utf-8"))
    assert result["name"] == {"_content": "John", "_type": "<class 'str'>"}
    assert result["address1"] == {"street": "123 Main St", "city": "Anytown", "state": "CA"}


def test_nesting_beyond_the_recursion_limit(tmp_path: Path) -> None:
    levels = 3000
    src = tmp_path / "deep.json"
    src.write_text('{"a": ' * levels + "1" + "}" * levels, encoding="utf-8")
    out = tmp_path / "out.json"
    assert main([str(src), str(out)]) == 0
    result = json.loads(out.read_text(encoding="utf-8"))
    for _ in range(levels - 1):
        result = result["a"]
    assert result == {"a": {"_content": 1, "_type": "<class 'int'>"}}


def test_unparseably_deep_input_is_reported(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    levels = 100_000
    src = tmp_path / "deep.json"
    src.write_text("[" * levels + "]" * levels, encoding="utf-8")
    out = tmp_path / "out.json"
    assert main([str(src), str(out)]) == 1
    assert "nested too deeply" in capsys.readouterr().err
    assert not out.exists()
