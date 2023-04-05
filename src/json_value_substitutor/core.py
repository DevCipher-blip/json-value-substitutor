"""Replace every leaf of a JSON object with a ``{_content, _type}`` wrapper."""

from typing import Any


def wrap(value: Any) -> dict[str, Any]:
    return {"_content": value, "_type": str(type(value))}


def substitution(dictionary: dict[str, Any], depth: int | None = None) -> dict[str, Any]:
    """Return a new dict with every leaf value of ``dictionary`` wrapped.

    Nested dicts are walked; anything else (including lists) counts as a
    leaf. ``depth`` limits how many levels are rewritten: objects nested at
    or below that level are passed through unchanged (shared, not copied).

    The walk uses an explicit stack rather than recursion, so any nesting the
    ``json`` module can parse is handled without hitting the recursion limit.
    """
    if depth == 0:
        return dict(dictionary)
    result: dict[str, Any] = {}
    stack = [(dictionary, result, 1)]
    while stack:
        source, target, level = stack.pop()
        for key, value in source.items():
            if not isinstance(value, dict):
                target[key] = wrap(value)
            elif depth is not None and level >= depth:
                target[key] = value
            else:
                child: dict[str, Any] = {}
                target[key] = child
                stack.append((value, child, level + 1))
    return result
