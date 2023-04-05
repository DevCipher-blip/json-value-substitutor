from json import dump, load
from sys import argv, exit

USAGE = "usage: python3 substitute.py INPUT.json [DEPTH] OUTPUT.json"


def substitution(dictionary, depth=None, current_depth=0):
    if depth is not None and current_depth >= depth:
        return dictionary
    # Build a new dict so the caller's data is left untouched.
    return {
        key: substitution(value, depth, current_depth + 1)
        if isinstance(value, dict)
        else {'_content': value, '_type': str(type(value))}
        for key, value in dictionary.items()
    }


if __name__ == '__main__':
    if len(argv) not in (3, 4):
        exit(USAGE)
    input_filename = argv[1]
    output_filename = argv[-1]
    depth = None
    if len(argv) == 4:
        if not argv[2].isdigit():
            exit(f"DEPTH must be a non-negative integer\n{USAGE}")
        depth = int(argv[2])
    with open(input_filename, encoding="utf-8") as source:
        data = load(source)
    if not isinstance(data, dict):
        exit(f"{input_filename}: top-level JSON value must be an object")
    with open(output_filename, "w", encoding="utf-8") as target:
        dump(substitution(data, depth), target)
