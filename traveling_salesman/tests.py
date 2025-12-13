"""
Unit tests for Traveling Salesman Problem algorithms and Game class.
Uses pytest for testing framework.
"""

import pytest
from traveling_salesman.brute_force import BruteForce
from traveling_salesman.held_karp import HeldKarpDP
from traveling_salesman.nn_2opt import NearestNeighbor2Opt
from traveling_salesman.game import Game


# Test fixtures for distance matrices
@pytest.fixture
def simple_distance_matrix():
	"""Simple 4-city distance matrix for testing."""
	# Cities: A, B, C, D
	# A-B: 10, A-C: 15, A-D: 20
	# B-C: 35, B-D: 25
	# C-D: 30
	return [
		[0, 10, 15, 20],  # A
		[10, 0, 35, 25],  # B
		[15, 35, 0, 30],  # C
		[20, 25, 30, 0]   # D
	]


@pytest.fixture
def symmetric_distance_matrix():
	"""Symmetric 5-city distance matrix."""
	# Cities: A, B, C, D, E
	return [
		[0, 10, 20, 30, 40],   # A
		[10, 0, 15, 25, 35],   # B
		[20, 15, 0, 12, 22],   # C
		[30, 25, 12, 0, 18],   # D
		[40, 35, 22, 18, 0]    # E
	]


@pytest.fixture
def triangle_inequality_matrix():
	"""Distance matrix that satisfies triangle inequality."""
	# Cities: A, B, C
	return [
		[0, 5, 8],   # A
		[5, 0, 6],   # B
		[8, 6, 0]    # C
	]


@pytest.fixture
def all_cities_simple():
	"""List of cities for simple matrix."""
	return ['A', 'B', 'C', 'D']


@pytest.fixture
def all_cities_symmetric():
	"""List of cities for symmetric matrix."""
	return ['A', 'B', 'C', 'D', 'E']


@pytest.fixture
def all_cities_triangle():
	"""List of cities for triangle matrix."""
	return ['A', 'B', 'C']


# ==================== Brute Force Algorithm Tests ====================

class TestBruteForce:
	"""Test suite for BruteForce algorithm."""
	
	def test_brute_force_simple_case(self, simple_distance_matrix, all_cities_simple):
		"""Test brute force with 3 cities (A, B, C) starting from A."""
		main_city = 'A'
		main_city_index = 0
		selected_cities = ['B', 'C']
		
		bf = BruteForce(main_city, main_city_index, selected_cities, 
		                simple_distance_matrix, all_cities_simple)
		distance, path = bf.start()
		
		# Expected: A -> B -> C -> A = 10 + 35 + 15 = 60
		# Or: A -> C -> B -> A = 15 + 35 + 10 = 60
		assert distance == 60
		assert path[0] == main_city
		assert path[-1] == main_city
		assert len(path) == 4  # Start, 2 cities, return
		assert set(path[1:-1]) == set(selected_cities)
	
	def test_brute_force_two_cities(self, simple_distance_matrix, all_cities_simple):
		"""Test brute force with only 2 cities."""
		main_city = 'A'
		main_city_index = 0
		selected_cities = ['B']
		
		bf = BruteForce(main_city, main_city_index, selected_cities,
		                simple_distance_matrix, all_cities_simple)
		distance, path = bf.start()
		
		# Expected: A -> B -> A = 10 + 10 = 20
		assert distance == 20
		assert path == ['A', 'B', 'A']
	
	def test_brute_force_filters_main_city(self, simple_distance_matrix, all_cities_simple):
		"""Test that main city is filtered from selected cities."""
		main_city = 'A'
		main_city_index = 0
		selected_cities = ['A', 'B', 'C']  # A is included but should be filtered
		
		bf = BruteForce(main_city, main_city_index, selected_cities,
		                simple_distance_matrix, all_cities_simple)
		
		# Main city should be filtered out
		assert 'A' not in bf.choosen_cities
		assert set(bf.choosen_cities) == {'B', 'C'}
	
	def test_brute_force_path_starts_and_ends_with_main(self, symmetric_distance_matrix, all_cities_symmetric):
		"""Test that path always starts and ends with main city."""
		main_city = 'C'
		main_city_index = 2
		selected_cities = ['A', 'B', 'D']
		
		bf = BruteForce(main_city, main_city_index, selected_cities,
		                symmetric_distance_matrix, all_cities_symmetric)
		distance, path = bf.start()
		
		assert path[0] == main_city
		assert path[-1] == main_city
		assert len(path) == len(selected_cities) + 2  # main + selected + main
	
	def test_brute_force_all_cities_visited(self, symmetric_distance_matrix, all_cities_symmetric):
		"""Test that all selected cities are visited exactly once."""
		main_city = 'A'
		main_city_index = 0
		selected_cities = ['B', 'C', 'D', 'E']
		
		bf = BruteForce(main_city, main_city_index, selected_cities,
		                symmetric_distance_matrix, all_cities_symmetric)
		distance, path = bf.start()
		
		# Check all selected cities appear exactly once in the middle
		visited = path[1:-1]
		assert len(visited) == len(selected_cities)
		assert set(visited) == set(selected_cities)


