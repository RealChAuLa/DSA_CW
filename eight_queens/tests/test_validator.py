# eight_queens/tests/test_validator.py
"""
Unit tests for validation logic related to the Eight Queens game.

Covers:
- Board string parsing
- Board format validation
- Detection of invalid solutions
- Normalization of solution strings

Uses:
- eight_queens.models
- common.validators (basic input validation)
"""

import pytest

from eight_queens import models
from common.validator import validate_non_empty_string


def test_validate_non_empty_string_valid():
    assert validate_non_empty_string("Alice") == "Alice"
    assert validate_non_empty_string("  Bob  ") == "Bob"


def test_validate_non_empty_string_invalid():
    with pytest.raises(ValueError):
        validate_non_empty_string("")
    with pytest.raises(ValueError):
        validate_non_empty_string("   ")
    with pytest.raises(ValueError):
        validate_non_empty_string(None)


def test_str_to_board_valid():
    board = models.str_to_board("0,4,7,5,2,6,1,3")
    assert board == [0, 4, 7, 5, 2, 6, 1, 3]
    assert models.board_is_valid_format(board)


def test_str_to_board_valid_whitespace():
    board = models.str_to_board("0 4 7 5 2 6 1 3")
    assert board == [0, 4, 7, 5, 2, 6, 1, 3]


def test_str_to_board_invalid_length():
    with pytest.raises(ValueError):
        models.str_to_board("0,1,2,3,4,5,6")  # only 7 values


def test_str_to_board_invalid_range():
    with pytest.raises(ValueError):
        models.str_to_board("0,4,7,5,2,6,1,9")  # 9 out of range


def test_str_to_board_duplicate_column():
    with pytest.raises(ValueError):
        models.str_to_board("0,4,7,5,2,6,1,1")  # duplicate column


def test_str_to_board_diagonal_conflict():
    # queens on (0,0) and (1,1) conflict diagonally
    with pytest.raises(ValueError):
        models.str_to_board("0,1,7,5,2,6,4,3")


def test_board_to_str_roundtrip():
    original = [0, 4, 7, 5, 2, 6, 1, 3]
    s = models.board_to_str(original)
    restored = models.str_to_board(s)
    assert restored == original


def test_normalize_solution_str():
    normalized = models.normalize_solution_str("0 4 7 5 2 6 1 3")
    assert normalized == "0,4,7,5,2,6,1,3"


def test_board_is_valid_format_false_cases():
    assert models.board_is_valid_format([0, 1, 2, 3, 4, 5, 6, 7]) is False  # diagonal conflicts
    assert models.board_is_valid_format([0, 0, 1, 2, 3, 4, 5, 6]) is False  # duplicate columns


def test_board_is_valid_format_true_case():
    assert models.board_is_valid_format([0, 4, 7, 5, 2, 6, 1, 3]) is True
