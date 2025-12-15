"""
Comprehensive Unit Tests for Traffic Flow Master Game
Tests all modules: database.py, graph.py, max_flow_algorithms.py, utils.py

Run with: pytest test_all.py -v
"""

import pytest
import sqlite3
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Import modules to test
import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import (
    init_db, clear_db, validate_player_name, validate_answer,
    insert_correct_result, insert_all_result, DatabaseError
)
from graph import (
    NODES, EDGES, generate_edge_caps, generate_capacity_matrix,
    new_random_graph
)
from max_flow_algorithms import (
    SimpleQueue, edmonds_karp, ford_fulkerson
)
from utils import validate_int, time_function


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    original_db = os.path.join(os.path.dirname(__file__), "traffic_simulations.db")
    temp_db_name = "test_traffic_simulations.db"
    
    # Backup original if it exists
    if os.path.exists(original_db):
        shutil.copy(original_db, f"{original_db}.backup")
    
    # Use temp database
    with patch('database.sqlite3.connect') as mock_connect:
        conn = sqlite3.connect(temp_db_name)
        mock_connect.return_value = conn
        yield temp_db_name
        conn.close()
    
    # Cleanup
    if os.path.exists(temp_db_name):
        os.remove(temp_db_name)
    
    # Restore backup if exists
    if os.path.exists(f"{original_db}.backup"):
        shutil.move(f"{original_db}.backup", original_db)


@pytest.fixture
def sample_graph():
    """Provide a sample graph for testing"""
    nodes = ["A", "B", "C", "D"]
    edges = [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")]
    edge_caps = {
        ("A", "B"): 10,
        ("A", "C"): 5,
        ("B", "D"): 8,
        ("C", "D"): 7
    }
    capacity_matrix = [
        [0, 10, 5, 0],   # A
        [0, 0, 0, 8],    # B
        [0, 0, 0, 7],    # C
        [0, 0, 0, 0]     # D
    ]
    return nodes, edges, edge_caps, capacity_matrix


@pytest.fixture
def simple_network():
    """Provide a simple flow network for testing"""
    # Simple network: A -> B -> C with capacities
    capacity_matrix = [
        [0, 10, 0],  # A
        [0, 0, 15],  # B
        [0, 0, 0]    # C
    ]
    return capacity_matrix


# ============================================================================
# DATABASE TESTS (database.py)
# ============================================================================

class TestDatabase:
    """Test suite for database.py module"""
    
    def test_validate_player_name_valid(self):
        """Test valid player names"""
        valid_names = [
            "Alice",
            "Bob123",
            "John_Doe",
            "Player-1",
            "Test User",
            "AB"  # minimum length
        ]
        
        for name in valid_names:
            is_valid, error_msg = validate_player_name(name)
            assert is_valid == True, f"Expected {name} to be valid"
            assert error_msg == ""
    
    def test_validate_player_name_invalid(self):
        """Test invalid player names"""
        invalid_cases = [
            ("", "Player name cannot be empty"),
            ("A", "Player name must be at least 2 characters"),
            ("a" * 51, "Player name cannot exceed 50 characters"),
            ("Player@#$", "Player name contains invalid characters"),
            ("Test<script>", "Player name contains invalid characters"),
            (None, "Player name cannot be empty"),
            (123, "Player name must be a string"),
        ]
        
        for name, expected_error_substring in invalid_cases:
            is_valid, error_msg = validate_player_name(name)
            assert is_valid == False, f"Expected {name} to be invalid"
            assert expected_error_substring in error_msg or error_msg != ""
    
    def test_validate_player_name_whitespace(self):
        """Test player names with whitespace"""
        is_valid, _ = validate_player_name("  Alice  ")
        assert is_valid == True
        
        is_valid, _ = validate_player_name("   ")
        assert is_valid == False
    
    def test_validate_answer_valid(self):
        """Test valid answers"""
        valid_answers = [0, 1, 10, 100, 1000, "42", "0"]
        
        for answer in valid_answers:
            is_valid, error_msg = validate_answer(answer)
            assert is_valid == True, f"Expected {answer} to be valid"
            assert error_msg == ""
    
    def test_validate_answer_invalid(self):
        """Test invalid answers"""
        invalid_answers = [
            (None, "Answer cannot be None"),
            (-1, "Answer must be a non-negative integer"),
            (-100, "Answer must be a non-negative integer"),
            ("abc", "Answer must be a valid integer"),
            ("12.5", "Answer must be a valid integer"),
            ([], "Answer must be a valid integer"),
            ({}, "Answer must be a valid integer"),
        ]
        
        for answer, expected_error_substring in invalid_answers:
            is_valid, error_msg = validate_answer(answer)
            assert is_valid == False, f"Expected {answer} to be invalid"
            assert expected_error_substring in error_msg
    
    def test_init_db_creates_table(self):
        """Test database initialization creates table"""
        from database import DB_PATH
        
        init_db()
        
        # Verify table exists
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check win_results table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='win_results'
        """)
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == 'win_results'
        # Check all_game_results table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='all_game_results'
        """)
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == 'all_game_results'
        
        conn.close()
    
    def test_insert_correct_result_valid(self):
        """Test inserting valid correct results"""
        from database import DB_PATH
        
        init_db()
        clear_db()
        
        # Insert valid result
        success, message = insert_correct_result(
            "TestPlayer",
            42,
            42,
            0.001,
            0.002
        )
        
        assert success == True
        assert "success" in message.lower()
        
        # Verify insertion
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM win_results")
        rows = cursor.fetchall()
        conn.close()
        
        assert len(rows) == 1
        assert rows[0][1] == "TestPlayer"
        assert rows[0][2] == 42
        assert rows[0][3] == 42
    
    def test_insert_correct_result_invalid_name(self):
        """Test inserting result with invalid player name"""
        success, message = insert_correct_result(
            "",  # Invalid empty name
            42,
            42,
            0.001,
            0.002
        )
        
        assert success == False
        assert "name" in message.lower()
    
    def test_insert_correct_result_invalid_answer(self):
        """Test inserting result with invalid answer"""
        success, message = insert_correct_result(
            "ValidPlayer",
            -1,  # Negative answer
            -1,
            0.001,
            0.002
        )
        
        assert success == False
        assert "answer" in message.lower() or "negative" in message.lower()
    
    def test_insert_correct_result_invalid_times(self):
        """Test inserting result with invalid execution times"""
        success, message = insert_correct_result(
            "ValidPlayer",
            42,
            42,
            -0.001,  # Negative time
            0.002
        )
        
        assert success == False
        assert "time" in message.lower() or "negative" in message.lower()
    
    def test_insert_correct_result_sanitizes_input(self):
        """Test that player name is sanitized"""
        from database import DB_PATH
        
        init_db()
        clear_db()
        
        # Insert with whitespace
        success, _ = insert_correct_result(
            "  TestPlayer  ",
            42,
            42,
            0.001,
            0.002
        )
        
        assert success == True
        
        # Verify trimmed
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT player_name FROM win_results")
        name = cursor.fetchone()[0]
        conn.close()
        
        assert name == "TestPlayer"


