# eight_queens/db_manager.py
"""
SQLite DB manager for the Eight Queens game.

Public API used by the UI:
- initialize(db_path:  str) -> None
- insert_solution(solution_str: str) -> None
- solution_exists(solution_str: str) -> bool
- mark_solution_recognized(solution_str: str) -> bool
- save_player_submission(name: str, solution_str: str) -> None
- get_recognized_solutions() -> List[Tuple[str, str, str]]
- reset_all_recognized_flags() -> None
- save_timing(technique: str, run_index: int, time_seconds: float) -> None
- get_db_path() -> str

Notes:
- Uses common. db_base. get_connection to obtain sqlite3.Connection
- Tables created:
    eqp_solutions(id, solution TEXT UNIQUE, recognized INTEGER DEFAULT 0)
    eqp_players(id, name TEXT, solution_id INTEGER, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
    eqp_timings(id, technique TEXT, run_index INTEGER, time_seconds REAL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)
"""

from typing import List, Tuple, Optional
import sqlite3

try:
    from common.db_base import get_connection, close_connection
except Exception:
    # Provide minimal fallbacks if the common helpers are not available.
    import sqlite3


    def get_connection(db_path: str) -> sqlite3.Connection:
        return sqlite3.connect(db_path)


    def close_connection(conn: Optional[sqlite3.Connection]) -> None:
        if conn:
            conn.close()

_DB_PATH: Optional[str] = None


def get_db_path() -> Optional[str]:
    """Return currently configured DB path (or None if not initialized)."""
    return _DB_PATH


