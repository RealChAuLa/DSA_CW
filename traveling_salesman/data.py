"""
Database operations for Traveling Salesman Problem game.
Handles saving algorithm times and player wins.
"""

import os
import sqlite3
from typing import Optional
from common.db_base import get_connection, close_connection


# Database path in project root
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "App.db")


def init_database() -> None:
	"""
	Initialize the database and create tables if they don't exist.
	"""
	conn = None
	try:
		conn = get_connection(DB_PATH)
		cursor = conn.cursor()
		
		# Table 1: Rounds (to track each game round) - must be created first for foreign keys
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS rounds (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				player_name TEXT NOT NULL,
				main_city TEXT NOT NULL,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
			)
		""")
		
		# Table 2: Algorithm times per round
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS algorithm_times (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				round_id INTEGER NOT NULL,
				algorithm_name TEXT NOT NULL,
				time_taken REAL NOT NULL,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				FOREIGN KEY (round_id) REFERENCES rounds(id)
			)
		""")
		
		# Table 3: Player wins
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS player_wins (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				round_id INTEGER NOT NULL,
				player_name TEXT NOT NULL,
				home_city TEXT NOT NULL,
				user_selected_cities TEXT NOT NULL,
				shortest_route TEXT NOT NULL,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				FOREIGN KEY (round_id) REFERENCES rounds(id)
			)
		""")
		
		conn.commit()
	except sqlite3.Error as e:
		if conn:
			conn.rollback()
		raise RuntimeError(f"Database initialization failed: {e}")
	finally:
		close_connection(conn)


def create_round(player_name: str, main_city: str) -> int:
	"""
	Create a new round and return its ID.
	
	:param player_name: Name of the player
	:param main_city: The main city for this round
	:return: Round ID
	"""
	conn = None
	try:
		conn = get_connection(DB_PATH)
		cursor = conn.cursor()
		
		cursor.execute("""
			INSERT INTO rounds (player_name, main_city)
			VALUES (?, ?)
		""", (player_name, main_city))
		
		round_id = cursor.lastrowid
		conn.commit()
		return round_id
	except sqlite3.Error as e:
		if conn:
			conn.rollback()
		raise RuntimeError(f"Failed to create round: {e}")
	finally:
		close_connection(conn)


def save_algorithm_times(round_id: int, algorithm_times: dict[str, float]) -> None:
	"""
	Save algorithm execution times for a round.
	
	:param round_id: ID of the round
	:param algorithm_times: Dictionary mapping algorithm names to execution times
	"""
	conn = None
	try:
		conn = get_connection(DB_PATH)
		cursor = conn.cursor()
		
		for algorithm_name, time_taken in algorithm_times.items():
			cursor.execute("""
				INSERT INTO algorithm_times (round_id, algorithm_name, time_taken)
				VALUES (?, ?, ?)
			""", (round_id, algorithm_name, time_taken))
		
		conn.commit()
	except sqlite3.Error as e:
		if conn:
			conn.rollback()
		raise RuntimeError(f"Failed to save algorithm times: {e}")
	finally:
		close_connection(conn)


def save_player_win(round_id: int, player_name: str, home_city: str, 
					user_selected_cities: list[str], shortest_route: list[str]) -> None:
	"""
	Save a player win to the database.
	
	:param round_id: ID of the round
	:param player_name: Name of the player
	:param home_city: The main/home city for this round
	:param user_selected_cities: List of cities selected by the player
	:param shortest_route: The shortest route found (as a list of city names)
	"""
	conn = None
	try:
		conn = get_connection(DB_PATH)
		cursor = conn.cursor()
		
		# Convert lists to comma-separated strings for storage
		selected_cities_str = ",".join(user_selected_cities)
		route_str = " -> ".join(shortest_route)
		
		cursor.execute("""
			INSERT INTO player_wins (round_id, player_name, home_city, user_selected_cities, shortest_route)
			VALUES (?, ?, ?, ?, ?)
		""", (round_id, player_name, home_city, selected_cities_str, route_str))
		
		conn.commit()
	except sqlite3.Error as e:
		if conn:
			conn.rollback()
		raise RuntimeError(f"Failed to save player win: {e}")
	finally:
		close_connection(conn)

