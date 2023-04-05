# json-value-substitutor

A small command-line tool that rewrites a JSON object so every leaf value is
replaced by a wrapper recording the value and its Python type:

```json
{"age": 30}   ->   {"age": {"_content": 30, "_type": "<class 'int'>"}}
```

Nested objects are walked and keep their keys; only the values at the bottom
are wrapped. It started as a file-processing exercise. Compare
[examples/input.json](examples/input.json) with
[examples/output.json](examples/output.json) to see the full transformation.
There is no server or UI.

## Setup

Requires Python 3.13 (pinned in `.python-version`). No runtime dependencies.

```sh
python3.13 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

The `dev` extra installs pytest, ruff and mypy. A plain `pip install .` is
enough to use the command.

## Usage

```
json-value-substitutor [-h] [-d DEPTH] [-f] input output
```

| Option | Meaning |
| --- | --- |
| `-d`, `--depth DEPTH` | Only rewrite the first `DEPTH` levels. Objects nested deeper are copied through unchanged. `0` leaves the file as it is. |
| `-f`, `--force` | Replace `output` if it already exists. Without it the tool refuses. |

`python -m json_value_substitutor` works the same way.

### Examples

These were captured from a run inside a fresh `python:3.13-slim` container.

Full substitution (output pretty-printed with `json.tool`, first lines only):

```console
$ json-value-substitutor examples/input.json out.json
$ python -m json.tool out.json | head -12
{
    "name": {
        "_content": "John",
        "_type": "<class 'str'>"
    },
    "age": {
        "_content": 30,
        "_type": "<class 'int'>"
    },
    "address1": {
        "street": {
            "_content": "123 Main St",
```

With `--depth 1` only the top level is rewritten; `address1` keeps its plain
values:

```console
$ json-value-substitutor examples/input.json shallow.json --depth 1
$ python -m json.tool shallow.json | head -12
{
    "name": {
        "_content": "John",
        "_type": "<class 'str'>"
    },
    "age": {
        "_content": 30,
        "_type": "<class 'int'>"
    },
    "address1": {
        "street": "123 Main St",
        "city": "Anytown",
```

Errors go to stderr with exit status 1 (2 for bad arguments):

```console
$ json-value-substitutor examples/input.json out.json
error: out.json already exists (use --force to replace it)
$ json-value-substitutor nan.json nan-out.json
error: nan.json is not valid JSON: NaN is not allowed in strict JSON
$ json-value-substitutor list.json list-out.json
error: list.json: top-level JSON value must be an object
$ json-value-substitutor missing.json x.json
error: cannot read missing.json: No such file or directory
```

From Python:

```python
from json_value_substitutor import substitution

substitution({"a": {"b": 1}})
# {'a': {'b': {'_content': 1, '_type': "<class 'int'>"}}}
```

## Behaviour worth knowing

- **Lists are leaves.** `{"tags": [1, 2]}` becomes
  `{"tags": {"_content": [1, 2], "_type": "<class 'list'>"}}`; objects inside
  a list are not walked. Empty nested objects stay `{}`.
- **`_type` is Python's name for the type** (`str(type(value))`), so JSON
  `true` is `<class 'bool'>`, `null` is `<class 'NoneType'>` and `1.5` is
  `<class 'float'>`. That format comes from the original exercise and is kept
  so existing output stays comparable.
- **Strict JSON.** Python's `json` module accepts `NaN` and `Infinity` by
  default; this tool rejects them, as RFC 8259 does. Input must be UTF-8.
- **Safe writes.** Output goes to a temporary file in the target directory,
  which is then renamed over `output`. A failed run never leaves a truncated
  file, and `input` and `output` may be the same path (with `--force`).
- **No recursion limit.** The walk uses an explicit stack, so anything the
  `json` module can parse (a few thousand levels) is handled. Input nested
  beyond that is reported as an error rather than a traceback.
- The input is never modified in memory; `substitution` returns a new dict.
  Subtrees below `--depth` are shared with the input rather than copied.

## Development

```sh
pytest           # 34 tests: core walk, depth, CLI errors, unicode, deep nesting
ruff check . && ruff format --check .
mypy             # strict mode over src/ and tests/
```

Layout:

```
src/json_value_substitutor/core.py   substitution() - the tree walk
src/json_value_substitutor/cli.py    argument parsing, strict read, atomic write
tests/                               pytest suites for both
examples/                            sample input and its expected output
```

## License

MIT - see [LICENSE](LICENSE).
