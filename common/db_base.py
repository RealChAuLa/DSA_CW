# common/db_base.py
import sqlite3
from typing import Optional


def get_connection(db_path: str) -> sqlite3.Connection:
    """
    Create and return a SQLite database connection.

    :param db_path: Path to the SQLite database file
    :return: sqlite3.Connection object
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        raise RuntimeError(f"Database connection failed: {e}")


def close_connection(conn: Optional[sqlite3.Connection]) -> None:
    """
    Safely close a SQLite database connection.

    :param conn: sqlite3.Connection object
    """
    if conn:
        conn.close()
