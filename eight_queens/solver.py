# eight_queens/solver.py
"""
Backtracking solver for the Eight Queens problem.

Public API expected by the UI:
- find_all_solutions_sequential() -> List[List[int]]
- run_sequential_timed() -> Tuple[List[List[int]], float]
- run_threaded_timed() -> Tuple[List[List[int]], float]

Implementation notes:
- Board representation: list of 8 integers where index = row, value = column (0..7)
- Uses backtracking (is_safe) to generate solutions.
- Threaded solver splits work by fixing the queen in row 0 to each column (0..7)
  and runs a backtracking solver for rows 1..7 in separate threads, then merges results.
"""
import traceback
from typing import List, Tuple, Callable
from concurrent.futures import ThreadPoolExecutor


# Try to import the project's common timer utility (optional)
try:
    from common.timer import measure_execution_time
except Exception:
    measure_execution_time = None  # fallback to manual timing

# Try to use models.board_to_str if available for canonicalization (optional)
try:
    from eight_queens import models
    _board_to_str = getattr(models, "board_to_str", lambda b: ",".join(str(x) for x in b))
except Exception:
    models = None
    _board_to_str = lambda b: ",".join(str(x) for x in b)


def is_safe(board: List[int], row: int, col: int) -> bool:
    """
    Check if placing a queen at (row, col) is safe given current partial board.
    Only rows [0..row-1] are assumed filled.
    """
    for r in range(row):
        c = board[r]
        if c == col:
            return False
        if abs(c - col) == abs(r - row):
            return False
    return True


def _backtrack_collect(row: int, board: List[int], solutions: List[List[int]]):
    """
    Classic recursive backtracking that collects complete boards into `solutions`.
    """
    if row == 8:
        # found full placement; append a copy
        solutions.append(board.copy())
        return

    for col in range(8):
        if is_safe(board, row, col):
            board[row] = col
            _backtrack_collect(row + 1, board, solutions)
            board[row] = -1  # reset for backtracking


def find_all_solutions_sequential() -> List[List[int]]:
    """
    Find all 92 solutions using a single-threaded backtracking solver.
    Returns a list of boards (each board is List[int] of length 8).
    """
    board = [-1] * 8
    solutions: List[List[int]] = []
    _backtrack_collect(0, board, solutions)
    return solutions


def run_sequential_timed() -> Tuple[List[List[int]], float]:
    """
    Run the sequential solver and return (solutions, elapsed_seconds).
    Uses common.timer.measure_execution_time if available, otherwise uses time.perf_counter.
    """
    if measure_execution_time:
        (sols, elapsed) = measure_execution_time(find_all_solutions_sequential)
        return sols, elapsed

    # fallback
    import time
    start = time.perf_counter()
    sols = find_all_solutions_sequential()
    elapsed = time.perf_counter() - start
    return sols, elapsed


def _solve_with_fixed_first_col(first_col: int) -> List[List[int]]:
    """
    Solve the board with the queen fixed at row 0, column=first_col.
    Returns a list of solutions (each solution is a board list).
    """
    board = [-1] * 8
    board[0] = first_col
    local_solutions: List[List[int]] = []
    # continue from row 1
    _backtrack_collect(1, board, local_solutions)
    return local_solutions


def run_threaded_timed(max_workers: int = 8) -> Tuple[List[List[int]], float]:
    """
    Run a threaded variant splitting by first-column placement.
    Returns (solutions_unique, elapsed_seconds).

    Note: Python's GIL makes threaded CPU-bound speedups unreliable;
    this function is primarily for coursework comparison (behavioral).
    """
    # use measure_execution_time wrapper if available
    def _threaded():
        solutions_accum: List[List[int]] = []
        try:
            with ThreadPoolExecutor(max_workers=max_workers) as ex:
                # dispatch tasks for first_col = 0..7
                futures = list(ex.map(_solve_with_fixed_first_col, range(8)))
                # futures is an iterable of lists
                for lst in futures:
                    if lst:
                        solutions_accum.extend(lst)
        except Exception:
            # in case of thread errors, try a safe sequential fallback
            traceback.print_exc()
            for c in range(8):
                solutions_accum.extend(_solve_with_fixed_first_col(c))

        # deduplicate/canonicalize (just in case)
        unique = {}
        for b in solutions_accum:
            key = _board_to_str(b)
            unique[key] = b

        # return list of unique solutions (order doesn't matter)
        return list(unique.values())

    if measure_execution_time:
        (sols, elapsed) = measure_execution_time(_threaded)
        return sols, elapsed

    import time
    start = time.perf_counter()
    sols = _threaded()
    elapsed = time.perf_counter() - start
    return sols, elapsed


# Convenience exports
__all__ = [
    "find_all_solutions_sequential",
    "run_sequential_timed",
    "run_threaded_timed",
    "is_safe",
]

# Quick self-test when executed directly
if __name__ == "__main__":
    print("Running quick self-test for eight_queens.solver ...")
    sols_seq, t_seq = run_sequential_timed()
    print(f"Sequential found {len(sols_seq)} solutions in {t_seq:.6f}s")
    sols_threaded, t_thread = run_threaded_timed()
    print(f"Threaded found {len(sols_threaded)} solutions in {t_thread:.6f}s")
    # sanity check - should be 92 unique solutions
    seq_set = set(_board_to_str(b) for b in sols_seq)
    thr_set = set(_board_to_str(b) for b in sols_threaded)
    print("Unique sequential:", len(seq_set))
    print("Unique threaded:", len(thr_set))
    if len(seq_set) != 92 or len(thr_set) != 92 or seq_set != thr_set:
        print("WARNING: solution sets differ or not 92 solutions.")
    else:
        print("OK: both methods returned 92 identical unique solutions.")
