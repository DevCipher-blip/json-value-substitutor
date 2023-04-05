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
