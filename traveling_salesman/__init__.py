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


from .game import Game
from .ui import draw_ui, show_win, show_lose

def launch_game() -> None:
	game = Game()
	draw_ui(game)

	is_algorithms_complete_running: bool = False

	# run algoritms
	correct_path: list[str] = []

	if is_algorithms_complete_running:
		if game.is_won:
			show_win()
		else:
			correct_path_str = " -> ".join(correct_path)
			show_lose(correct_path_str)
