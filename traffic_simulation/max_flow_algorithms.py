# max_flow_algorithms.py
# Pure Python implementations: Edmonds-Karp (BFS) and Dinic's Algorithm (level graph + blocking flow)
# No external imports required beyond built-ins.

# -------------------------
# Helper: Simple Queue (list-based)
# -------------------------


class SimpleQueue:
    def __init__(self):
        self._data = []
    def enqueue(self, x):
        self._data.append(x)
    def dequeue(self):
        if self._data:
            return self._data.pop(0)
        return None
    def is_empty(self):
        return len(self._data) == 0

# -------------------------
# Edmonds-Karp (BFS-based Ford-Fulkerson)
# Uses adjacency matrix 'capacity' and integer node indices
# -------------------------
def edmonds_karp(capacity, source, sink):
    n = len(capacity)
    # residual is a copy of capacity
    residual = [capacity[i][:] for i in range(n)]

    parent = [-1] * n

    def bfs():
        # returns True if there's a path, fills parent[]
        for i in range(n):
            parent[i] = -1
        q = SimpleQueue()
        q.enqueue(source)
        parent[source] = -2  # mark source visited with special value
        while not q.is_empty():
            u = q.dequeue()
            for v in range(n):
                if parent[v] == -1 and residual[u][v] > 0:
                    parent[v] = u
                    if v == sink:
                        return True
                    q.enqueue(v)
        return False

    max_flow = 0
    while bfs():
        # find bottleneck
        path_flow = 10**18
        s = sink
        while s != source:
            u = parent[s]
            if u == -1:
                break
            if residual[u][s] < path_flow:
                path_flow = residual[u][s]
            s = u
        if path_flow == 10**18:
            break
        # update residual
        v = sink
        while v != source:
            u = parent[v]
            residual[u][v] -= path_flow
            residual[v][u] += path_flow
            v = u
        max_flow += path_flow

    return max_flow

# -------------------------
# Dinic's Algorithm
# Uses adjacency matrix 'capacity' and integer node indices
# -------------------------
def dinic(capacity, source, sink):
    n = len(capacity)
    residual = [capacity[i][:] for i in range(n)]

    def bfs_level():
        """Build level graph; return list of levels (sink level -1 if unreachable)."""
        level = [-1] * n
        q = SimpleQueue()
        q.enqueue(source)
        level[source] = 0
        while not q.is_empty():
            u = q.dequeue()
            for v in range(n):
                if residual[u][v] > 0 and level[v] == -1:
                    level[v] = level[u] + 1
                    q.enqueue(v)
        return level

    def dfs_block(u, pushed, level, it):
        """Send flow through level graph using current-edge iteration to reduce complexity."""
        if u == sink:
            return pushed
        for v in range(it[u], n):
            if residual[u][v] > 0 and level[v] == level[u] + 1:
                it[u] = v  # mark current edge index
                bottleneck = pushed if pushed is not None else residual[u][v]
                flow = dfs_block(v, min(bottleneck, residual[u][v]) if bottleneck is not None else residual[u][v], level, it)
                if flow and flow > 0:
                    residual[u][v] -= flow
                    residual[v][u] += flow
                    return flow
            it[u] = v + 1  # move iterator forward even if edge not used
        it[u] = n  # exhausted all neighbors
        return 0

    max_flow = 0
    INF = 10**18

    while True:
        level = bfs_level()
        if level[sink] == -1:
            break  # no more augmenting paths
        it = [0] * n
        while True:
            pushed = dfs_block(source, INF, level, it)
            if not pushed:
                break
            max_flow += pushed

    return max_flow

# Exposed API: functions expecting adjacency-matrix and integer indices:
# edmonds_karp(capacity_matrix, source_index, sink_index)
# dinic(capacity_matrix, source_index, sink_index)
