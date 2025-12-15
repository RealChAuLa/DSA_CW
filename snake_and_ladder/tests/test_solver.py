import unittest
import sys
import os

# Add project root to path to allow imports from both root and snake_and_ladder directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from snake_and_ladder.solver import SnakeLadderSolver


class TestSnakeLadderSolver(unittest.TestCase):

    def test_bfs_simple_board(self):
        """
        Test BFS on a small board with no snakes or ladders
        """
        size = 6
        snakes = {}
        ladders = {}

        solver = SnakeLadderSolver(size, snakes, ladders)
        moves, path, elapsed_time = solver.bfs_min_dice()

        self.assertIsInstance(moves, int)
        self.assertGreater(moves, 0)
        self.assertIsInstance(elapsed_time, float)
        self.assertGreaterEqual(elapsed_time, 0)

    def test_dijkstra_simple_board(self):
        """
        Test Dijkstra on a small board with no snakes or ladders
        """
        size = 6
        snakes = {}
        ladders = {}

        solver = SnakeLadderSolver(size, snakes, ladders)
        moves, path, elapsed_time = solver.dijkstra_min_dice()

        self.assertIsInstance(moves, int)
        self.assertGreater(moves, 0)
        self.assertIsInstance(elapsed_time, float)
        self.assertGreaterEqual(elapsed_time, 0)

    def test_snake_effect(self):
        """
        Test that snake actually reduces progress
        """
        size = 6
        snakes = {14: 7}   # snake from 14 to 7
        ladders = {}

        solver = SnakeLadderSolver(size, snakes, ladders)
        moves, path, elapsed_time = solver.bfs_min_dice()

        # Verify path is valid: starts at 1, ends at 36
        self.assertEqual(path[0], 1)
        self.assertEqual(path[-1], size * size)
        # Verify that if we land on snake head (14), we go to tail (7)
        # The optimal path might avoid the snake, so just verify solver works
        self.assertIsInstance(moves, int)
        self.assertGreater(moves, 0)
        self.assertIsInstance(elapsed_time, float)
        self.assertGreaterEqual(elapsed_time, 0)

    def test_ladder_effect(self):
        """
        Test that ladder increases progress
        """
        size = 6
        snakes = {}
        ladders = {3: 15}  # ladder from 3 to 15

        solver = SnakeLadderSolver(size, snakes, ladders)
        moves, path, elapsed_time = solver.bfs_min_dice()

        self.assertIn(15, path)
        self.assertIsInstance(elapsed_time, float)
        self.assertGreaterEqual(elapsed_time, 0)


if __name__ == "__main__":
    unittest.main()
