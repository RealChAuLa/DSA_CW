"""
Script to view App.db database details
Run this script to see the database structure and all records
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from snake_and_ladder.data import (
    init_database,
    get_algorithm_timings,
    get_player_wins,
    get_player_wins_with_round_info
)
import sqlite3

def view_table_structure(db_path):
    """Display the structure of tables in App.db"""
    conn = None
    try:
        from common.db_base import get_connection, close_connection
        conn = get_connection(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table_name in tables:
            table = table_name[0]
            print("\n" + "="*80)
            print(f"TABLE STRUCTURE: {table}")
            print("="*80)
            
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            
            print(f"{'Column Name':<20} {'Type':<15} {'Not Null':<10} {'Default':<15} {'PK':<5}")
            print("-"*80)
            for col in columns:
                cid, name, col_type, not_null, default_val, pk = col
                print(f"{name:<20} {col_type:<15} {'YES' if not_null else 'NO':<10} {str(default_val) if default_val else 'None':<15} {'YES' if pk else 'NO':<5}")
            print("="*80)
        
    except sqlite3.Error as e:
        print(f"Error viewing table structure: {e}")
    finally:
        if conn:
            conn.close()

def main():
    """Main function to display database information"""
    print("\n" + "="*80)
    print("SNAKE AND LADDER GAME - App.db DATABASE VIEWER")
    print("="*80)
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), "App.db")
    
    # Initialize database (creates if doesn't exist)
    try:
        init_database()
        print(f"Database initialized successfully! Location: {db_path}")
    except Exception as e:
        print(f"Error initializing database: {e}")
        return
    
    # View table structures
    view_table_structure(db_path)
    
    # View algorithm timings
    print("\n" + "="*80)
    print("ALGORITHM TIMINGS RECORDS")
    print("="*80)
    timings = get_algorithm_timings()
    if timings:
        print(f"{'ID':<5} {'Round ID':<10} {'BFS Time (μs)':<15} {'Dijkstra Time (μs)':<18} {'Timestamp':<20}")
        print("-"*80)
        for timing in timings:
            record_id, round_id, bfs_time, dijkstra_time, timestamp = timing
            print(f"{record_id:<5} {round_id:<10} {bfs_time:<15.2f} {dijkstra_time:<18.2f} {timestamp:<20}")
    else:
        print("No algorithm timing records found.")
    print("="*80)
    print(f"Total Algorithm Timing Records: {len(timings)}")
    
    # View player wins
    print("\n" + "="*80)
    print("PLAYER WINS RECORDS")
    print("="*80)
    wins = get_player_wins()
    if wins:
        print(f"{'ID':<5} {'Round ID':<10} {'Player Name':<20} {'Correct Answer':<15} {'Timestamp':<20}")
        print("-"*80)
        for win in wins:
            record_id, round_id, player_name, correct_answer, timestamp = win
            round_str = str(round_id) if round_id is not None else "N/A"
            print(f"{record_id:<5} {round_str:<10} {player_name:<20} {correct_answer:<15} {timestamp:<20}")
    else:
        print("No player win records found.")
    print("="*80)
    print(f"Total Player Win Records: {len(wins)}")
    
    # View player wins with round relationship
    print("\n" + "="*80)
    print("PLAYER WINS WITH ROUND RELATIONSHIP")
    print("="*80)
    wins_with_round = get_player_wins_with_round_info()
    if wins_with_round:
        print(f"{'Win ID':<8} {'Round ID':<10} {'Player Name':<20} {'Answer':<8} {'BFS Time (μs)':<15} {'Dijkstra Time (μs)':<18} {'Timestamp':<20}")
        print("-"*100)
        for win in wins_with_round:
            win_id, round_id, player_name, correct_answer, bfs_time, dijkstra_time, timestamp = win
            round_str = str(round_id) if round_id is not None else "N/A"
            bfs_str = f"{bfs_time:.2f}" if bfs_time is not None else "N/A"
            dijkstra_str = f"{dijkstra_time:.2f}" if dijkstra_time is not None else "N/A"
            print(f"{win_id:<8} {round_str:<10} {player_name:<20} {correct_answer:<8} {bfs_str:<15} {dijkstra_str:<18} {timestamp:<20}")
    else:
        print("No player win records with round information found.")
    print("="*80)
    
    # Statistics
    if wins:
        print("\n" + "="*80)
        print("STATISTICS")
        print("="*80)
        unique_players = set(win[2] for win in wins)  # Updated index since round_id is now included
        print(f"Unique Players: {len(unique_players)}")
        print(f"Players: {', '.join(sorted(unique_players))}")
        
        # Show wins per round
        rounds_with_wins = [win[1] for win in wins if win[1] is not None]
        unique_rounds = set(rounds_with_wins)
        print(f"Rounds with Wins: {len(unique_rounds)}")
        if unique_rounds:
            print(f"Round IDs: {', '.join(map(str, sorted(unique_rounds)))}")
        print("="*80 + "\n")

if __name__ == "__main__":
    main()

