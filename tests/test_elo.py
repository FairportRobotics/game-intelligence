"""
tests/test_elo.py - Tests for metrics/elo.py.

TODO (Beginner): fill these in after implementing expected_score().
Simple facts a correct Elo formula must satisfy:
    - Equal ratings -> 0.5 chance
    - A much higher rating -> chance close to 1
    - expected_score(a, b) + expected_score(b, a) == 1
"""

import pytest


@pytest.mark.skip(reason="TODO: implement metrics.elo.expected_score first")
def test_equal_ratings_are_fifty_fifty():
    # from metrics.elo import expected_score
    # assert expected_score(1500, 1500) == 0.5
    raise NotImplementedError
