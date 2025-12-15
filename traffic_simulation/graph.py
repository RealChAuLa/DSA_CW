# graph.py
# Build the traffic network as an edge-capacity map and a nodes list.
# This module returns:
# - NODES (list)
# - EDGES (list of pairs)
# - edge_caps dict {(u,v): cap}
# - capacity_matrix (adjacency matrix)

import random

NODES = ["A","B","C","D","E","F","G","H","T"]
EDGES = [
    ("A","B"), ("A","C"), ("A","D"),
    ("B","E"), ("B","F"),
    ("C","E"), ("C","F"),
    ("D","F"),
    ("E","G"), ("E","H"),
    ("F","H"),
    ("G","T"), ("H","T")
]

def generate_edge_caps(min_cap=5, max_cap=15):
    edge_caps = {}
    for (u,v) in EDGES:
        edge_caps[(u,v)] = random.randint(min_cap, max_cap)
    return edge_caps

def generate_capacity_matrix(nodes_list, edge_caps):
    n = len(nodes_list)
    idx = {nodes_list[i]: i for i in range(n)}
    mat = [[0]*n for _ in range(n)]
    for (u,v), cap in edge_caps.items():
        ui = idx[u]
        vi = idx[v]
        mat[ui][vi] = cap
    return mat

# convenience function used by UI/main to get all artifacts
def new_random_graph():
    edge_caps = generate_edge_caps()
    capacity_mat = generate_capacity_matrix(NODES, edge_caps)
    return NODES, EDGES, edge_caps, capacity_mat
