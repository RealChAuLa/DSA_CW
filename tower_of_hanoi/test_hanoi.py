# Tower of Hanoi - Unit Tests
import sys
import os

# Add parent directory to path for direct execution
if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import sqlite3
import tempfile
from unittest.mock import patch, MagicMock

# Try relative imports first (for pytest), fall back to absolute (for direct execution)
try:
    from . import algorithm
    from .db import Database
except ImportError:
    from tower_of_hanoi import algorithm
    from tower_of_hanoi.db import Database


# 3-Peg Recursive Algorithm Tests
class TestHanoiRecursive3Peg:
    
    def test_zero_disks(self):
        moves = algorithm.hanoi_recursive_3peg(0)
        assert moves == []
    
    def test_one_disk(self):
        moves = algorithm.hanoi_recursive_3peg(1)
        assert moves == [('A', 'C')]
        assert len(moves) == 1
    
    def test_two_disks(self):
        moves = algorithm.hanoi_recursive_3peg(2)
        assert len(moves) == 3
        assert moves == [('A', 'B'), ('A', 'C'), ('B', 'C')]
    
    def test_three_disks(self):
        moves = algorithm.hanoi_recursive_3peg(3)
        assert len(moves) == 7
    
    def test_move_count_formula(self):
        # Verify 2^n - 1 formula
        for n in range(1, 8):
            moves = algorithm.hanoi_recursive_3peg(n)
            expected_moves = (2 ** n) - 1
            assert len(moves) == expected_moves, f"Failed for n={n}"
    
    def test_custom_peg_names(self):
        moves = algorithm.hanoi_recursive_3peg(2, source='X', target='Z', auxiliary='Y')
        assert moves[0][0] == 'X'
        assert moves[-1][1] == 'Z'
    
    def test_negative_disks_raises_error(self):
        with pytest.raises(ValueError):
            algorithm.hanoi_recursive_3peg(-1)
    
    def test_non_integer_raises_error(self):
        with pytest.raises(ValueError):
            algorithm.hanoi_recursive_3peg(2.5)
        with pytest.raises(ValueError):
            algorithm.hanoi_recursive_3peg("three")
    
    def test_valid_moves_sequence(self):
        # Verify no larger disk placed on smaller
        n = 4
        moves = algorithm.hanoi_recursive_3peg(n)
        towers = {'A': list(range(n, 0, -1)), 'B': [], 'C': []}
        
        for frm, to in moves:
            assert len(towers[frm]) > 0, "Cannot move from empty tower"
            disk = towers[frm].pop()
            if towers[to]:
                assert disk < towers[to][-1], "Cannot place larger disk on smaller"
            towers[to].append(disk)
        
        assert towers['C'] == list(range(n, 0, -1))
        assert towers['A'] == []
        assert towers['B'] == []


# 3-Peg Iterative Algorithm Tests
class TestHanoiIterative3Peg:
    
    def test_zero_disks(self):
        moves = algorithm.hanoi_iterative_3peg(0)
        assert moves == []
    
    def test_one_disk(self):
        moves = algorithm.hanoi_iterative_3peg(1)
        assert len(moves) == 1
    
    def test_move_count_formula(self):
        for n in range(1, 8):
            moves = algorithm.hanoi_iterative_3peg(n)
            expected_moves = (2 ** n) - 1
            assert len(moves) == expected_moves, f"Failed for n={n}"
    
    def test_matches_recursive_move_count(self):
        for n in range(1, 6):
            recursive_moves = algorithm.hanoi_recursive_3peg(n)
            iterative_moves = algorithm.hanoi_iterative_3peg(n)
            assert len(recursive_moves) == len(iterative_moves)
    
    def test_negative_disks_raises_error(self):
        with pytest.raises(ValueError):
            algorithm.hanoi_iterative_3peg(-1)
    
    def test_non_integer_raises_error(self):
        with pytest.raises(ValueError):
            algorithm.hanoi_iterative_3peg(3.14)
    
    def test_valid_moves_sequence(self):
        n = 4
        moves = algorithm.hanoi_iterative_3peg(n)
        towers = {'A': list(range(n, 0, -1)), 'B': [], 'C': []}
        
        for frm, to in moves:
            assert len(towers[frm]) > 0, "Cannot move from empty tower"
            disk = towers[frm].pop()
            if towers[to]:
                assert disk < towers[to][-1], "Cannot place larger disk on smaller"
            towers[to].append(disk)
        
        assert towers['C'] == list(range(n, 0, -1))


