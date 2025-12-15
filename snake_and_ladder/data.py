"""
Data Module for Snake and Ladder Game
Handles database operations for saving algorithm timings and player win records
"""
import os
import sqlite3
from datetime import datetime
from typing import List, Tuple

from common.db_base import close_connection, get_connection


# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "App.db")


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================
def init_database():
    """
    Initialize the database and create tables if they don't exist.
    
    Creates two tables:
    1. algorithm_timings - stores time taken for each algorithm in each round
    2. player_wins - stores player name and correct answer only when player wins
    
    Handles migration for existing databases by adding round_id column if missing.
    """
    conn = None
    try:
        conn = get_connection(DB_PATH)
        cursor = conn.cursor()

        # Create algorithm_timings table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS algorithm_timings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                round_id INTEGER NOT NULL,
                bfs_time REAL NOT NULL,
                dijkstra_time REAL NOT NULL,
                timestamp TEXT NOT NULL,
                UNIQUE(round_id)
            )
        """
        )

        # Create player_wins table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS player_wins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                round_id INTEGER NOT NULL,
                player_name TEXT NOT NULL,
                correct_answer INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (round_id) REFERENCES algorithm_timings(round_id)
            )
        """
        )

        # Migration: Add round_id column to existing player_wins table if missing
        try:
            cursor.execute("PRAGMA table_info(player_wins)")
            columns = [col[1] for col in cursor.fetchall()]
            if "round_id" not in columns:
                cursor.execute("ALTER TABLE player_wins ADD COLUMN round_id INTEGER")
        except sqlite3.OperationalError:
            # Column already exists or table doesn't exist yet
            pass

        # Ensure round_id in algorithm_timings is unique (required for FK)
        try:
            cursor.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_algorithm_timings_round_id "
                "ON algorithm_timings(round_id)"
            )
        except sqlite3.OperationalError:
            pass

        conn.commit()
    except sqlite3.Error as e:
        raise RuntimeError(f"Database initialization failed: {e}")
    finally:
        close_connection(conn)


# ============================================================================
# ALGORITHM TIMINGS OPERATIONS
# ============================================================================
def save_algorithm_timings(
    round_id: int, bfs_time: float, dijkstra_time: float
) -> bool:
    """
    Save algorithm timings for a round.
    
    :param round_id: Unique identifier for the game round
    :param bfs_time: Time taken by BFS algorithm (in microseconds)
    :param dijkstra_time: Time taken by Dijkstra algorithm (in microseconds)
    :return: True if successful, False otherwise
    """
    conn = None
    try:
        init_database()

        conn = get_connection(DB_PATH)
        cursor = conn.cursor()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            """
            INSERT INTO algorithm_timings 
            (round_id, bfs_time, dijkstra_time, timestamp)
            VALUES (?, ?, ?, ?)
        """,
            (round_id, bfs_time, dijkstra_time, timestamp),
        )

        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error saving algorithm timings: {e}")
        return False
    finally:
        close_connection(conn)


def get_algorithm_timings() -> List[Tuple]:
    """
    Retrieve all algorithm timing records.
    
    :return: List of tuples containing (id, round_id, bfs_time, dijkstra_time, timestamp)
    """
    conn = None
    try:
        conn = get_connection(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, round_id, bfs_time, dijkstra_time, timestamp
            FROM algorithm_timings
            ORDER BY timestamp DESC
        """
        )

        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error retrieving algorithm timings: {e}")
        return []
    finally:
        close_connection(conn)


# ============================================================================
# PLAYER WINS OPERATIONS
# ============================================================================
def save_player_win(round_id: int, player_name: str, correct_answer: int) -> bool:
    """
    Save player win record. Only called when player wins the round.
    
    :param round_id: The round ID this win belongs to
    :param player_name: Name of the player
    :param correct_answer: The correct minimum dice throws
    :return: True if successful, False otherwise
    """
    conn = None
    try:
        init_database()

        conn = get_connection(DB_PATH)
        cursor = conn.cursor()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            """
            INSERT INTO player_wins 
            (round_id, player_name, correct_answer, timestamp)
            VALUES (?, ?, ?, ?)
        """,
            (round_id, player_name, correct_answer, timestamp),
        )

        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error saving player win: {e}")
        return False
    finally:
        close_connection(conn)


def get_player_wins() -> List[Tuple]:
    """
    Retrieve all player win records.
    
    :return: List of tuples containing (id, round_id, player_name, correct_answer, timestamp)
    """
    conn = None
    try:
        conn = get_connection(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, round_id, player_name, correct_answer, timestamp
            FROM player_wins
            ORDER BY timestamp DESC
        """
        )

        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error retrieving player wins: {e}")
        return []
    finally:
        close_connection(conn)


def get_player_wins_with_round_info() -> List[Tuple]:
    """
    Retrieve all player win records with algorithm timing information (JOIN query).
    
    :return: List of tuples containing (win_id, round_id, player_name, correct_answer,
             bfs_time, dijkstra_time, timestamp)
    """
    conn = None
    try:
        conn = get_connection(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 
                pw.id,
                pw.round_id,
                pw.player_name,
                pw.correct_answer,
                at.bfs_time,
                at.dijkstra_time,
                pw.timestamp
            FROM player_wins pw
            LEFT JOIN algorithm_timings at ON pw.round_id = at.round_id
            ORDER BY pw.timestamp DESC
        """
        )

        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error retrieving player wins with round info: {e}")
        return []
    finally:
        close_connection(conn)


# ============================================================================
# ROUND MANAGEMENT
# ============================================================================
def get_next_round_id() -> int:
    """
    Get the next round ID by finding the maximum round_id and adding 1.
    
    :return: Next round ID
    """
    conn = None
    try:
        conn = get_connection(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT MAX(round_id) FROM algorithm_timings")
        result = cursor.fetchone()

        if result[0] is None:
            return 1
        return result[0] + 1
    except sqlite3.Error as e:
        print(f"Error getting next round ID: {e}")
        return 1
    finally:
        close_connection(conn)
