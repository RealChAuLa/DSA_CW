import itertools

class BruteForce:
	def __init__(self, main_city: str, main_city_index: int, choosen_cities: list[str], distance_matrix: list[list[int]], all_cities: list[str]) -> None:
		self.main_city = main_city
		# Filter out main city from choosen_cities to avoid duplicates
		self.choosen_cities = [city for city in choosen_cities if city != main_city]
		self.distance_matrix = distance_matrix
		self.best_distance = float('inf')
		self.best_route = []

		# Map city names to their global indices in the distance matrix
		self.city_to_global_index: dict[str, int] = {city: all_cities.index(city) for city in self.choosen_cities}
		self.city_to_index: dict[str, int] = {city: i for i, city in enumerate(self.choosen_cities)}
		self.main_city_index = main_city_index

	def start(self) -> tuple[int, list[str]]:
		# Edge case: if no cities are selected, return main city to itself
		if len(self.choosen_cities) == 0:
			return 0, [self.main_city, self.main_city]
		
		for perm in itertools.permutations(self.choosen_cities):
			total: int = 0
			# go to first city (use global indices)
			total += self.distance_matrix[self.main_city_index][self.city_to_global_index[perm[0]]]

			# then visit others in order (use global indices for distance matrix)
			for i in range(len(perm) - 1):
				a = self.city_to_global_index[perm[i]]
				b = self.city_to_global_index[perm[i+1]]
				total += self.distance_matrix[a][b]

			# return to main (use global indices)
			total += self.distance_matrix[self.city_to_global_index[perm[-1]]][self.main_city_index]

			# check if this route is better
			if total < self.best_distance:
				self.best_distance = total
				self.best_route = [self.main_city, *perm, self.main_city]

		return self.best_distance, self.best_route