# 4-Peg Frame-Stewart Algorithm Tests
class TestHanoiFrameStewart:
    
    def test_zero_disks(self):
        moves = algorithm.hanoi_frame_stewart(0)
        assert moves == []
    
    def test_one_disk(self):
        moves = algorithm.hanoi_frame_stewart(1)
        assert len(moves) == 1
        assert moves == [('A', 'D')]
    
    def test_two_disks(self):
        moves = algorithm.hanoi_frame_stewart(2)
        assert len(moves) >= 1
    
    def test_negative_disks_raises_error(self):
        with pytest.raises(ValueError):
            algorithm.hanoi_frame_stewart(-1)
    
    def test_non_integer_raises_error(self):
        with pytest.raises(ValueError):
            algorithm.hanoi_frame_stewart(2.5)
    
    def test_fewer_moves_than_3peg(self):
        # 4-peg should use fewer moves than 3-peg for n > 2
        for n in range(3, 8):
            three_peg_moves = len(algorithm.hanoi_recursive_3peg(n))
            four_peg_moves = len(algorithm.hanoi_frame_stewart(n))
            assert four_peg_moves <= three_peg_moves, f"4-peg should be <= 3-peg for n={n}"
    
    def test_valid_moves_sequence(self):
        n = 5
        moves = algorithm.hanoi_frame_stewart(n)
        towers = {'A': list(range(n, 0, -1)), 'B': [], 'C': [], 'D': []}
        
        for frm, to in moves:
            assert len(towers[frm]) > 0, f"Cannot move from empty tower {frm}"
            disk = towers[frm].pop()
            if towers[to]:
                assert disk < towers[to][-1], f"Cannot place disk {disk} on {towers[to][-1]}"
            towers[to].append(disk)
        
        assert towers['D'] == list(range(n, 0, -1))
        assert towers['A'] == []
    
    def test_custom_peg_names(self):
        moves = algorithm.hanoi_frame_stewart(2, source='W', target='Z', aux1='X', aux2='Y')
        assert moves[0][0] == 'W'
        assert moves[-1][1] == 'Z'


