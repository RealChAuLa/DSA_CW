import multiprocessing
import random

from .brute_force import BruteForce
from .held_karp import HeldKarpDP
from .nn_2opt import NearestNeighbor2Opt

# Worker functions for multiprocessing (must be at module level for Windows)
def run_brute_force(args: tuple) -> tuple[int, list[str], float]:
	import time
	main_city, main_city_index, selected_cities, distance_matrix, all_cities = args
	start_time = time.time()
	bf = BruteForce(main_city, main_city_index, selected_cities, distance_matrix, all_cities)
	distance, path = bf.start()
	elapsed = time.time() - start_time
	return distance, path, elapsed

def run_held_karp(args: tuple) -> tuple[int, list[str], float]:
	import time
	main_city, all_cities, distance_matrix, selected_cities = args
	start_time = time.time()
	hk = HeldKarpDP(main_city, all_cities, distance_matrix, selected_cities)
	distance, path = hk.start()
	elapsed = time.time() - start_time
	return distance, path, elapsed

def run_nn_2opt(args: tuple) -> tuple[int, list[str], float]:
	import time
	main_city, selected_cities, distance_matrix = args
	start_time = time.time()
	nn = NearestNeighbor2Opt(main_city, selected_cities, distance_matrix)
	distance, path = nn.start()
	elapsed = time.time() - start_time
	return distance, path, elapsed

class Game:
	def __init__(self) -> None:
		# define cities
		self.cities = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
		n = len(self.cities)

		# define and fill the distance matrix
		self.distance_matrix: list[list[int]] = [[0] * n for _ in range(n)]
		for i in range(n):
			for j in range(i + 1, n):
				distance = random.randint(50, 100)
				self.distance_matrix[i][j] = distance
				self.distance_matrix[j][i] = distance

		# choose main city
		self.main_city: str = random.choice(self.cities)

		# player choosen cities
		self.player_selected_cities = []

	def reset_game(self) -> None:
		n = len(self.cities)
		
		# Generate new distance matrix
		self.distance_matrix: list[list[int]] = [[0] * n for _ in range(n)]
		for i in range(n):
			for j in range(i + 1, n):
				distance = random.randint(50, 100)
				self.distance_matrix[i][j] = distance
				self.distance_matrix[j][i] = distance
		
		# Choose new main city
		self.main_city: str = random.choice(self.cities)
		
		# Reset player selected cities
		self.player_selected_cities = []

	def win_or_lose(self, player_guess: list[str], correct_path: list[str]) -> None:
		if player_guess == correct_path:
			self.is_won = True
		else:
			self.is_won = False

	def run_algorithms(self, player_guess: list[str]) -> tuple[bool, list[str]]:
		# Prepare arguments for each algorithm
		main_city_index = self.cities.index(self.main_city)
		bf_args = (self.main_city, main_city_index, self.player_selected_cities, self.distance_matrix, self.cities)
		hk_args = (self.main_city, self.cities, self.distance_matrix, self.player_selected_cities)
		nn_args = (self.main_city, self.player_selected_cities, self.distance_matrix)

		# Run algorithms in parallel using multiprocessing
		with multiprocessing.Pool(processes=3) as pool:
			bf_result = pool.apply_async(run_brute_force, (bf_args,))
			hk_result = pool.apply_async(run_held_karp, (hk_args,))
			nn_result = pool.apply_async(run_nn_2opt, (nn_args,))

			# Get results
			bf_distance, bf_path, bf_time = bf_result.get()
			hk_distance, hk_path, hk_time = hk_result.get()
			nn_distance, nn_path, nn_time = nn_result.get()
		
		# Store timing information
		self.algorithm_times = {
			"Brute Force": bf_time,
			"Held-Karp": hk_time,
			"Nearest Neighbor 2-Opt": nn_time
		}

		# Compare results and find the best path
		results = [
			(bf_distance, bf_path, "Brute Force"),
			(hk_distance, hk_path, "Held-Karp"),
			(nn_distance, nn_path, "Nearest Neighbor 2-Opt")
		]

		# Find the best result
		best_distance, best_path, best_algorithm = min(results, key=lambda x: x[0])

		# Check if player guess matches the best path
		self.win_or_lose(player_guess, best_path)

		return self.is_won, best_path
