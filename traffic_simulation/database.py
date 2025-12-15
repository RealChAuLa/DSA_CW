import sqlite3
import logging
import os

# Configure logging for database operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database path relative to this file's directory
DB_PATH = os.path.join(os.path.dirname(__file__), "traffic_simulations.db")

class DatabaseError(Exception):
    """Custom exception for database operations"""
    pass

def init_db():
    """Initialize the database with proper exception handling"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # Table for CORRECT answers only
        cur.execute("""
            CREATE TABLE IF NOT EXISTS win_results (
                id INTEGER PRIMARY KEY,
                player_name TEXT NOT NULL,
                player_guess INTEGER NOT NULL,
                correct_answer INTEGER NOT NULL,
                ek_time REAL,
                ff_time REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            ) WITHOUT ROWID
        """)
        
        # Table for ALL game results (pass and fail)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS all_game_results (
                id INTEGER PRIMARY KEY,
                player_name TEXT NOT NULL,
                player_guess INTEGER NOT NULL,
                correct_answer INTEGER NOT NULL,
                ek_time REAL,
                ff_time REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            ) WITHOUT ROWID
        """)
        
        # Remove sqlite_sequence table if it exists
        cur.execute("DROP TABLE IF EXISTS sqlite_sequence")
        
        conn.commit()
        logger.info("Database initialized successfully")
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")
        raise DatabaseError(f"Failed to initialize database: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}")
        raise DatabaseError(f"Unexpected error: {e}")
    finally:
        if conn:
            conn.close()

def clear_db():
    """Clear all data from database tables"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        cur.execute("DELETE FROM win_results")
        cur.execute("DELETE FROM all_game_results")
        
        conn.commit()
        logger.info("Database cleared successfully")
    except sqlite3.Error as e:
        logger.error(f"Database clear error: {e}")
        raise DatabaseError(f"Failed to clear database: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during database clear: {e}")
        raise DatabaseError(f"Unexpected error: {e}")
    finally:
        if conn:
            conn.close()

def validate_player_name(player_name):
    """
    Validate player name input
    Returns: (is_valid, error_message)
    """
    if not player_name:
        return False, "Player name cannot be empty"
    
    if not isinstance(player_name, str):
        return False, "Player name must be a string"
    
    # Remove extra whitespace
    player_name = player_name.strip()
    
    if len(player_name) < 2:
        return False, "Player name must be at least 2 characters"
    
    if len(player_name) > 50:
        return False, "Player name cannot exceed 50 characters"
    
    # Check for valid characters (letters, numbers, spaces, basic punctuation)
    if not all(c.isalnum() or c.isspace() or c in "._-" for c in player_name):
        return False, "Player name contains invalid characters"
    
    return True, ""

def validate_answer(answer):
    """
    Validate answer input
    Returns: (is_valid, error_message)
    """
    if answer is None:
        return False, "Answer cannot be None"
    
    try:
        answer = int(answer)
        if answer < 0:
            return False, "Answer must be a non-negative integer"
        return True, ""
    except (ValueError, TypeError):
        return False, "Answer must be a valid integer"

def insert_correct_result(player_name, player_guess, correct_answer, ek_time, ff_time):
    """
    Insert a correct result into the database with comprehensive validation and error handling.
    Only called when player's answer is correct.
    
    Args:
        player_name: Name of the player (string)
        player_guess: The player's guessed answer (integer, equals correct_answer)
        correct_answer: The correct answer they identified (integer)
        ek_time: Edmonds-Karp algorithm execution time (float)
        ff_time: Ford-Fulkerson algorithm execution time (float)
    
    Returns:
        (success, message): Tuple indicating success and message
    """
    # Validate player name
    is_valid, error_msg = validate_player_name(player_name)
    if not is_valid:
        logger.warning(f"Invalid player name: {error_msg}")
        return False, error_msg
    
    # Validate answer
    is_valid, error_msg = validate_answer(correct_answer)
    if not is_valid:
        logger.warning(f"Invalid answer: {error_msg}")
        return False, error_msg
    
    # Validate times (should be non-negative)
    try:
        ek_time = float(ek_time) if ek_time is not None else 0.0
        ff_time = float(ff_time) if ff_time is not None else 0.0
        
        if ek_time < 0 or ff_time < 0:
            return False, "Execution times cannot be negative"
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid time values: {e}")
        return False, "Invalid execution time values"
    
    # Sanitize player name
    player_name = player_name.strip()
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        cur = conn.cursor()
        
        # Get next ID
        cur.execute("SELECT MAX(id) FROM win_results")
        max_id = cur.fetchone()[0]
        next_id = (max_id + 1) if max_id is not None else 1

        cur.execute("""
            INSERT INTO win_results (id, player_name, player_guess, correct_answer, ek_time, ff_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (next_id, player_name, int(player_guess), int(correct_answer), ek_time, ff_time))

        conn.commit()
        logger.info(f"Successfully saved correct answer for player: {player_name}")
        return True, "Result saved successfully"
        
    except sqlite3.IntegrityError as e:
        logger.error(f"Database integrity error: {e}")
        return False, "Database integrity error occurred"
    except sqlite3.OperationalError as e:
        logger.error(f"Database operational error: {e}")
        return False, "Database is currently unavailable"
    except sqlite3.Error as e:
        logger.error(f"Database error while inserting result: {e}")
        return False, f"Failed to save result: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error while inserting result: {e}")
        return False, "An unexpected error occurred while saving"
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")

