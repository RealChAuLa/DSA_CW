# Tower of Hanoi - SQLite Database Module
import sqlite3
import os


class Database:
    """SQLite database for storing game data and statistics"""
    
    def __init__(self):
        try:
            # Create database in the same folder as this file
            db_path = os.path.join(os.path.dirname(__file__), 'tower_of_hanoi.db')
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self._create_tables()
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            raise
    
    def _create_tables(self):
        # Games history table
        self.conn.execute('''CREATE TABLE IF NOT EXISTS tower_of_hanoi (
            id INTEGER PRIMARY KEY, player TEXT, disks INTEGER, pegs INTEGER,
            moves INTEGER, min_moves INTEGER, predicted_moves INTEGER, is_correct INTEGER, 
            algorithm TEXT, time_ms REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        
        # Algorithm performance table
        self.conn.execute('''CREATE TABLE IF NOT EXISTS toh_algo_perf (
            id INTEGER PRIMARY KEY, algorithm TEXT, disks INTEGER, pegs INTEGER,
            moves INTEGER, time_ms REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        
        # Winners table - stores winning games with algorithm and time
        self.conn.execute('''CREATE TABLE IF NOT EXISTS toh_winners (
            id INTEGER PRIMARY KEY, player TEXT, disks INTEGER, pegs INTEGER,
            moves INTEGER, min_moves INTEGER, predicted_moves INTEGER,
            algorithm TEXT, time_ms REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        
        # Migration: add column if missing
        try:
            self.conn.execute('ALTER TABLE tower_of_hanoi ADD COLUMN predicted_moves INTEGER')
        except sqlite3.OperationalError:
            pass
        self.conn.commit()
    
    def save_game(self, player, disks, pegs, moves, min_moves, predicted_moves, correct, algo=None, time_ms=0):
        try:
            self.conn.execute(
                'INSERT INTO tower_of_hanoi (player,disks,pegs,moves,min_moves,predicted_moves,is_correct,algorithm,time_ms) VALUES (?,?,?,?,?,?,?,?,?)',
                (player, disks, pegs, moves, min_moves, predicted_moves, 1 if correct else 0, algo, time_ms))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving game: {e}")
    
    def save_winner(self, player, disks, pegs, moves, min_moves, predicted_moves, algo, time_ms):
        try:
            self.conn.execute(
                'INSERT INTO toh_winners (player,disks,pegs,moves,min_moves,predicted_moves,algorithm,time_ms) VALUES (?,?,?,?,?,?,?,?)',
                (player, disks, pegs, moves, min_moves, predicted_moves, algo, time_ms))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving winner: {e}")
    
    def save_algo_perf(self, algo, disks, pegs, moves, time_ms):
        try:
            self.conn.execute(
                'INSERT INTO toh_algo_perf (algorithm,disks,pegs,moves,time_ms) VALUES (?,?,?,?,?)',
                (algo, disks, pegs, moves, time_ms))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving algorithm performance: {e}")
    
    def get_history(self, limit=50):
        return self.conn.execute(
            'SELECT * FROM tower_of_hanoi ORDER BY timestamp DESC LIMIT ?', (limit,)).fetchall()
    
    def get_winners(self, limit=50):
        return self.conn.execute(
            'SELECT * FROM toh_winners ORDER BY timestamp DESC LIMIT ?', (limit,)).fetchall()
    
    def get_leaderboard(self):
        try:
            return self.conn.execute('''
                SELECT player, COUNT(DISTINCT timestamp) as games, 
                    COUNT(DISTINCT CASE WHEN is_correct=1 THEN timestamp END) as correct_predictions 
                FROM tower_of_hanoi GROUP BY player ORDER BY correct_predictions DESC, games DESC LIMIT 20
            ''').fetchall()
        except sqlite3.Error as e:
            print(f"Error getting leaderboard: {e}")
            return []
    
    def get_algo_stats(self, pegs):
        return self.conn.execute('''
            SELECT algorithm, disks, moves, time_ms as time, AVG(time_ms) as avg_time, COUNT(*) as runs 
            FROM toh_algo_perf WHERE pegs=? GROUP BY algorithm, disks ORDER BY algorithm, disks
        ''', (pegs,)).fetchall()
    
    def get_comparison_data(self):
        """Get best 3-peg vs 4-peg performance for matching disk counts"""
        try:
            return self.conn.execute('''
                SELECT t3.disks, t3.moves as moves_3peg, t4.moves as moves_4peg,
                    t3.time_ms as time_3peg, t4.time_ms as time_4peg
                FROM (SELECT disks, MIN(moves) as moves, MIN(time_ms) as time_ms 
                      FROM toh_algo_perf WHERE pegs=3 GROUP BY disks) t3
                INNER JOIN (SELECT disks, MIN(moves) as moves, MIN(time_ms) as time_ms 
                           FROM toh_algo_perf WHERE pegs=4 GROUP BY disks) t4
                ON t3.disks = t4.disks ORDER BY t3.disks
            ''').fetchall()
        except sqlite3.Error as e:
            print(f"Error getting comparison data: {e}")
            return []
    
    def get_all_played_games_for_comparison(self):
        """Get all played games for comparison table"""
        try:
            return self.conn.execute('''
                SELECT disks, pegs, algorithm, moves, time_ms FROM toh_algo_perf ORDER BY disks, pegs
            ''').fetchall()
        except sqlite3.Error as e:
            print(f"Error getting played games for comparison: {e}")
            return []
