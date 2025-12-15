"""
Snake and Ladder Solver Module
Implements BFS and Dijkstra algorithms to find minimum dice throws
"""
import heapq
import time
from typing import Tuple


class SnakeLadderSolver:
    """
    Solver for finding minimum dice throws in Snake and Ladder game.
    
    Uses BFS and Dijkstra algorithms to find the optimal path from
    position 1 to the final position (N*N).
    """

    def __init__(self, size: int, snakes: dict, ladders: dict):
        """
        Initialize the solver.
        
        :param size: Board size (N x N)
        :param snakes: Dictionary mapping snake head to tail position
        :param ladders: Dictionary mapping ladder bottom to top position
        """
        self.N = size
        self.total_cells = size * size
        self.snakes = snakes
        self.ladders = ladders

    # ------------------------------------------------------------------------
    # BOARD TRANSFORMATION
    # ------------------------------------------------------------------------
    def get_next_position(self, pos: int) -> int:
        """
        Return final position after applying snake or ladder.
        
        :param pos: Current position
        :return: Final position after snake/ladder transformation
        """
        if pos in self.ladders:
            return self.ladders[pos]
        if pos in self.snakes:
            return self.snakes[pos]
        return pos

    # ------------------------------------------------------------------------
    # BFS ALGORITHM
    # ------------------------------------------------------------------------
    def bfs_min_dice(self) -> Tuple[int, list, float]:
        """
        Find minimum dice throws using Breadth-First Search.
        
        BFS is optimal for unweighted graphs where each move costs the same.
        
        :return: Tuple of (minimum_moves, path, elapsed_time_microseconds)
        """
        start_time = time.perf_counter()

        visited = [False] * (self.total_cells + 1)
        parent = {}  # Track path for reconstruction
        queue = [(1, 0)]  # (cell, distance)

        visited[1] = True
        parent[1] = None

        while queue:
            cell, dist = queue.pop(0)

            # Check if reached the end
            if cell == self.total_cells:
                elapsed_seconds = time.perf_counter() - start_time
                elapsed_microseconds = elapsed_seconds * 1_000_000  # Convert to microseconds
                path = self._reconstruct_path(parent, cell)
                return dist, path, elapsed_microseconds

            # Try all possible dice rolls (1-6)
            for dice in range(1, 7):
                next_pos = cell + dice
                if next_pos <= self.total_cells:
                    next_pos = self.get_next_position(next_pos)

                    if not visited[next_pos]:
                        visited[next_pos] = True
                        parent[next_pos] = cell
                        queue.append((next_pos, dist + 1))

        # Should never happen if board is solvable
        return -1, [], 0.0

    # ------------------------------------------------------------------------
    # DIJKSTRA ALGORITHM
    # ------------------------------------------------------------------------
    def dijkstra_min_dice(self) -> Tuple[int, list, float]:
        """
        Find minimum dice throws using Dijkstra's algorithm.
        
        Dijkstra works for weighted graphs, though in this case
        all moves have equal weight (1).
        
        :return: Tuple of (minimum_moves, path, elapsed_time_microseconds)
        """
        start_time = time.perf_counter()

        dist = {i: float("inf") for i in range(1, self.total_cells + 1)}
        dist[1] = 0
        parent = {}  # Track path for reconstruction
        parent[1] = None

        priority_queue = [(0, 1)]  # (cost, cell)

        while priority_queue:
            moves, cell = heapq.heappop(priority_queue)

            # Check if reached the end
            if cell == self.total_cells:
                elapsed_seconds = time.perf_counter() - start_time
                elapsed_microseconds = elapsed_seconds * 1_000_000  # Convert to microseconds
                path = self._reconstruct_path(parent, cell)
                return moves, path, elapsed_microseconds

            # Explore all possible dice outcomes
            for dice in range(1, 7):
                next_pos = cell + dice
                if next_pos <= self.total_cells:
                    next_pos = self.get_next_position(next_pos)

                    new_cost = moves + 1

                    if new_cost < dist[next_pos]:
                        dist[next_pos] = new_cost
                        parent[next_pos] = cell
                        heapq.heappush(priority_queue, (new_cost, next_pos))

        # Should never happen if board is solvable
        return -1, [], 0.0

    # ------------------------------------------------------------------------
    # PATH RECONSTRUCTION
    # ------------------------------------------------------------------------
    def _reconstruct_path(self, parent: dict, end_cell: int) -> list:
        """
        Reconstruct the path from start to end using parent dictionary.
        
        :param parent: Dictionary mapping cell to its parent cell
        :param end_cell: Final cell position
        :return: List of cells representing the path
        """
        path = []
        current = end_cell
        while current is not None:
            path.append(current)
            current = parent.get(current)
        path.reverse()
        return path
