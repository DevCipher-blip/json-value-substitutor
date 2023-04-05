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


def test_lists_are_leaves_and_not_walked() -> None:
    assert substitution({"tags": [1, {"x": 2}]}) == {
        "tags": {"_content": [1, {"x": 2}], "_type": "<class 'list'>"}
    }


def test_json_literals_keep_their_python_types() -> None:
    result = substitution({"t": True, "n": None, "f": 1.5})
    assert [v["_type"] for v in result.values()] == [
        "<class 'bool'>",
        "<class 'NoneType'>",
        "<class 'float'>",
    ]


def test_empty_nested_object_stays_empty() -> None:
    assert substitution({"a": {}}) == {"a": {}}


@pytest.mark.parametrize(
    ("depth", "expected"),
    [
        (0, {"a": 1, "b": {"c": 2}}),
        (1, {"a": {"_content": 1, "_type": "<class 'int'>"}, "b": {"c": 2}}),
        (
            2,
            {
                "a": {"_content": 1, "_type": "<class 'int'>"},
                "b": {"c": {"_content": 2, "_type": "<class 'int'>"}},
            },
        ),
    ],
)
def test_depth_stops_rewriting_below_the_limit(depth: int, expected: dict[str, Any]) -> None:
    assert substitution({"a": 1, "b": {"c": 2}}, depth) == expected


def test_deep_nesting() -> None:
    data: dict[str, Any] = {"leaf": "x"}
    for _ in range(3000):
        data = {"n": data}
    result = substitution(data)
    for _ in range(3000):
        result = result["n"]
    assert result == {"leaf": {"_content": "x", "_type": "<class 'str'>"}}


def test_unicode_keys_and_values() -> None:
    assert substitution({"città": "Zürich 東京 🙂"}) == {
        "città": {"_content": "Zürich 東京 🙂", "_type": "<class 'str'>"}
    }
