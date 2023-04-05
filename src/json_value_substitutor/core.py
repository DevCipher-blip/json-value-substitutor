"""Replace every leaf of a JSON object with a ``{_content, _type}`` wrapper."""

from typing import Any


def substitution(
    dictionary: dict[str, Any], depth: int | None = None, current_depth: int = 0
) -> dict[str, Any]:
    """Return a copy of ``dictionary`` with leaf values wrapped.

    Nested dicts are walked; anything else (including lists) counts as a
    leaf. ``depth`` limits how many levels are rewritten: levels at or below
    it are copied through unchanged.
    """
    if depth is not None and current_depth >= depth:
        return dictionary
    # Build a new dict so the caller's data is left untouched.
    return {
        key: substitution(value, depth, current_depth + 1)
        if isinstance(value, dict)
        else {"_content": value, "_type": str(type(value))}
        for key, value in dictionary.items()
    }
