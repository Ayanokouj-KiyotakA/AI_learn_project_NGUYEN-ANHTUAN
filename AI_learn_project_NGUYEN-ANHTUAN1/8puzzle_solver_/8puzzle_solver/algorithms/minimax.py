from .utils import get_neighbors, is_goal, heuristic

# Minimax Search (adapted cho 8-puzzle)
# Trong 8-puzzle khong co doi thu, nen ta gia lap:
# MAX node: agent chon nuoc di tot nhat (giam h)
# MIN node: "doi thu ao" chon nuoc di xau nhat (tang h)
# Gop xen MAX-MIN theo tung do sau de ra quyet dinh

MAX_DEPTH = 6

def _minimax(state, goal, depth, is_max, path, visited):
    if is_goal(state, goal):
        return path[:], heuristic(state, goal), 1
    if depth == 0:
        return None, heuristic(state, goal), 1

    state_t = tuple(state)
    if state_t in visited:
        return None, heuristic(state, goal), 0
    visited = visited | {state_t}

    neighbors = get_neighbors(state)
    nodes = 1
    best_path = None

    if is_max:
        best_score = float('inf')  # muon h nho nhat
        for nxt in neighbors:
            path.append(nxt)
            result, score, n = _minimax(nxt, goal, depth - 1, False, path, visited)
            nodes += n
            if score < best_score:
                best_score = score
                best_path = result if result else path[:]
            path.pop()
    else:
        best_score = float('-inf')  # doi thu muon h lon nhat
        for nxt in neighbors:
            path.append(nxt)
            result, score, n = _minimax(nxt, goal, depth - 1, True, path, visited)
            nodes += n
            if score > best_score:
                best_score = score
                best_path = result
            path.pop()

    return best_path, best_score, nodes


def minimax(start, goal):
    path = [start[:]]
    current = start[:]
    total_nodes = 0
    visited_global = set()

    # Tung buoc chon nuoc di tot nhat bang minimax
    for _ in range(100):
        if is_goal(current, goal):
            return path, total_nodes

        visited_global.add(tuple(current))
        neighbors = get_neighbors(current)

        best_score = float('inf')
        best_next = None
        nodes = 0

        for nxt in neighbors:
            _, score, n = _minimax(nxt, goal, MAX_DEPTH - 1, False, [nxt], visited_global)
            nodes += n
            if score < best_score:
                best_score = score
                best_next = nxt

        total_nodes += nodes

        if best_next is None:
            break

        current = best_next[:]
        path.append(current)

    if is_goal(current, goal):
        return path, total_nodes
    return None, total_nodes
