"""Command-line entry point: ``json-value-substitutor INPUT OUTPUT``."""

import argparse
import json
import sys
from collections.abc import Sequence

from .core import substitution


def non_negative_int(text: str) -> int:
    if not text.isdigit():
        raise argparse.ArgumentTypeError(f"expected a non-negative integer, got {text!r}")
    return int(text)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="json-value-substitutor",
        description="Wrap every leaf value of a JSON object as {_content, _type}.",
    )
    parser.add_argument("input", help="JSON file whose top-level value is an object")
    parser.add_argument("output", help="where to write the substituted JSON")
    parser.add_argument(
        "-d",
        "--depth",
        type=non_negative_int,
        default=None,
        help="only rewrite the first DEPTH levels (default: all levels)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        with open(args.input, encoding="utf-8") as source:
            data = json.load(source)
    except OSError as exc:
        print(f"error: cannot read {args.input}: {exc.strerror}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: {args.input} is not valid JSON: {exc}", file=sys.stderr)
        return 1
    if not isinstance(data, dict):
        print(f"error: {args.input}: top-level JSON value must be an object", file=sys.stderr)
        return 1
    with open(args.output, "w", encoding="utf-8") as target:
        json.dump(substitution(data, args.depth), target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
