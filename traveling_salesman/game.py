import random

from .brute_force import BruteForce
from .held_karp import HeldKarpDP
from .nn_2opt import NearestNeighbor2Opt

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

	def win_or_lose(self, player_guess: list[str], correct_path: list[str]) -> None:
		if player_guess == correct_path:
			self.is_won = True
		else:
			self.is_won = False

	def run_algorithms(self) -> None:
		# muti-processing to spin up the algorithms
		brute_force_tsp = BruteForce(self.main_city, self.cities.index(self.main_city), self.player_selected_cities, self.distance_matrix)
		hk_tsp = HeldKarpDP(self.main_city, self.cities, self.distance_matrix, self.player_selected_cities)
		nn_2opt_tsp = NearestNeighbor2Opt(self.main_city, self.player_selected_cities, self.distance_matrix)
		# 2-opt + nearest neighbor

		# player choose city cap
		# min 2
		# max 7
