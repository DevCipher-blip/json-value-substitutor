# Nested JSON substitution

## Read the example before the algorithm

This exercise transforms nested dictionary values into typed wrappers. Compare [input.json](input.json), [output.json](output.json), and [substitute.py](substitute.py) to see the representation before changing the recursion.

The two test modules describe depth and substitution behavior. Lists and scalar values deserve explicit cases when extending the format; avoid assuming that dictionary recursion also traverses every container type. This is a focused file-processing exercise, with no API server or frontend.

## 1. Run Program
### Run this scropt in this directory

    $ python3 substitute.py input.json ouput.json
## 2. Test Cases Coverage
### Install pytest by running command in terminal

    $ pip3 install pytest
Run Test 1

    $ python3 -m pytest test_substitution1.py
Run Test 2
    
    $ python3 -m pytest test_substitution2.py