# ============================================================================
# GRAPH TESTS (graph.py)
# ============================================================================

class TestGraph:
    """Test suite for graph.py module"""
    
    def test_nodes_list_exists(self):
        """Test that NODES list is defined and non-empty"""
        assert NODES is not None
        assert len(NODES) > 0
        assert "A" in NODES
        assert "T" in NODES
    
    def test_nodes_list_correct_size(self):
        """Test NODES has expected size"""
        assert len(NODES) == 9
    
    def test_edges_list_exists(self):
        """Test that EDGES list is defined and non-empty"""
        assert EDGES is not None
        assert len(EDGES) > 0
    
    def test_edges_list_correct_size(self):
        """Test EDGES has expected size"""
        assert len(EDGES) == 13
    
    def test_edges_are_tuples(self):
        """Test that all edges are tuples"""
        for edge in EDGES:
            assert isinstance(edge, tuple)
            assert len(edge) == 2
    
    def test_edges_nodes_exist(self):
        """Test that all nodes in edges exist in NODES"""
        for u, v in EDGES:
            assert u in NODES, f"Node {u} not in NODES"
            assert v in NODES, f"Node {v} not in NODES"
    
    def test_generate_edge_caps_returns_dict(self):
        """Test generate_edge_caps returns a dictionary"""
        edge_caps = generate_edge_caps()
        assert isinstance(edge_caps, dict)
    
    def test_generate_edge_caps_correct_keys(self):
        """Test edge_caps has correct keys"""
        edge_caps = generate_edge_caps()
        assert len(edge_caps) == len(EDGES)
        
        for edge in EDGES:
            assert edge in edge_caps
    
    def test_generate_edge_caps_values_in_range(self):
        """Test edge capacities are within specified range"""
        min_cap, max_cap = 5, 15
        edge_caps = generate_edge_caps(min_cap, max_cap)
        
        for cap in edge_caps.values():
            assert min_cap <= cap <= max_cap
            assert isinstance(cap, int)
    
    def test_generate_edge_caps_custom_range(self):
        """Test generate_edge_caps with custom range"""
        min_cap, max_cap = 10, 20
        edge_caps = generate_edge_caps(min_cap, max_cap)
        
        for cap in edge_caps.values():
            assert min_cap <= cap <= max_cap
    
    def test_generate_capacity_matrix_shape(self):
        """Test capacity matrix has correct shape"""
        edge_caps = generate_edge_caps()
        matrix = generate_capacity_matrix(NODES, edge_caps)
        
        n = len(NODES)
        assert len(matrix) == n
        for row in matrix:
            assert len(row) == n
    
    def test_generate_capacity_matrix_values(self):
        """Test capacity matrix has correct values"""
        edge_caps = {
            ("A", "B"): 10,
            ("B", "C"): 15
        }
        nodes = ["A", "B", "C"]
        matrix = generate_capacity_matrix(nodes, edge_caps)
        
        assert matrix[0][1] == 10  # A -> B
        assert matrix[1][2] == 15  # B -> C
        assert matrix[0][0] == 0   # A -> A
        assert matrix[1][0] == 0   # No reverse edge
    
    def test_generate_capacity_matrix_zeros_for_no_edges(self):
        """Test capacity matrix has zeros where no edges exist"""
        edge_caps = generate_edge_caps()
        matrix = generate_capacity_matrix(NODES, edge_caps)
        
        # Diagonal should be zero
        for i in range(len(NODES)):
            assert matrix[i][i] == 0
    
    def test_new_random_graph_returns_four_values(self):
        """Test new_random_graph returns 4 values"""
        result = new_random_graph()
        assert len(result) == 4
    
    def test_new_random_graph_nodes(self):
        """Test new_random_graph returns correct nodes"""
        nodes, _, _, _ = new_random_graph()
        assert nodes == NODES
    
    def test_new_random_graph_edges(self):
        """Test new_random_graph returns correct edges"""
        _, edges, _, _ = new_random_graph()
        assert edges == EDGES
    
    def test_new_random_graph_edge_caps(self):
        """Test new_random_graph returns valid edge_caps"""
        _, _, edge_caps, _ = new_random_graph()
        assert isinstance(edge_caps, dict)
        assert len(edge_caps) == len(EDGES)
    
    def test_new_random_graph_capacity_matrix(self):
        """Test new_random_graph returns valid capacity matrix"""
        _, _, _, capacity_mat = new_random_graph()
        assert len(capacity_mat) == len(NODES)
        assert all(len(row) == len(NODES) for row in capacity_mat)
    
    def test_new_random_graph_consistency(self):
        """Test edge_caps and capacity_matrix are consistent"""
        nodes, _, edge_caps, capacity_mat = new_random_graph()
        
        for (u, v), cap in edge_caps.items():
            ui = nodes.index(u)
            vi = nodes.index(v)
            assert capacity_mat[ui][vi] == cap


