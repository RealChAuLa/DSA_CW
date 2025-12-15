# eight_queens/models.py
"""
Data-format helpers for the Eight Queens game.

Public functions:
- board_to_str(board: list[int]) -> str
- str_to_board(s: str) -> list[int]
- board_is_valid_format(board: list[int]) -> bool
- normalize_solution_str(s: str) -> str
- pretty_print_board(board: list[int]) -> str

Board representation:
- A board is a list of 8 integers where index = row (0..7) and value = column (0..7).
- The canonical string form is "c0,c1,c2,...,c7" (comma-separated, no spaces).
"""

from typing import List


def _validate_length_and_type(board: List[int]) -> None:
    if not isinstance(board, list):
        raise TypeError("Board must be a list of 8 integers.")
    if len(board) != 8:
        raise ValueError("Board must contain exactly 8 integers.")
    for i, v in enumerate(board):
        if not isinstance(v, int):
            raise TypeError(f"Board element at index {i} is not an integer.")
        if v < 0 or v > 7:
            raise ValueError(f"Board element at index {i} ({v}) must be between 0 and 7.")


def board_is_valid_format(board: List[int]) -> bool:
    """
    Check whether `board` is a valid board format and no two queens threaten each other.

    Returns True if:
      - board is list of 8 integers in range 0..7
      - no two queens share the same column
      - no two queens share the same diagonal

    Raises TypeError/ValueError for malformed boards (useful for callers that want exceptions).
    """
    _validate_length_and_type(board)

    # check unique columns
    if len(set(board)) != 8:
        return False

    # check diagonals
    for r1 in range(8):
        for r2 in range(r1 + 1, 8):
            if abs(board[r1] - board[r2]) == abs(r1 - r2):
                return False
    return True


def board_to_str(board: List[int]) -> str:
    """
    Convert a board list to its canonical string representation: "c0,c1,...,c7".
    Raises TypeError/ValueError if board malformed.
    """
    _validate_length_and_type(board)
    return ",".join(str(x) for x in board)


def str_to_board(s: str) -> List[int]:
    """
    Parse a solution string into a board list[int].
    Accepts comma-separated or whitespace-separated numbers (e.g. "0,4,7,5,2,6,1,3" or "0 4 7 5 2 6 1 3").
    Raises ValueError/TypeError for invalid formats.
    """
    if s is None:
        raise ValueError("Input string is None.")
    if not isinstance(s, str):
        raise TypeError("Input must be a string.")

    # normalize separators: commas or whitespace
    parts = [p.strip() for p in s.replace(",", " ").split() if p.strip() != ""]
    if len(parts) != 8:
        raise ValueError("Solution must contain exactly 8 integers.")

    board: List[int] = []
    for i, part in enumerate(parts):
        if not (part.lstrip("-").isdigit()):
            raise ValueError(f"Element {i} ('{part}') is not an integer.")
        val = int(part)
        if val < 0 or val > 7:
            raise ValueError(f"Element {i} ({val}) out of range 0..7.")
        board.append(val)

    # ensure the board does not contain obvious conflicts
    if len(set(board)) != 8:
        raise ValueError("Two queens share the same column (columns must be unique).")

    for r1 in range(8):
        for r2 in range(r1 + 1, 8):
            if abs(board[r1] - board[r2]) == abs(r1 - r2):
                raise ValueError("Two queens threaten each other diagonally.")

    return board


def normalize_solution_str(s: str) -> str:
    """
    Convert any accepted string form into the canonical form "c0,c1,...,c7".
    Useful for DB keys and deduplication.
    """
    board = str_to_board(s)
    return board_to_str(board)


def pretty_print_board(board: List[int]) -> str:
    """
    Return a multi-line string visualising the 8x8 board with 'Q' for queens and '.' for empty squares.

    Example:
    0,4,7,5,2,6,1,3  -> returns an 8-line string where each line has 8 characters separated by spaces.
    """
    _validate_length_and_type(board)
    rows = []
    for r in range(8):
        cols = []
        for c in range(8):
            cols.append("Q" if board[r] == c else ".")
        rows.append(" ".join(cols))
    return "\n".join(rows)


__all__ = [
    "board_to_str",
    "str_to_board",
    "board_is_valid_format",
    "normalize_solution_str",
    "pretty_print_board",
]
