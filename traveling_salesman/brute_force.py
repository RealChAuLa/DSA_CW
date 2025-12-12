import itertools

class BruteForce:
	def __init__(self, main_city: str, main_city_index: int, choosen_cities: list[str], distance_matrix: list[list[int]]) -> None:
		self.main_city = main_city
		self.choosen_cities = choosen_cities
		self.distance_matrix = distance_matrix
		self.best_distance = float('inf')
		self.best_route = None

		self.city_to_index: dict[str, int] = {city: i for i, city in enumerate(choosen_cities)}
		self.main_city_index = main_city_index

	def start(self) -> (int, list[str]):
		for perm in itertools.permutations(self.choosen_cities):
			total: int = 0

			# go to first city
			total += self.distance_matrix[self.main_city_index][self.city_to_index[perm[0]]]

			# then visit others in order
			for i in range(len(perm) - 1):
				a = self.city_to_index[perm[i]]
				b = self.city_to_index[perm[i+1]]
				total += self.distance_matrix[a][b]

			# return to main
			total += self.distance_matrix[self.city_to_index[perm[-1]]][self.main_city_index]

			# check if this route is better
			if total < self.best_distance:
				self.best_distance = total
				self.best_route = [self.main_city, *perm, self.main_city]

		return total, self.best_route