def insert_all_result(player_name, player_guess, correct_answer, ek_time, ff_time):
    """
    Insert ALL game results (both pass and fail) into the database with comprehensive validation.
    
    Args:
        player_name: Name of the player (string)
        player_guess: The player's guessed answer (integer)
        correct_answer: The correct answer (integer)
        ek_time: Edmonds-Karp algorithm execution time (float)
        ff_time: Ford-Fulkerson algorithm execution time (float)
    
    Returns:
        (success, message): Tuple indicating success and message
    """
    # Validate player name
    is_valid, error_msg = validate_player_name(player_name)
    if not is_valid:
        logger.warning(f"Invalid player name: {error_msg}")
        return False, error_msg
    
    # Validate answer
    is_valid, error_msg = validate_answer(correct_answer)
    if not is_valid:
        logger.warning(f"Invalid answer: {error_msg}")
        return False, error_msg
    
    # Validate guess
    is_valid, error_msg = validate_answer(player_guess)
    if not is_valid:
        logger.warning(f"Invalid guess: {error_msg}")
        return False, error_msg
    
    # Validate times (should be non-negative)
    try:
        ek_time = float(ek_time) if ek_time is not None else 0.0
        ff_time = float(ff_time) if ff_time is not None else 0.0
        
        if ek_time < 0 or ff_time < 0:
            return False, "Execution times cannot be negative"
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid time values: {e}")
        return False, "Invalid execution time values"
    
    # Sanitize player name
    player_name = player_name.strip()
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        cur = conn.cursor()
        
        # Get next ID
        cur.execute("SELECT MAX(id) FROM all_game_results")
        max_id = cur.fetchone()[0]
        next_id = (max_id + 1) if max_id is not None else 1

        cur.execute("""
            INSERT INTO all_game_results (id, player_name, player_guess, correct_answer, ek_time, ff_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (next_id, player_name, int(player_guess), int(correct_answer), ek_time, ff_time))

        conn.commit()
        logger.info(f"Successfully saved result for player: {player_name} (guess: {player_guess}, correct: {correct_answer})")
        return True, "Result saved successfully"
        
    except sqlite3.IntegrityError as e:
        logger.error(f"Database integrity error: {e}")
        return False, "Database integrity error occurred"
    except sqlite3.OperationalError as e:
        logger.error(f"Database operational error: {e}")
        return False, "Database is currently unavailable"
    except sqlite3.Error as e:
        logger.error(f"Database error while inserting result: {e}")
        return False, f"Failed to save result: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error while inserting result: {e}")
        return False, "An unexpected error occurred while saving"
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")
