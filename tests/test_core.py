from typing import Any

import pytest

from json_value_substitutor import substitution


def test_substitution_simple() -> None:
    assert substitution({"a": 1, "b": "hello"}) == {
        "a": {"_content": 1, "_type": "<class 'int'>"},
        "b": {"_content": "hello", "_type": "<class 'str'>"},
    }


@pytest.mark.parametrize(
    ("input_dict", "depth", "expected"),
    [
        (
            {"a": 1, "b": "Good Luck"},
            None,
            {
                "a": {"_content": 1, "_type": "<class 'int'>"},
                "b": {"_content": "Good Luck", "_type": "<class 'str'>"},
            },
        ),
        ({"a": {"b": {"c": 1}}}, 3, {"a": {"b": {"c": {"_content": 1, "_type": "<class 'int'>"}}}}),
        ({}, None, {}),
    ],
)
def test_substitution_depth(
    input_dict: dict[str, Any], depth: int | None, expected: dict[str, Any]
) -> None:
    assert substitution(input_dict, depth) == expected


def test_substitution_leaves_input_untouched() -> None:
    data = {"a": {"b": 1}}
    substitution(data)
    assert data == {"a": {"b": 1}}