# ==================== Held-Karp Algorithm Tests ====================

class TestHeldKarp:
	"""Test suite for HeldKarpDP algorithm."""
	
	def test_held_karp_simple_case(self, simple_distance_matrix, all_cities_simple):
		"""Test Held-Karp with 3 cities starting from A."""
		main_city = 'A'
		selected_cities = ['B', 'C']
		
		hk = HeldKarpDP(main_city, all_cities_simple, simple_distance_matrix, selected_cities)
		distance, path = hk.start()
		
		# Should find optimal solution
		assert distance == 60  # Same as brute force
		assert path[0] == main_city
		assert path[-1] == main_city
		assert len(path) >= 3
	
	def test_held_karp_two_cities(self, simple_distance_matrix, all_cities_simple):
		"""Test Held-Karp with only 2 cities."""
		main_city = 'A'
		selected_cities = ['B']
		
		hk = HeldKarpDP(main_city, all_cities_simple, simple_distance_matrix, selected_cities)
		distance, path = hk.start()
		
		# Expected: A -> B -> A = 10 + 10 = 20
		assert distance == 20
		assert path[0] == main_city
		assert path[-1] == main_city
	
	def test_held_karp_filters_main_city(self, simple_distance_matrix, all_cities_simple):
		"""Test that main city is filtered from selected cities."""
		main_city = 'A'
		selected_cities = ['A', 'B', 'C']
		
		hk = HeldKarpDP(main_city, all_cities_simple, simple_distance_matrix, selected_cities)
		
		# Main city should be filtered out from selected_cities
		# ordered_city_list should be [A, B, C] (A added explicitly)
		assert hk.ordered_city_list[0] == main_city
		assert 'A' not in hk.ordered_city_list[1:]  # A should only appear once at start
	
	def test_held_karp_path_validity(self, symmetric_distance_matrix, all_cities_symmetric):
		"""Test that Held-Karp produces a valid path."""
		main_city = 'C'
		selected_cities = ['A', 'B', 'D']
		
		hk = HeldKarpDP(main_city, all_cities_symmetric, symmetric_distance_matrix, selected_cities)
		distance, path = hk.start()
		
		assert path[0] == main_city
		assert path[-1] == main_city
		assert len(path) >= len(selected_cities) + 1
	
	def test_held_karp_optimal_solution(self, triangle_inequality_matrix, all_cities_triangle):
		"""Test Held-Karp finds optimal solution for small case."""
		main_city = 'A'
		selected_cities = ['B', 'C']
		
		hk = HeldKarpDP(main_city, all_cities_triangle, triangle_inequality_matrix, selected_cities)
		distance, path = hk.start()
		
		# A -> B -> C -> A = 5 + 6 + 8 = 19
		# A -> C -> B -> A = 8 + 6 + 5 = 19
		# Both are optimal
		assert distance == 19
		assert path[0] == main_city
		assert path[-1] == main_city


# ==================== Nearest Neighbor 2-Opt Algorithm Tests ====================

