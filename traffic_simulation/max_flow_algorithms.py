# max_flow_algorithms.py
# Pure Python implementations: Ford-Fulkerson (DFS) and Edmonds-Karp (BFS)
# No imports used — manual queue via list, recursion allowed.

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
# Ford-Fulkerson (DFS-based)
# Uses adjacency matrix 'capacity' and integer node indices
# -------------------------
def ford_fulkerson(capacity, source, sink):
    n = len(capacity)
    residual = [capacity[i][:] for i in range(n)]

    def dfs(u, t, visited, flow):
        if u == t:
            return flow
        visited[u] = True
        for v in range(n):
            if not visited[v] and residual[u][v] > 0:
                # Calculate minimum capacity along the path
                if flow is None:
                    min_cap = residual[u][v]
                else:
                    min_cap = min(flow, residual[u][v])
                pushed = dfs(v, t, visited, min_cap)
                if pushed and pushed > 0:
                    residual[u][v] -= pushed
                    residual[v][u] += pushed
                    return pushed
        return 0

    max_flow = 0
    while True:
        visited = [False] * n
        pushed = dfs(source, sink, visited, None)  # None means infinite
        if not pushed or pushed == 0:
            break
        max_flow += pushed

    return max_flow

# Exposed API: functions expecting adjacency-matrix and integer indices:
# edmonds_karp(capacity_matrix, source_index, sink_index)
# ford_fulkerson(capacity_matrix, source_index, sink_index)