# Database Tests
class TestDatabase:
    
    @pytest.fixture
    def temp_db(self):
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        with patch.object(sqlite3, 'connect', return_value=sqlite3.connect(path)):
            db = Database()
            yield db
            db.conn.close()
        
        os.unlink(path)
    
    @pytest.fixture
    def in_memory_db(self):
        with patch.object(sqlite3, 'connect', return_value=sqlite3.connect(':memory:')):
            db = Database()
            yield db
            db.conn.close()
    
    def test_database_initialization(self, in_memory_db):
        cursor = in_memory_db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in cursor.fetchall()]
        assert 'tower_of_hanoi' in tables
        assert 'toh_algo_perf' in tables
        assert 'toh_winners' in tables
    
    def test_save_game(self, in_memory_db):
        in_memory_db.save_game(
            player='TestPlayer', disks=3, pegs=3, moves=7, min_moves=7,
            predicted_moves=7, correct=True, algo='recursive', time_ms=100.5
        )
        
        history = in_memory_db.get_history(limit=1)
        assert len(history) == 1
        assert history[0][1] == 'TestPlayer'
        assert history[0][2] == 3
    
    def test_save_winner(self, in_memory_db):
        in_memory_db.save_winner(
            player='Winner', disks=4, pegs=3, moves=15, min_moves=15,
            predicted_moves=15, algo='iterative', time_ms=200.0
        )
        
        winners = in_memory_db.get_winners(limit=1)
        assert len(winners) == 1
        assert winners[0][1] == 'Winner'
    
    def test_save_algo_perf(self, in_memory_db):
        in_memory_db.save_algo_perf(algo='recursive', disks=5, pegs=3, moves=31, time_ms=50.0)
        stats = in_memory_db.get_algo_stats(pegs=3)
        assert len(stats) >= 1
    
    def test_get_history_empty(self, in_memory_db):
        history = in_memory_db.get_history()
        assert history == []
    
    def test_get_leaderboard(self, in_memory_db):
        in_memory_db.save_game('Player1', 3, 3, 7, 7, 7, True, 'rec', 100)
        in_memory_db.save_game('Player1', 4, 3, 15, 15, 15, True, 'rec', 150)
        in_memory_db.save_game('Player2', 3, 3, 10, 7, 7, False, 'rec', 120)
        
        leaderboard = in_memory_db.get_leaderboard()
        assert len(leaderboard) >= 1
    
    def test_get_comparison_data_empty(self, in_memory_db):
        # No data should return empty list
        comparison = in_memory_db.get_comparison_data()
        assert comparison == []
    
    def test_get_comparison_data_with_matching_disks(self, in_memory_db):
        # Add 3-peg and 4-peg performance for same disk count
        in_memory_db.save_algo_perf('recursive_3peg', 5, 3, 31, 10.0)
        in_memory_db.save_algo_perf('frame_stewart', 5, 4, 13, 5.0)
        
        comparison = in_memory_db.get_comparison_data()
        assert len(comparison) == 1
        assert comparison[0][0] == 5  # disks
        assert comparison[0][1] == 31  # 3-peg moves
        assert comparison[0][2] == 13  # 4-peg moves
    
    def test_get_comparison_data_no_match(self, in_memory_db):
        # Different disk counts should not match
        in_memory_db.save_algo_perf('recursive_3peg', 3, 3, 7, 5.0)
        in_memory_db.save_algo_perf('frame_stewart', 5, 4, 13, 5.0)
        
        comparison = in_memory_db.get_comparison_data()
        assert comparison == []
    
    def test_get_comparison_data_multiple_entries(self, in_memory_db):
        # Multiple matching disk counts
        in_memory_db.save_algo_perf('recursive_3peg', 4, 3, 15, 8.0)
        in_memory_db.save_algo_perf('frame_stewart', 4, 4, 9, 4.0)
        in_memory_db.save_algo_perf('recursive_3peg', 6, 3, 63, 20.0)
        in_memory_db.save_algo_perf('frame_stewart', 6, 4, 17, 8.0)
        
        comparison = in_memory_db.get_comparison_data()
        assert len(comparison) == 2
        # Should be ordered by disks
        assert comparison[0][0] == 4
        assert comparison[1][0] == 6
    
    def test_get_all_played_games_for_comparison_empty(self, in_memory_db):
        games = in_memory_db.get_all_played_games_for_comparison()
        assert games == []
    
    def test_get_all_played_games_for_comparison(self, in_memory_db):
        in_memory_db.save_algo_perf('recursive_3peg', 5, 3, 31, 10.0)
        in_memory_db.save_algo_perf('iterative_3peg', 5, 3, 31, 12.0)
        in_memory_db.save_algo_perf('frame_stewart', 5, 4, 13, 5.0)
        
        games = in_memory_db.get_all_played_games_for_comparison()
        assert len(games) == 3
        # Verify structure: (disks, pegs, algorithm, moves, time_ms)
        for game in games:
            assert len(game) == 5


# Integration Tests
class TestIntegration:
    
    def test_recursive_and_iterative_same_final_state(self):
        n = 5
        
        rec_moves = algorithm.hanoi_recursive_3peg(n)
        towers_rec = {'A': list(range(n, 0, -1)), 'B': [], 'C': []}
        for frm, to in rec_moves:
            towers_rec[to].append(towers_rec[frm].pop())
        
        iter_moves = algorithm.hanoi_iterative_3peg(n)
        towers_iter = {'A': list(range(n, 0, -1)), 'B': [], 'C': []}
        for frm, to in iter_moves:
            towers_iter[to].append(towers_iter[frm].pop())
        
        assert towers_rec['C'] == towers_iter['C']
        assert towers_rec['C'] == list(range(n, 0, -1))
    
    def test_all_algorithms_complete_puzzle(self):
        n = 4
        
        moves_3r = algorithm.hanoi_recursive_3peg(n)
        assert self._verify_solution(n, moves_3r, 'C', 3)
        
        moves_3i = algorithm.hanoi_iterative_3peg(n)
        assert self._verify_solution(n, moves_3i, 'C', 3)
        
        moves_4 = algorithm.hanoi_frame_stewart(n)
        assert self._verify_solution(n, moves_4, 'D', 4)
    
    def _verify_solution(self, n, moves, target, num_pegs):
        peg_names = ['A', 'B', 'C', 'D'][:num_pegs]
        towers = {p: [] for p in peg_names}
        towers['A'] = list(range(n, 0, -1))
        
        for frm, to in moves:
            if not towers[frm]:
                return False
            disk = towers[frm].pop()
            if towers[to] and disk > towers[to][-1]:
                return False
            towers[to].append(disk)
        
        return towers[target] == list(range(n, 0, -1))