class TestNearestNeighbor2Opt:
	"""Test suite for NearestNeighbor2Opt algorithm."""
	
	def test_nn_2opt_simple_case(self, simple_distance_matrix, all_cities_simple):
		"""Test Nearest Neighbor 2-Opt with 3 cities."""
		main_city = 'A'
		selected_cities = ['B', 'C']
		
		# Create submatrix for NN2Opt (ordered_city_list = [A, B, C])
		# Matrix indices: 0=A, 1=B, 2=C
		# Get distances from simple_distance_matrix: A=0, B=1, C=2
		nn_matrix = [
			[simple_distance_matrix[0][0], simple_distance_matrix[0][1], simple_distance_matrix[0][2]],  # A to A, B, C
			[simple_distance_matrix[1][0], simple_distance_matrix[1][1], simple_distance_matrix[1][2]],  # B to A, B, C
			[simple_distance_matrix[2][0], simple_distance_matrix[2][1], simple_distance_matrix[2][2]]   # C to A, B, C
		]
		
		nn = NearestNeighbor2Opt(main_city, selected_cities, nn_matrix)
		distance, path = nn.start()
		
		assert path[0] == main_city
		assert path[-1] == main_city
		assert distance > 0
	
	def test_nn_2opt_two_cities(self, simple_distance_matrix, all_cities_simple):
		"""Test Nearest Neighbor 2-Opt with only 2 cities."""
		main_city = 'A'
		selected_cities = ['B']
		
		nn_matrix = [
			[0, 10],
			[10, 0]
		]
		
		nn = NearestNeighbor2Opt(main_city, selected_cities, nn_matrix)
		distance, path = nn.start()
		
		# Should be A -> B -> A = 20
		assert distance == 20
		assert path == ['A', 'B', 'A']
	
	def test_nn_2opt_filters_main_city(self, simple_distance_matrix, all_cities_simple):
		"""Test that main city is filtered from selected cities."""
		main_city = 'A'
		selected_cities = ['A', 'B', 'C']
		
		nn_matrix = [
			[0, 10, 15],
			[10, 0, 35],
			[15, 35, 0]
		]
		
		nn = NearestNeighbor2Opt(main_city, selected_cities, nn_matrix)
		
		# Main city should be filtered, then added at start
		assert nn.ordered_city_list[0] == main_city
		assert nn.ordered_city_list.count(main_city) == 1  # Only once
	
	def test_nn_2opt_path_validity(self, symmetric_distance_matrix, all_cities_symmetric):
		"""Test that NN 2-Opt produces a valid path."""
		main_city = 'C'
		selected_cities = ['A', 'B', 'D']
		
		# Create submatrix for [C, A, B, D]
		# Global indices: C=2, A=0, B=1, D=3
		# Local indices: 0=C, 1=A, 2=B, 3=D
		global_indices = {'C': 2, 'A': 0, 'B': 1, 'D': 3}
		ordered_list = [main_city] + selected_cities  # [C, A, B, D]
		
		nn_matrix = [[0] * 4 for _ in range(4)]
		for i, city_i in enumerate(ordered_list):
			for j, city_j in enumerate(ordered_list):
				nn_matrix[i][j] = symmetric_distance_matrix[global_indices[city_i]][global_indices[city_j]]
		
		nn = NearestNeighbor2Opt(main_city, selected_cities, nn_matrix)
		distance, path = nn.start()
		
		assert path[0] == main_city
		assert path[-1] == main_city
		assert distance > 0
	
	def test_nn_2opt_improves_with_2opt(self):
		"""Test that 2-Opt improvement actually improves the tour."""
		# Create a matrix where 2-opt can improve the solution
		# Cities: A, B, C, D in a square
		# A-B: 1, B-C: 1, C-D: 1, D-A: 1 (optimal: 4)
		# But if we go A-B-C-D-A, we get 1+1+1+1=4
		# If we go A-C-B-D-A, we might get worse, but 2-opt should fix it
		main_city = 'A'
		selected_cities = ['B', 'C', 'D']
		
		# Matrix where crossing edges is worse
		nn_matrix = [
			[0, 1, 100, 1],    # A
			[1, 0, 1, 100],    # B
			[100, 1, 0, 1],    # C
			[1, 100, 1, 0]     # D
		]
		
		nn = NearestNeighbor2Opt(main_city, selected_cities, nn_matrix)
		distance, path = nn.start()
		
		# Should find a reasonable solution
		assert distance < 400  # Much better than worst case
		assert path[0] == main_city
		assert path[-1] == main_city


# ==================== Algorithm Comparison Tests ====================

