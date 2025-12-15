class HeldKarpDP:
	def __init__(self, main_city: str, all_cities: list[str], distance_matrix: list[list[int]], selected_cities: list[str]) -> None:
		# Filter out main city from selected_cities to avoid duplicates
		selected_cities = [city for city in selected_cities if city != main_city]
		# create new list with main city first and selected cities
		self.ordered_city_list = [main_city] + selected_cities
		# city name -> index in global matrix
		global_indices = {city: i for i, city in enumerate(all_cities)}

		n = len(self.ordered_city_list)

		# create new matrix for hk
		self.hk_matrix = [[0] * n for _ in range(n)]

		# fill new matrix using distance matrix
		for i in range(n):
			for j in range(n):
				city_i = self.ordered_city_list[i]
				city_j = self.ordered_city_list[j]

				self.hk_matrix[i][j] = distance_matrix[global_indices[city_i]][global_indices[city_j]]


	def start(self) -> tuple[int, list[str]]:
		n = len(self.hk_matrix)
		
		# Edge case: if only main city (n=1), return main city to itself
		if n == 1:
			return 0, [self.ordered_city_list[0], self.ordered_city_list[0]]
		
		# Number of subsets: 2^n
		N = 1 << n
		INF = float('inf')

		# dp[mask][j] = minimum cost to reach subset 'mask' and end at node j
		dp = [[INF] * n for _ in range(N)]
		# parent[mask][j] = previous node before j in optimal path for (mask, j)
		parent: list[list[int | None]] = [[None] * n for _ in range(N)]

		# Base case: start at node 0, mask = 1<<0
		dp[1][0] = 0

		# Iterate over all subsets that include node 0
		for mask in range(1, N):
			if not (mask & 1):
				continue  # we always require the tour to start at node 0

			for j in range(1, n):
				if not (mask & (1 << j)):
					continue  # j not in subset

				prev_mask = mask ^ (1 << j)
				# Try all possibilities of coming to j from some k in prev_mask
				for k in range(n):
					if prev_mask & (1 << k):
						cost = dp[prev_mask][k] + self.hk_matrix[k][j]
						if cost < dp[mask][j]:
							dp[mask][j] = cost
							parent[mask][j] = k

		# Close the tour: return to node 0
		full_mask = (1 << n) - 1
		min_cost = INF
		last = None
		for j in range(1, n):
			cost = dp[full_mask][j] + self.hk_matrix[j][0]
			if cost < min_cost:
				min_cost = cost
				last = j

		# Reconstruct path
		path = []
		mask = full_mask
		curr = last
		while curr is not None:
			path.append(curr)
			prev = parent[mask][curr]
			mask ^= (1 << curr) # ^ - xor operator
			curr = prev
		# Path now contains [last, ..., 0] in reverse order (ends with 0)
		path.reverse()  # Now it's [0, ..., last]
		# Remove duplicate 0 at start if present (shouldn't happen but safety check)
		if len(path) > 0 and path[0] == 0 and len(path) > 1 and path[1] == 0:
			path = path[1:]
		# Add return to start (path ends with last, not 0, so we need to add 0)
		if len(path) == 0 or path[-1] != 0:
			path.append(0)

		final_path: list[str] = [self.ordered_city_list[i] for i in path]

		return int(min_cost), final_path