# ============================================================================
# MAX FLOW ALGORITHMS TESTS (max_flow_algorithms.py)
# ============================================================================

class TestMaxFlowAlgorithms:
    """Test suite for max_flow_algorithms.py module"""
    
    # SimpleQueue Tests
    def test_simple_queue_creation(self):
        """Test SimpleQueue can be created"""
        q = SimpleQueue()
        assert q is not None
        assert q.is_empty() == True
    
    def test_simple_queue_enqueue_dequeue(self):
        """Test enqueue and dequeue operations"""
        q = SimpleQueue()
        q.enqueue(1)
        q.enqueue(2)
        q.enqueue(3)
        
        assert q.dequeue() == 1
        assert q.dequeue() == 2
        assert q.dequeue() == 3
        assert q.is_empty() == True
    
    def test_simple_queue_is_empty(self):
        """Test is_empty method"""
        q = SimpleQueue()
        assert q.is_empty() == True
        
        q.enqueue(1)
        assert q.is_empty() == False
        
        q.dequeue()
        assert q.is_empty() == True
    
    def test_simple_queue_dequeue_empty(self):
        """Test dequeue on empty queue returns None"""
        q = SimpleQueue()
        assert q.dequeue() is None
    
    # Edmonds-Karp Tests
    def test_edmonds_karp_simple_network(self, simple_network):
        """Test Edmonds-Karp on simple network"""
        # A -> B (cap 10) -> C (cap 15)
        # Max flow should be 10
        max_flow = edmonds_karp(simple_network, 0, 2)
        assert max_flow == 10
    
    def test_edmonds_karp_sample_graph(self, sample_graph):
        """Test Edmonds-Karp on sample graph"""
        _, _, _, capacity_matrix = sample_graph
        # A to D: max flow through A->B->D (8) + A->C->D (5) = 13
        max_flow = edmonds_karp(capacity_matrix, 0, 3)
        assert max_flow == 13
    
    def test_edmonds_karp_no_path(self):
        """Test Edmonds-Karp when no path exists"""
        # Disconnected graph
        capacity = [
            [0, 10, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        max_flow = edmonds_karp(capacity, 0, 2)
        assert max_flow == 0
    
    def test_edmonds_karp_direct_edge(self):
        """Test Edmonds-Karp with direct edge"""
        capacity = [
            [0, 20],
            [0, 0]
        ]
        max_flow = edmonds_karp(capacity, 0, 1)
        assert max_flow == 20
    
    def test_edmonds_karp_multiple_paths(self):
        """Test Edmonds-Karp with multiple paths"""
        # Diamond graph: two paths from A to D
        capacity = [
            [0, 10, 10, 0],  # A
            [0, 0, 0, 10],   # B
            [0, 0, 0, 10],   # C
            [0, 0, 0, 0]     # D
        ]
        max_flow = edmonds_karp(capacity, 0, 3)
        assert max_flow == 20
    
    # Ford-Fulkerson Tests
    def test_ford_fulkerson_simple_network(self, simple_network):
        """Test Ford-Fulkerson on simple network"""
        max_flow = ford_fulkerson(simple_network, 0, 2)
        assert max_flow == 10
    
    def test_ford_fulkerson_sample_graph(self, sample_graph):
        """Test Ford-Fulkerson on sample graph"""
        _, _, _, capacity_matrix = sample_graph
        max_flow = ford_fulkerson(capacity_matrix, 0, 3)
        assert max_flow == 13
    
    def test_ford_fulkerson_no_path(self):
        """Test Ford-Fulkerson when no path exists"""
        capacity = [
            [0, 10, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        max_flow = ford_fulkerson(capacity, 0, 2)
        assert max_flow == 0
    
    def test_ford_fulkerson_direct_edge(self):
        """Test Ford-Fulkerson with direct edge"""
        capacity = [
            [0, 20],
            [0, 0]
        ]
        max_flow = ford_fulkerson(capacity, 0, 1)
        assert max_flow == 20
    
    def test_ford_fulkerson_multiple_paths(self):
        """Test Ford-Fulkerson with multiple paths"""
        capacity = [
            [0, 10, 10, 0],
            [0, 0, 0, 10],
            [0, 0, 0, 10],
            [0, 0, 0, 0]
        ]
        max_flow = ford_fulkerson(capacity, 0, 3)
        assert max_flow == 20
    
    # Algorithm Consistency Tests
    def test_algorithms_give_same_result_simple(self, simple_network):
        """Test both algorithms give same result on simple network"""
        ek_flow = edmonds_karp(simple_network, 0, 2)
        
        # Need fresh copy for FF
        capacity_copy = [row[:] for row in simple_network]
        ff_flow = ford_fulkerson(capacity_copy, 0, 2)
        
        assert ek_flow == ff_flow
    
    def test_algorithms_give_same_result_complex(self, sample_graph):
        """Test both algorithms give same result on complex graph"""
        _, _, _, capacity_matrix = sample_graph
        
        ek_flow = edmonds_karp(capacity_matrix, 0, 3)
        
        # Fresh copy for FF
        capacity_copy = [row[:] for row in capacity_matrix]
        ff_flow = ford_fulkerson(capacity_copy, 0, 3)
        
        assert ek_flow == ff_flow


# ============================================================================
# UTILS TESTS (utils.py)
# ============================================================================

class TestUtils:
    """Test suite for utils.py module"""
    
    def test_validate_int_valid_integer(self):
        """Test validate_int with valid integers"""
        valid_cases = ["0", "1", "42", "100", "9999"]
        
        for text in valid_cases:
            is_valid, value = validate_int(text)
            assert is_valid == True
            assert value == int(text)
    
    def test_validate_int_negative_integer(self):
        """Test validate_int with negative integers"""
        is_valid, value = validate_int("-5")
        assert is_valid == True
        assert value == -5
    
    def test_validate_int_invalid_text(self):
        """Test validate_int with invalid text"""
        invalid_cases = ["abc", "12.5", "", "  ", "1a2", "NaN"]
        
        for text in invalid_cases:
            is_valid, value = validate_int(text)
            assert is_valid == False
            assert value is None
    
    def test_validate_int_whitespace(self):
        """Test validate_int with whitespace"""
        is_valid, value = validate_int("  42  ")
        assert is_valid == True
        assert value == 42
    
    def test_time_function_basic(self):
        """Test time_function with basic function"""
        def dummy_func():
            return 42
        
        result, elapsed = time_function(dummy_func)
        
        assert result == 42
        assert elapsed >= 0
        assert isinstance(elapsed, float)
    
    def test_time_function_with_args(self):
        """Test time_function with arguments"""
        def add(a, b):
            return a + b
        
        result, elapsed = time_function(add, 5, 10)
        
        assert result == 15
        assert elapsed >= 0
    
    def test_time_function_with_kwargs(self):
        """Test time_function with keyword arguments"""
        def multiply(a, b=2):
            return a * b
        
        result, elapsed = time_function(multiply, 5, b=3)
        
        assert result == 15
        assert elapsed >= 0
    
    def test_time_function_measures_time(self):
        """Test that time_function actually measures time"""
        import time as time_module
        
        def slow_func():
            time_module.sleep(0.01)  # Sleep for 10ms
            return "done"
        
        result, elapsed = time_function(slow_func)
        
        assert result == "done"
        assert elapsed >= 0.01  # Should take at least 10ms
        assert elapsed < 1.0    # Should be much less than 1 second
    
    def test_time_function_returns_tuple(self):
        """Test time_function returns a tuple"""
        def dummy():
            return 1
        
        result = time_function(dummy)
        assert isinstance(result, tuple)
        assert len(result) == 2


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for the entire system"""
    
    def test_full_game_flow(self):
        """Test complete game flow from graph generation to flow calculation"""
        # Generate graph
        nodes, edges, edge_caps, capacity_mat = new_random_graph()
        
        # Calculate flow using both algorithms
        source_idx = nodes.index("A")
        sink_idx = nodes.index("T")
        
        ek_flow = edmonds_karp(capacity_mat, source_idx, sink_idx)
        
        # Fresh copy for FF
        capacity_copy = [row[:] for row in capacity_mat]
        ff_flow = ford_fulkerson(capacity_copy, source_idx, sink_idx)
        
        # Both should give same result
        assert ek_flow == ff_flow
        
        # Flow should be non-negative
        assert ek_flow >= 0
        
        # Flow should be reasonable (not exceeding sum of all capacities)
        total_capacity = sum(edge_caps.values())
        assert ek_flow <= total_capacity
    
    def test_graph_to_algorithm_pipeline(self):
        """Test pipeline from graph generation to algorithm execution"""
        nodes, _, edge_caps, capacity_mat = new_random_graph()
        
        # Verify matrix consistency
        for (u, v), cap in edge_caps.items():
            ui = nodes.index(u)
            vi = nodes.index(v)
            assert capacity_mat[ui][vi] == cap
        
        # Run algorithm
        source_idx = nodes.index("A")
        sink_idx = nodes.index("T")
        max_flow = edmonds_karp(capacity_mat, source_idx, sink_idx)
        
        # Validate result
        assert isinstance(max_flow, int)
        assert max_flow >= 0
    
    def test_timed_algorithm_execution(self):
        """Test timing both algorithms"""
        nodes, _, _, capacity_mat = new_random_graph()
        source_idx = nodes.index("A")
        sink_idx = nodes.index("T")
        
        # Time EK
        ek_flow, ek_time = time_function(edmonds_karp, capacity_mat, source_idx, sink_idx)
        
        # Time FF
        capacity_copy = [row[:] for row in capacity_mat]
        ff_flow, ff_time = time_function(ford_fulkerson, capacity_copy, source_idx, sink_idx)
        
        # Both should succeed
        assert ek_flow == ff_flow
        assert ek_time >= 0
        assert ff_time >= 0
    
    def test_database_workflow(self):
        """Test complete database workflow"""
        from database import DB_PATH
        
        init_db()
        clear_db()
        
        # Insert multiple results
        for i in range(3):
            success, _ = insert_correct_result(
                f"Player{i}",
                10 + i,
                10 + i,
                0.001 * i,
                0.002 * i
            )
            assert success == True
        
        # Verify all inserted
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM win_results")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 3
    
    def test_insert_all_result_correct_guess(self):
        """Test inserting a correct guess into all_game_results"""
        from database import DB_PATH
        
        init_db()
        
        # Insert correct result
        success, message = insert_all_result(
            "TestPlayer",
            42,
            42,
            0.001,
            0.002
        )
        
        assert success == True
        assert "success" in message.lower()
        
        # Verify insertion
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM all_game_results")
        rows = cursor.fetchall()
        conn.close()
        
        assert len(rows) == 1
        assert rows[0][1] == "TestPlayer"
        assert rows[0][2] == 42
        assert rows[0][3] == 42
    
    def test_insert_all_result_wrong_guess(self):
        """Test inserting a wrong guess into all_game_results"""
        from database import DB_PATH
        
        init_db()
        clear_db()
        
        # Insert wrong result (guess 30, correct 42)
        success, message = insert_all_result(
            "TestPlayer",
            30,
            42,
            0.001,
            0.002
        )
        
        assert success == True
        
        # Verify insertion
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM all_game_results")
        rows = cursor.fetchall()
        conn.close()
        
        assert len(rows) == 1
    def test_insert_all_result_multiple(self):
        """Test inserting multiple results (both correct and incorrect)"""
        from database import DB_PATH
        
        init_db()
        clear_db()
        
        # Insert mixed results
        test_cases = [
            ("Player1", 42, 42),  # Correct
            ("Player2", 30, 42),  # Wrong
            ("Player3", 50, 42),  # Wrong
        ]
        
        for name, guess, correct in test_cases:
            success, _ = insert_all_result(name, guess, correct, 0.001, 0.002)
            assert success == True
        
        # Verify all inserted
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM all_game_results")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 3
    
    def test_sqlite_sequence_removed(self):
        """Test that sqlite_sequence table is removed"""
        from database import DB_PATH
        
        init_db()
        
        # Check sqlite_sequence does not exist
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='sqlite_sequence'
        """)
        result = cursor.fetchone()
        conn.close()
        
        assert result is None, "sqlite_sequence table should not exist"


# ============================================================================
# EDGE CASES AND STRESS TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_single_node_graph(self):
        """Test algorithms on single node (source = sink)"""
        capacity = [[0]]
        # When source equals sink, flow should be 0 or handled gracefully
        # This is a degenerate case
        max_flow = edmonds_karp(capacity, 0, 0)
        assert max_flow == 0
    
    def test_two_node_graph(self):
        """Test algorithms on two-node graph"""
        capacity = [
            [0, 100],
            [0, 0]
        ]
        max_flow = edmonds_karp(capacity, 0, 1)
        assert max_flow == 100
    
    def test_large_capacity_values(self):
        """Test with very large capacity values"""
        capacity = [
            [0, 1000000, 1000000],
            [0, 0, 1000000],
            [0, 0, 0]
        ]
        max_flow = edmonds_karp(capacity, 0, 2)
        assert max_flow == 2000000
    
    def test_zero_capacity_edges(self):
        """Test graph with all zero capacity edges"""
        capacity = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        max_flow = edmonds_karp(capacity, 0, 2)
        assert max_flow == 0
    
    def test_player_name_boundary_lengths(self):
        """Test player names at boundary lengths"""
        # Minimum length (2 chars)
        is_valid, _ = validate_player_name("AB")
        assert is_valid == True
        
        # Just below minimum
        is_valid, _ = validate_player_name("A")
        assert is_valid == False
        
        # Maximum length (50 chars)
        is_valid, _ = validate_player_name("A" * 50)
        assert is_valid == True
        
        # Just above maximum
        is_valid, _ = validate_player_name("A" * 51)
        assert is_valid == False
    
    def test_answer_boundary_values(self):
        """Test answer validation at boundaries"""
        # Zero
        is_valid, _ = validate_answer(0)
        assert is_valid == True
        
        # Just below zero
        is_valid, _ = validate_answer(-1)
        assert is_valid == False
        
        # Large positive
        is_valid, _ = validate_answer(999999)
        assert is_valid == True


# ============================================================================
# RUN CONFIGURATION
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