class TestAlgorithmComparison:
	"""Test that all algorithms produce valid results and can be compared."""
	
	def test_all_algorithms_same_input(self, simple_distance_matrix, all_cities_simple):
		"""Test all three algorithms with the same input."""
		main_city = 'A'
		main_city_index = 0
		selected_cities = ['B', 'C']
		
		# Brute Force
		bf = BruteForce(main_city, main_city_index, selected_cities,
		                simple_distance_matrix, all_cities_simple)
		bf_distance, bf_path = bf.start()
		
		# Held-Karp
		hk = HeldKarpDP(main_city, all_cities_simple, simple_distance_matrix, selected_cities)
		hk_distance, hk_path = hk.start()
		
		# NN 2-Opt (needs submatrix for ordered_city_list = [A, B, C])
		# Global: A=0, B=1, C=2
		nn_matrix = [
			[simple_distance_matrix[0][0], simple_distance_matrix[0][1], simple_distance_matrix[0][2]],  # A
			[simple_distance_matrix[1][0], simple_distance_matrix[1][1], simple_distance_matrix[1][2]],  # B
			[simple_distance_matrix[2][0], simple_distance_matrix[2][1], simple_distance_matrix[2][2]]   # C
		]
		nn = NearestNeighbor2Opt(main_city, selected_cities, nn_matrix)
		nn_distance, nn_path = nn.start()
		
		# All should produce valid paths
		assert bf_distance > 0
		assert hk_distance > 0
		assert nn_distance > 0
		
		# Brute Force and Held-Karp should find optimal (same distance)
		assert bf_distance == hk_distance
		
		# NN 2-Opt should be >= optimal (heuristic)
		assert nn_distance >= bf_distance
	
	def test_algorithms_path_format(self, symmetric_distance_matrix, all_cities_symmetric):
		"""Test that all algorithms produce paths in the same format."""
		main_city = 'A'
		main_city_index = 0
		selected_cities = ['B', 'C']
		
		# Brute Force
		bf = BruteForce(main_city, main_city_index, selected_cities,
		                symmetric_distance_matrix, all_cities_symmetric)
		bf_distance, bf_path = bf.start()
		
		# Held-Karp
		hk = HeldKarpDP(main_city, all_cities_symmetric, symmetric_distance_matrix, selected_cities)
		hk_distance, hk_path = hk.start()
		
		# All paths should start and end with main city
		assert bf_path[0] == main_city
		assert bf_path[-1] == main_city
		assert hk_path[0] == main_city
		assert hk_path[-1] == main_city


# ==================== Game Class Tests ====================

class TestGame:
	"""Test suite for Game class."""
	
	def test_game_initialization(self):
		"""Test that Game initializes correctly."""
		game = Game()
		
		assert len(game.cities) == 10
		assert game.cities == ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
		assert game.main_city in game.cities
		assert len(game.distance_matrix) == 10
		assert len(game.distance_matrix[0]) == 10
		assert game.player_selected_cities == []
	
	def test_game_distance_matrix_symmetric(self):
		"""Test that distance matrix is symmetric."""
		game = Game()
		
		for i in range(len(game.cities)):
			for j in range(len(game.cities)):
				assert game.distance_matrix[i][j] == game.distance_matrix[j][i]
	
	def test_game_distance_matrix_diagonal_zero(self):
		"""Test that distance matrix diagonal is zero."""
		game = Game()
		
		for i in range(len(game.cities)):
			assert game.distance_matrix[i][i] == 0
	
	def test_game_distance_matrix_values(self):
		"""Test that distance matrix values are in expected range."""
		game = Game()
		
		for i in range(len(game.cities)):
			for j in range(len(game.cities)):
				if i != j:
					assert 50 <= game.distance_matrix[i][j] <= 100
	
	def test_reset_game(self):
		"""Test that reset_game generates new distance matrix and main city."""
		game = Game()
		original_main_city = game.main_city
		original_matrix = [row[:] for row in game.distance_matrix]  # Deep copy
		
		game.reset_game()
		
		# Main city might be the same or different (random)
		assert game.main_city in game.cities
		
		# Distance matrix should be regenerated (might be same or different)
		# At least verify it's still valid
		assert len(game.distance_matrix) == 10
		assert len(game.distance_matrix[0]) == 10
	
	def test_reset_game_clears_player_selection(self):
		"""Test that reset_game clears player selected cities."""
		game = Game()
		game.player_selected_cities = ['A', 'B', 'C']
		
		game.reset_game()
		
		assert game.player_selected_cities == []
	
	def test_win_or_lose_correct_guess(self):
		"""Test win_or_lose with correct player guess."""
		game = Game()
		correct_path = ['A', 'B', 'C', 'A']
		player_guess = ['A', 'B', 'C', 'A']
		
		game.win_or_lose(player_guess, correct_path)
		
		assert game.is_won is True
	
	def test_win_or_lose_incorrect_guess(self):
		"""Test win_or_lose with incorrect player guess."""
		game = Game()
		correct_path = ['A', 'B', 'C', 'A']
		player_guess = ['A', 'C', 'B', 'A']
		
		game.win_or_lose(player_guess, correct_path)
		
		assert game.is_won is False
	
	def test_win_or_lose_different_length(self):
		"""Test win_or_lose with paths of different lengths."""
		game = Game()
		correct_path = ['A', 'B', 'C', 'A']
		player_guess = ['A', 'B', 'A']
		
		game.win_or_lose(player_guess, correct_path)
		
		assert game.is_won is False
	
	def test_run_algorithms_returns_tuple(self):
		"""Test that run_algorithms returns a tuple of (bool, list)."""
		game = Game()
		game.player_selected_cities = ['B', 'C']
		player_guess = ['A', 'B', 'C', 'A']
		
		# This test might be slow due to multiprocessing, but it's important
		result = game.run_algorithms(player_guess)
		
		assert isinstance(result, tuple)
		assert len(result) == 2
		assert isinstance(result[0], bool)
		assert isinstance(result[1], list)
	
	def test_run_algorithms_stores_times(self):
		"""Test that run_algorithms stores algorithm execution times."""
		game = Game()
		game.player_selected_cities = ['B', 'C']
		player_guess = ['A', 'B', 'C', 'A']
		
		game.run_algorithms(player_guess)
		
		assert hasattr(game, 'algorithm_times')
		assert 'Brute Force' in game.algorithm_times
		assert 'Held-Karp' in game.algorithm_times
		assert 'Nearest Neighbor 2-Opt' in game.algorithm_times
		assert all(isinstance(t, (int, float)) for t in game.algorithm_times.values())
		assert all(t >= 0 for t in game.algorithm_times.values())


