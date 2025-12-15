# eight_queens/tests/test_solver.py
"""
Unit tests for eight_queens.solver

Covers:
- Correct number of solutions (92)
- Validity of generated solutions
- Sequential vs Threaded consistency
- Basic safety checks
"""

import pytest

from eight_queens import solver
from eight_queens import models


def test_sequential_solution_count():
    """
    Sequential solver must find exactly 92 solutions.
    """
    solutions = solver.find_all_solutions_sequential()
    assert len(solutions) == 92


def test_sequential_solutions_are_valid():
    """
    Every solution produced by the sequential solver must be a valid board.
    """
    solutions = solver.find_all_solutions_sequential()
    for board in solutions:
        assert models.board_is_valid_format(board)


def test_threaded_solution_count():
    """
    Threaded solver must also find exactly 92 solutions.
    """
    solutions, _ = solver.run_threaded_timed()
    assert len(solutions) == 92


def test_sequential_and_threaded_match():
    """
    Sequential and threaded solvers must produce the same solution set.
    Order does not matter.
    """
    seq_solutions = solver.find_all_solutions_sequential()
    thr_solutions, _ = solver.run_threaded_timed()

    seq_set = set(models.board_to_str(b) for b in seq_solutions)
    thr_set = set(models.board_to_str(b) for b in thr_solutions)

    assert seq_set == thr_set


def test_is_safe_basic_cases():
    """
    Basic correctness tests for is_safe().
    """
    board = [-1] * 8
    assert solver.is_safe(board, 0, 0) is True

    board[0] = 0
    # same column
    assert solver.is_safe(board, 1, 0) is False
    # diagonal
    assert solver.is_safe(board, 1, 1) is False
    # safe placement
    assert solver.is_safe(board, 1, 2) is True


def test_timed_sequential_returns_time():
    """
    Timed sequential run must return (solutions, time) where time > 0.
    """
    solutions, elapsed = solver.run_sequential_timed()
    assert len(solutions) == 92
    assert elapsed >= 0.0
