class NearestNeighbor2Opt:
	def __init__(self, main_city: str, selected_cities_list: list[str], distance_matrix: list[list[int]]):
		self.ordered_city_list = [main_city] + selected_cities_list
		self.dist = distance_matrix
		self.n = len(self.ordered_city_list)

	# Nearest Neighbor Heuristic
	def nearest_neighbor(self) -> list[int]:
		n = self.n
		visited = [False] * n
		tour = [0]  # always start at main city
		visited[0] = True

		current = 0
		for _ in range(n - 1):
			next_city = None
			next_dist = float("inf")

			for j in range(n):
				if not visited[j] and self.dist[current][j] < next_dist:
					next_dist = self.dist[current][j]
					next_city = j

			if next_city is None:
				raise RuntimeError("No reachable next city. Check distance matrix")

			tour.append(next_city)
			visited[next_city] = True
			current = next_city

		tour.append(0)  # return to start
		return tour

		# Compute Tour Cost
	def compute_cost(self, tour: list[int]) -> int:
		cost = 0
		for i in range(len(tour) - 1):
			cost += self.dist[tour[i]][tour[i + 1]]
		return cost

	# 2-Opt Improvement
	def two_opt(self, tour: list[int]) -> list[int]:
		improved = True
		n = len(tour)

		while improved:
			improved = False
			for i in range(1, n - 2):
				for j in range(i + 1, n - 1):
					# Swap edges: (i-1,i) + (j,j+1) → (i-1,j) + (i,j+1)
					old = (
						self.dist[tour[i - 1]][tour[i]]
						+ self.dist[tour[j]][tour[j + 1]]
					)
					new = (
						self.dist[tour[i - 1]][tour[j]]
						+ self.dist[tour[i]][tour[j + 1]]
					)

					if new < old:
						tour[i : j + 1] = reversed(tour[i : j + 1])
						improved = True
		return tour

	def start(self) -> tuple[int, list[str]]:
		nn_tour = self.nearest_neighbor()
		improved_tour = self.two_opt(nn_tour)
		cost = self.compute_cost(improved_tour)

		str_tour = [self.ordered_city_list[i] for i in improved_tour]
		return cost, str_tour