# Performance Tests
class TestPerformance:
    
    def test_algorithm_time_bounds(self):
        import time
        
        n = 10
        
        start = time.time()
        algorithm.hanoi_recursive_3peg(n)
        recursive_time = time.time() - start
        
        start = time.time()
        algorithm.hanoi_iterative_3peg(n)
        iterative_time = time.time() - start
        
        assert recursive_time < 1.0
        assert iterative_time < 1.0
    
    def test_frame_stewart_efficiency(self):
        n = 10
        
        three_peg_count = len(algorithm.hanoi_recursive_3peg(n))
        four_peg_count = len(algorithm.hanoi_frame_stewart(n))
        
        assert four_peg_count < three_peg_count
        efficiency_ratio = four_peg_count / three_peg_count
        assert efficiency_ratio < 0.5


# Edge Cases
class TestEdgeCases:
    
    def test_large_disk_count(self):
        n = 12
        moves = algorithm.hanoi_recursive_3peg(n)
        assert len(moves) == (2 ** n) - 1
    
    def test_single_move_consistency(self):
        assert len(algorithm.hanoi_recursive_3peg(1)) == 1
        assert len(algorithm.hanoi_iterative_3peg(1)) == 1
        assert len(algorithm.hanoi_frame_stewart(1)) == 1
    
    def test_moves_are_tuples(self):
        for func in [algorithm.hanoi_recursive_3peg, 
                     algorithm.hanoi_iterative_3peg, 
                     algorithm.hanoi_frame_stewart]:
            moves = func(3)
            for move in moves:
                assert isinstance(move, tuple)
                assert len(move) == 2
    
    def test_move_pegs_are_strings(self):
        moves = algorithm.hanoi_recursive_3peg(3)
        for frm, to in moves:
            assert isinstance(frm, str)
            assert isinstance(to, str)
    
    def test_no_self_moves(self):
        for func in [algorithm.hanoi_recursive_3peg, 
                     algorithm.hanoi_iterative_3peg, 
                     algorithm.hanoi_frame_stewart]:
            moves = func(4)
            for frm, to in moves:
                assert frm != to, f"Self-move detected: {frm} -> {to}"


# Parametrized Tests
class TestParametrized:
    
    @pytest.mark.parametrize("n,expected_moves", [
        (1, 1), (2, 3), (3, 7), (4, 15), (5, 31), (6, 63),
    ])
    def test_recursive_move_counts(self, n, expected_moves):
        moves = algorithm.hanoi_recursive_3peg(n)
        assert len(moves) == expected_moves
    
    @pytest.mark.parametrize("n,expected_moves", [
        (1, 1), (2, 3), (3, 7), (4, 15), (5, 31),
    ])
    def test_iterative_move_counts(self, n, expected_moves):
        moves = algorithm.hanoi_iterative_3peg(n)
        assert len(moves) == expected_moves
    
    @pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6, 7, 8])
    def test_solution_validity(self, n):
        moves = algorithm.hanoi_recursive_3peg(n)
        towers = {'A': list(range(n, 0, -1)), 'B': [], 'C': []}
        
        for frm, to in moves:
            disk = towers[frm].pop()
            if towers[to]:
                assert disk < towers[to][-1]
            towers[to].append(disk)
        
        assert towers['C'] == list(range(n, 0, -1))


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
