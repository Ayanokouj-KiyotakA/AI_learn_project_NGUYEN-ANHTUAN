from .utils import get_neighbors, is_goal
from .dls import dls

# IDS - Iterative Deepening Search
# Lap lai DLS voi limit tang dan tu 0 den max_depth
# Ket hop uu diem cua BFS (tim kiem toan dien) va DFS (tiet kiem bo nho)

def ids(start, goal, max_depth=50):
    total_nodes = 0

    for depth in range(max_depth + 1):
        result, nodes = dls(start, goal, limit=depth)
        total_nodes += nodes
        if result is not None:
            return result, total_nodes

    return None, total_nodes