def initialize(db_path: str = "App.db") -> None:
    """
    Initialize the database file and ensure required tables exist.
    Sets module-level DB path used by other functions.
    """
    global _DB_PATH
    _DB_PATH = db_path
    conn = None
    try:
        conn = get_connection(db_path)
        cur = conn.cursor()

        # Create eqp_solutions table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS eqp_solutions
            (
                id
                INTEGER
                PRIMARY
                KEY
                AUTOINCREMENT,
                solution
                TEXT
                NOT
                NULL
                UNIQUE,
                recognized
                INTEGER
                NOT
                NULL
                DEFAULT
                0
            );
            """
        )

        # Create eqp_players table (stores solution_id instead of solution string)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS eqp_players
            (
                id
                INTEGER
                PRIMARY
                KEY
                AUTOINCREMENT,
                name
                TEXT
                NOT
                NULL,
                solution_id
                INTEGER
                NOT
                NULL,
                timestamp
                DATETIME
                DEFAULT
                CURRENT_TIMESTAMP,
                FOREIGN
                KEY
            (
                solution_id
            ) REFERENCES eqp_solutions
            (
                id
            ) ON DELETE CASCADE
                );
            """
        )

        # Create eqp_timings table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS eqp_timings
            (
                id
                INTEGER
                PRIMARY
                KEY
                AUTOINCREMENT,
                technique
                TEXT
                NOT
                NULL,
                run_index
                INTEGER
                NOT
                NULL,
                time_seconds
                REAL
                NOT
                NULL,
                created_at
                DATETIME
                DEFAULT
                CURRENT_TIMESTAMP
            );
            """
        )

        conn.commit()
    finally:
        close_connection(conn)


def _get_solution_id(cur: sqlite3.Cursor, solution_str: str) -> Optional[int]:
    """
    Helper function to get solution_id from solution string.
    Returns None if solution doesn't exist.
    """
    cur.execute("SELECT id FROM eqp_solutions WHERE solution = ?  LIMIT 1;", (solution_str,))
    row = cur.fetchone()
    return row[0] if row else None


def insert_solution(solution_str: str) -> None:
    """
    Insert a solution string into the eqp_solutions table.
    Uses INSERT OR IGNORE so duplicate inserts are ignored.
    """
    if _DB_PATH is None:
        raise RuntimeError("DB not initialized.  Call initialize(db_path) first.")

    conn = None
    try:
        conn = get_connection(_DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO eqp_solutions (solution, recognized) VALUES (?, 0);",
            (solution_str,),
        )
        conn.commit()
    finally:
        close_connection(conn)


def solution_exists(solution_str: str) -> bool:
    """
    Check if a solution exists in the eqp_solutions table.
    """
    if _DB_PATH is None:
        raise RuntimeError("DB not initialized. Call initialize(db_path) first.")

    conn = None
    try:
        conn = get_connection(_DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM eqp_solutions WHERE solution = ?  LIMIT 1;", (solution_str,))
        row = cur.fetchone()
        return row is not None
    finally:
        close_connection(conn)


def mark_solution_recognized(solution_str: str) -> bool:
    """
    Atomically mark a solution as recognized.
    Returns True if this call changed the flag from 0->1 (i.e., this player is the first to recognize it).
    Returns False if the solution was already recognized.

    Raises ValueError if the solution does not exist in the DB.
    """
    if _DB_PATH is None:
        raise RuntimeError("DB not initialized.  Call initialize(db_path) first.")

    conn = None
    try:
        conn = get_connection(_DB_PATH)
        cur = conn.cursor()

        # Ensure solution exists
        cur.execute("SELECT recognized FROM eqp_solutions WHERE solution = ? ;", (solution_str,))
        row = cur.fetchone()
        if row is None:
            raise ValueError("Solution does not exist in the database.  Precompute or insert the solution first.")

        # Atomic update:  only update if recognized is currently 0
        cur.execute(
            "UPDATE eqp_solutions SET recognized = 1 WHERE solution = ?  AND recognized = 0;",
            (solution_str,),
        )
        conn.commit()

        # rowcount == 1 means we updated (i.e., we marked it now)
        return cur.rowcount == 1
    finally:
        close_connection(conn)


def save_player_submission(name: str, solution_str: str) -> None:
    """
    Record a player's submission into the eqp_players table.
    Stores the solution_id (foreign key) instead of the solution string.
    Does not modify the eqp_solutions. recognized flag (marking should be done with mark_solution_recognized).
    """
    if _DB_PATH is None:
        raise RuntimeError("DB not initialized. Call initialize(db_path) first.")
    if not name or not str(name).strip():
        raise ValueError("Player name cannot be empty.")

    conn = None
    try:
        conn = get_connection(_DB_PATH)
        cur = conn.cursor()

        # Get solution_id from solution string
        solution_id = _get_solution_id(cur, solution_str)
        if solution_id is None:
            raise ValueError("Solution does not exist in the database. Cannot save player submission.")

        cur.execute(
            "INSERT INTO eqp_players (name, solution_id) VALUES (?, ?);",
            (str(name).strip(), solution_id),
        )
        conn.commit()
    finally:
        close_connection(conn)


def get_recognized_solutions() -> List[Tuple[str, str, str]]:
    """
    Return a list of tuples:  (solution_str, player_name, timestamp)
    For each recognized solution, return the player who recorded it most recently (if any).
    Results are ordered by timestamp descending.
    """
    if _DB_PATH is None:
        raise RuntimeError("DB not initialized. Call initialize(db_path) first.")

    conn = None
    try:
        conn = get_connection(_DB_PATH)
        cur = conn.cursor()

        # Join eqp_solutions with eqp_players using solution_id
        # For each solution where recognized=1, get the latest player submission timestamp and name.
        cur.execute(
            """
            SELECT s.solution, p.name, p.timestamp
            FROM eqp_solutions s
                     JOIN eqp_players p ON s.id = p.solution_id
            WHERE s.recognized = 1
              AND p.timestamp = (SELECT MAX(p2.timestamp) FROM eqp_players p2 WHERE p2.solution_id = s.id)
            ORDER BY p.timestamp DESC;
            """
        )
        rows = cur.fetchall()
        # rows are tuples (solution, name, timestamp)
        return [(r[0], r[1], r[2]) for r in rows]
    finally:
        close_connection(conn)


def get_recognized_count() -> int:
    """
    Return the count of recognized solutions.
    Useful for checking if all 92 solutions have been found.
    """
    if _DB_PATH is None:
        raise RuntimeError("DB not initialized.  Call initialize(db_path) first.")

    conn = None
    try:
        conn = get_connection(_DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM eqp_solutions WHERE recognized = 1;")
        row = cur.fetchone()
        return row[0] if row else 0
    finally:
        close_connection(conn)


def reset_all_recognized_flags() -> None:
    """
    Reset all eqp_solutions.recognized flags to 0.
    Use this to allow future players to submit the same answers again.
    """
    if _DB_PATH is None:
        raise RuntimeError("DB not initialized.  Call initialize(db_path) first.")

    conn = None
    try:
        conn = get_connection(_DB_PATH)
        cur = conn.cursor()
        cur.execute("UPDATE eqp_solutions SET recognized = 0 WHERE recognized != 0;")
        conn.commit()
    finally:
        close_connection(conn)


def save_timing(technique: str, run_index: int, time_seconds: float) -> None:
    """
    Save timing results for a run.  technique can be e.g. "sequential" or "threaded".
    """
    if _DB_PATH is None:
        raise RuntimeError("DB not initialized. Call initialize(db_path) first.")
    if technique is None or str(technique).strip() == "":
        raise ValueError("Technique name required.")

    conn = None
    try:
        conn = get_connection(_DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO eqp_timings (technique, run_index, time_seconds) VALUES (?, ?, ?);",
            (str(technique).strip(), int(run_index), float(time_seconds)),
        )
        conn.commit()
    finally:
        close_connection(conn)