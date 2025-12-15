"""
Unit tests for eight_queens. db_manager

Uses a temporary SQLite database to test:
- Table creation
- Inserting solutions
- Recognized solution logic
- Player submission storage
- Resetting recognized flags
- Saving timing data
"""

import os
import tempfile
import sqlite3
import pytest

from eight_queens import db_manager


@pytest.fixture
def temp_db():
    """
    Creates a temporary SQLite database for testing.
    """
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    db_manager.initialize(path)
    yield path

    # Reset module state for next test
    db_manager._DB_PATH = None
    os.remove(path)


def test_tables_created(temp_db):
    """
    Verify database tables exist after initialization.
    """
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    )
    tables = {row[0] for row in cursor.fetchall()}

    # Updated table names with eqp_ prefix
    expected_tables = {
        "eqp_solutions",
        "eqp_players",
        "eqp_timings",
    }

    assert expected_tables.issubset(tables)
    conn.close()


def test_get_db_path(temp_db):
    """
    Verify get_db_path returns the initialized path.
    """
    assert db_manager.get_db_path() == temp_db


def test_save_timing(temp_db):
    """
    Saving timing results should not raise errors.
    """
    db_manager. save_timing(
        technique="sequential",
        run_index=1,
        time_seconds=0.123
    )

    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    # Updated table name
    cursor.execute("SELECT technique, run_index, time_seconds FROM eqp_timings;")
    row = cursor.fetchone()
    conn.close()

    assert row == ("sequential", 1, 0.123)


def test_insert_and_check_solution(temp_db):
    """
    Test inserting a solution and checking if it exists.
    """
    solution = "0,4,7,5,2,6,1,3"

    # Initially does not exist
    assert db_manager.solution_exists(solution) is False

    # Insert solution
    db_manager.insert_solution(solution)

    # Now exists
    assert db_manager.solution_exists(solution) is True


def test_duplicate_solution_not_inserted(temp_db):
    """
    Inserting the same solution twice should not create duplicates.
    """
    solution = "0,4,7,5,2,6,1,3"

    db_manager.insert_solution(solution)
    db_manager.insert_solution(solution)

    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    # Updated table name
    cursor.execute(
        "SELECT COUNT(*) FROM eqp_solutions WHERE solution = ?;",
        (solution,)
    )
    count = cursor.fetchone()[0]
    conn.close()

    assert count == 1


def test_save_player_submission(temp_db):
    """
    Player submissions should be saved successfully with solution_id.
    """
    player = "Alice"
    solution = "0,4,7,5,2,6,1,3"

    db_manager.insert_solution(solution)
    db_manager.save_player_submission(player, solution)

    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    # Get solution_id first
    cursor.execute(
        "SELECT id FROM eqp_solutions WHERE solution = ?;",
        (solution,)
    )
    solution_id = cursor.fetchone()[0]

    # Check player was saved with correct solution_id
    cursor. execute(
        "SELECT name, solution_id FROM eqp_players WHERE solution_id = ?;",
        (solution_id,)
    )
    row = cursor.fetchone()
    conn.close()

    assert row[0] == player
    assert row[1] == solution_id


def test_mark_solution_recognized(temp_db):
    """
    Marking a solution as recognized should work correctly.
    """
    solution = "0,4,7,5,2,6,1,3"

    db_manager.insert_solution(solution)

    # First mark should return True (changed from 0 to 1)
    assert db_manager.mark_solution_recognized(solution) is True

    # Second mark should return False (already recognized)
    assert db_manager.mark_solution_recognized(solution) is False


def test_mark_nonexistent_solution_raises(temp_db):
    """
    Marking a non-existent solution should raise ValueError.
    """
    solution = "nonexistent"

    with pytest.raises(ValueError):
        db_manager.mark_solution_recognized(solution)


def test_get_recognized_solutions(temp_db):
    """
    Get recognized solutions should return correct data.
    """
    solution = "0,4,7,5,2,6,1,3"
    player = "Bob"

    db_manager.insert_solution(solution)
    db_manager.save_player_submission(player, solution)
    db_manager.mark_solution_recognized(solution)

    results = db_manager.get_recognized_solutions()

    assert len(results) == 1
    assert results[0][0] == solution
    assert results[0][1] == player


def test_get_recognized_count(temp_db):
    """
    Get recognized count should return correct number.
    """
    solution1 = "0,4,7,5,2,6,1,3"
    solution2 = "1,5,0,6,3,7,2,4"

    db_manager.insert_solution(solution1)
    db_manager.insert_solution(solution2)

    # Initially no recognized solutions
    assert db_manager.get_recognized_count() == 0

    # Mark one as recognized
    db_manager.mark_solution_recognized(solution1)
    assert db_manager.get_recognized_count() == 1

    # Mark another as recognized
    db_manager.mark_solution_recognized(solution2)
    assert db_manager.get_recognized_count() == 2


def test_reset_all_recognized_flags(temp_db):
    """
    Resetting recognized flags should clear all flags.
    """
    solution = "0,4,7,5,2,6,1,3"

    db_manager.insert_solution(solution)
    db_manager.mark_solution_recognized(solution)

    # Verify it's recognized
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    # Updated table name
    cursor.execute("SELECT recognized FROM eqp_solutions WHERE solution = ? ;", (solution,))
    assert cursor.fetchone()[0] == 1

    # Reset flags
    db_manager.reset_all_recognized_flags()

    # Verify it's no longer recognized
    cursor.execute("SELECT recognized FROM eqp_solutions WHERE solution = ?;", (solution,))
    assert cursor.fetchone()[0] == 0
    conn.close()


def test_empty_player_name_raises(temp_db):
    """
    Empty player name should raise ValueError.
    """
    solution = "0,4,7,5,2,6,1,3"
    db_manager.insert_solution(solution)

    with pytest.raises(ValueError):
        db_manager. save_player_submission("", solution)


def test_empty_technique_raises(temp_db):
    """
    Empty technique name should raise ValueError.
    """
    with pytest.raises(ValueError):
        db_manager.save_timing("", 1, 0.5)


def test_save_player_nonexistent_solution_raises(temp_db):
    """
    Saving player submission for non-existent solution should raise ValueError.
    """
    with pytest.raises(ValueError):
        db_manager.save_player_submission("Alice", "nonexistent_solution")


def test_operations_without_init_raise():
    """
    Operations without initialization should raise RuntimeError.
    """
    # Ensure DB is not initialized
    db_manager._DB_PATH = None

    with pytest.raises(RuntimeError):
        db_manager.insert_solution("test")

    with pytest.raises(RuntimeError):
        db_manager. solution_exists("test")

    with pytest.raises(RuntimeError):
        db_manager.mark_solution_recognized("test")

    with pytest.raises(RuntimeError):
        db_manager.save_player_submission("player", "test")

    with pytest.raises(RuntimeError):
        db_manager.get_recognized_solutions()

    with pytest.raises(RuntimeError):
        db_manager.get_recognized_count()

    with pytest.raises(RuntimeError):
        db_manager.reset_all_recognized_flags()

    with pytest.raises(RuntimeError):
        db_manager.save_timing("technique", 1, 0.5)