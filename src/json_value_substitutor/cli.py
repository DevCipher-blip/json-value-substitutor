"""Command-line entry point: ``json-value-substitutor INPUT OUTPUT``."""

import argparse
import contextlib
import json
import os
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Any, NoReturn

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
    parser.add_argument("input", type=Path, help="JSON file whose top-level value is an object")
    parser.add_argument("output", type=Path, help="where to write the substituted JSON")
    parser.add_argument(
        "-d",
        "--depth",
        type=non_negative_int,
        default=None,
        help="only rewrite the first DEPTH levels (default: all levels)",
    )
    parser.add_argument(
        "-f", "--force", action="store_true", help="replace OUTPUT if it already exists"
    )
    return parser


def reject_constant(name: str) -> NoReturn:
    # Python's json accepts NaN/Infinity by default; RFC 8259 does not.
    raise ValueError(f"{name} is not allowed in strict JSON")


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as source:
        return json.load(source, parse_constant=reject_constant)


def write_atomically(path: Path, text: str) -> None:
    """Write via a temp file in the same directory, then rename over ``path``.

    A crash or full disk leaves either the old file or the new one, never a
    truncated mix, and lets INPUT and OUTPUT be the same file.
    """
    try:
        mode = path.stat().st_mode & 0o777
    except FileNotFoundError:
        umask = os.umask(0)
        os.umask(umask)
        mode = 0o666 & ~umask
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp_name, mode)
        os.replace(tmp_name, path)
    except BaseException:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(tmp_name)
        raise


def fail(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 1


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.output.exists() and not args.force:
        return fail(f"{args.output} already exists (use --force to replace it)")
    try:
        data = read_json(args.input)
    except OSError as exc:
        return fail(f"cannot read {args.input}: {exc.strerror}")
    except ValueError as exc:
        return fail(f"{args.input} is not valid JSON: {exc}")
    except RecursionError:
        return fail(f"{args.input} is nested too deeply to parse")
    if not isinstance(data, dict):
        return fail(f"{args.input}: top-level JSON value must be an object")
    try:
        text = json.dumps(substitution(data, args.depth), ensure_ascii=False, allow_nan=False)
    except RecursionError:
        return fail(f"{args.input} is nested too deeply to serialise")
    try:
        write_atomically(args.output, text)
    except OSError as exc:
        return fail(f"cannot write {args.output}: {exc.strerror}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
