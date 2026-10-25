"""
tests/test_parser.py - Tests for scanning/parser.py.

HOW TO USE
    Run all tests with:  pytest
    Add one test per real sample scan in tests/samples/ BEFORE writing the parser.
    Write the test, watch it fail, then make the parser pass it (test-first!).

TODO (Intermediate): write real tests, for example:
    - a valid match scan parses to the right team number and match number
    - a scan with too few fields raises ValueError
    - a pit scan is recognized as a pit scan
"""

import pytest


@pytest.mark.skip(
    reason="TODO: add real sample scans to tests/samples/ and write tests"
)
def test_parse_valid_match_scan():
    raise NotImplementedError
