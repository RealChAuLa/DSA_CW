"""
Traveling Salesman Problem Game Module

This package includes:
- Distance matrix generation
- Recursive and iterative algorithm implementations
- User-selected city handling
- User interface logic
- Database operations
- Unit tests

Developed as part of the PDSA coursework.
"""


import random
from brute_force import BruteForce

# define cities
cities = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
n = len(cities)

# define and fill the distance matrix
distance_matrix: list[list[int]] = [[0] * n for _ in range(n)]
for i in range(n):
	for j in range(i + 1, n):
		distance = random.randint(50, 100)
		distance_matrix[i][j] = distance
		distance_matrix[j][i] = distance

# choose main city
main_city: str = random.choice(cities)

# player choosen cities
player_selected_cities = []

# muti-processing to spin up the algorithms
# brute force algorithm
brute_force_tsp = BruteForce(main_city, player_selected_cities, distance_matrix)
# held-karp dynamic programming
# 2-opt + nearest neighbor

# player choose city cap
# min 2
# max 7
# else my laptop will die