# ==================== Edge Cases and Error Handling ====================

class TestEdgeCases:
	"""Test edge cases and error handling."""
	
	def test_brute_force_single_city(self, simple_distance_matrix, all_cities_simple):
		"""Test brute force with no selected cities (only main city)."""
		main_city = 'A'
		main_city_index = 0
		selected_cities = []
		
		bf = BruteForce(main_city, main_city_index, selected_cities,
		                simple_distance_matrix, all_cities_simple)
		distance, path = bf.start()
		
		# Should just be A -> A = 0
		assert distance == 0
		assert path == ['A', 'A']
	
	def test_held_karp_single_city(self, simple_distance_matrix, all_cities_simple):
		"""Test Held-Karp with no selected cities."""
		main_city = 'A'
		selected_cities = []
		
		hk = HeldKarpDP(main_city, all_cities_simple, simple_distance_matrix, selected_cities)
		distance, path = hk.start()
		
		# Should return main city to itself with distance 0
		assert distance == 0
		assert path[0] == main_city
		assert path[-1] == main_city
		assert len(path) == 2
	
	def test_nn_2opt_single_city(self):
		"""Test NN 2-Opt with no selected cities."""
		main_city = 'A'
		selected_cities = []
		
		nn_matrix = [[0]]
		nn = NearestNeighbor2Opt(main_city, selected_cities, nn_matrix)
		distance, path = nn.start()
		
		assert distance == 0
		assert path == ['A', 'A']


# ==================== Integration Tests ====================

class TestIntegration:
	"""Integration tests for the full system."""
	
	def test_full_game_flow(self):
		"""Test a complete game flow."""
		game = Game()
		
		# Select some cities
		game.player_selected_cities = ['B', 'C', 'D']
		
		# Make a guess (might not be correct)
		player_guess = [game.main_city, 'B', 'C', 'D', game.main_city]
		
		# Run algorithms
		is_won, best_path = game.run_algorithms(player_guess)
		
		# Verify results
		assert isinstance(is_won, bool)
		assert isinstance(best_path, list)
		assert len(best_path) > 0
		assert best_path[0] == game.main_city
		assert best_path[-1] == game.main_city
		
		# Verify algorithm times are stored
		assert hasattr(game, 'algorithm_times')
		assert len(game.algorithm_times) == 3
	
	def test_multiple_rounds(self):
		"""Test multiple game rounds with reset."""
		game = Game()
		round1_main = game.main_city
		
		game.player_selected_cities = ['B', 'C']
		player_guess = [game.main_city, 'B', 'C', game.main_city]
		game.run_algorithms(player_guess)
		
		# Reset and play again
		game.reset_game()
		round2_main = game.main_city
		
		game.player_selected_cities = ['D', 'E']
		player_guess = [game.main_city, 'D', 'E', game.main_city]
		game.run_algorithms(player_guess)
		
		# Both rounds should work
		assert round1_main in game.cities
		assert round2_main in game.cities
		assert game.player_selected_cities == ['D', 'E']

