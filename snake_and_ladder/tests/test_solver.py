import os
import sys

import pytest

# Add project root to path to allow imports from both root and snake_and_ladder directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from snake_and_ladder.solver import SnakeLadderSolver


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def empty_board_solver():
    size = 6
    return SnakeLadderSolver(size=size, snakes={}, ladders={})


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def test_bfs_simple_board(empty_board_solver):
    moves, path, elapsed_time = empty_board_solver.bfs_min_dice()

    assert isinstance(moves, int) and moves > 0
    assert isinstance(elapsed_time, float) and elapsed_time >= 0
    assert path[0] == 1
    assert path[-1] == empty_board_solver.total_cells


def test_dijkstra_simple_board(empty_board_solver):
    moves, path, elapsed_time = empty_board_solver.dijkstra_min_dice()

    assert isinstance(moves, int) and moves > 0
    assert isinstance(elapsed_time, float) and elapsed_time >= 0
    assert path[0] == 1
    assert path[-1] == empty_board_solver.total_cells


def test_bfs_and_dijkstra_match_on_unweighted_board(empty_board_solver):
    bfs_moves, _, _ = empty_board_solver.bfs_min_dice()
    dj_moves, _, _ = empty_board_solver.dijkstra_min_dice()

    # On an unweighted board both algorithms should find the same minimum
    assert bfs_moves == dj_moves


def test_snake_effect_path_valid():
    size = 6
    snakes = {14: 7}  # snake from 14 to 7
    solver = SnakeLadderSolver(size=size, snakes=snakes, ladders={})

    moves, path, elapsed_time = solver.bfs_min_dice()

    assert path[0] == 1
    assert path[-1] == size * size
    assert isinstance(moves, int) and moves > 0
    assert isinstance(elapsed_time, float) and elapsed_time >= 0


def test_ladder_effect_reaches_top():
    size = 6
    ladders = {3: 15}  # ladder from 3 to 15
    solver = SnakeLadderSolver(size=size, snakes={}, ladders=ladders)

    moves, path, elapsed_time = solver.bfs_min_dice()

    assert 15 in path  # ensures ladder is taken somewhere along the path
    assert path[-1] == size * size
    assert isinstance(elapsed_time, float) and elapsed_time >= 0


def test_path_is_monotonic_non_decreasing(empty_board_solver):
    _, path, _ = empty_board_solver.bfs_min_dice()
    # After applying snakes/ladders, the visited sequence should not go backwards
    assert all(path[i] <= path[i + 1] for i in range(len(path) - 1))


def test_tiny_board_deterministic_path():
    """On a 2x2 board the solver should finish in one throw (1 -> 4)."""
    size = 2
    solver = SnakeLadderSolver(size=size, snakes={}, ladders={})

    moves, path, elapsed_time = solver.bfs_min_dice()

    assert moves == 1
    assert path == [1, 4]
    assert elapsed_time >= 0.0


def test_edge_snake_near_goal():
    """A snake right before the goal should still allow finishing."""
    size = 6  # total 36
    snakes = {35: 2}  # big setback
    solver = SnakeLadderSolver(size=size, snakes=snakes, ladders={})

    moves, path, elapsed_time = solver.bfs_min_dice()

    assert path[0] == 1 and path[-1] == size * size
    assert moves > 0
    assert elapsed_time >= 0.0


def test_chained_ladders_are_taken():
    """Chained ladders should be followed to reach higher cells quickly."""
    size = 6
    ladders = {2: 10, 10: 20}
    solver = SnakeLadderSolver(size=size, snakes={}, ladders=ladders)

    _, path, _ = solver.bfs_min_dice()

    # The path should reach at least one of the ladder destinations
    # (the algorithm might jump directly from 2 to 20 via the chain)
    # Verify the path is valid and reaches the end
    assert path[0] == 1
    assert path[-1] == size * size
    # At least one ladder destination should be reached
    assert any(pos in path for pos in [10, 20])


def test_mixed_snakes_and_ladders():
    """Mixed board should still yield a valid path to the end."""
    size = 6
    snakes = {16: 5, 22: 8, 33: 12}
    ladders = {3: 18, 11: 25, 15: 30}
    solver = SnakeLadderSolver(size=size, snakes=snakes, ladders=ladders)

    moves_bfs, path_bfs, _ = solver.bfs_min_dice()
    moves_dj, path_dj, _ = solver.dijkstra_min_dice()

    assert path_bfs[-1] == size * size
    assert path_dj[-1] == size * size
    # Dijkstra should not be worse than BFS; on unweighted graphs they should match
    assert moves_dj == moves_bfs
