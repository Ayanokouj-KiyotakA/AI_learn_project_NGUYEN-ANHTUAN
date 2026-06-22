import random
from .utils import get_neighbors, is_goal, heuristic

# Expectimax Search
# MAX node: agent chon nuoc di co h nho nhat
# CHANCE node: ket qua ngau nhien, tinh gia tri ky vong (trung binh)
# Thich hop khi moi truong co yeu to may rui (non-deterministic)

MAX_DEPTH = 5

def _expectimax(state, goal, depth, is_max, visited):
    if is_goal(state, goal):
        return heuristic(state, goal), 1
    if depth == 0:
        return heuristic(state, goal), 1

    state_t = tuple(state)
    if state_t in visited:
        return heuristic(state, goal), 0
    visited = visited | {state_t}

    neighbors = get_neighbors(state)
    nodes = 1

    if is_max:
        # MAX node: chon nuoc co h nho nhat
        best = float('inf')
        for nxt in neighbors:
            score, n = _expectimax(nxt, goal, depth - 1, False, visited)
            nodes += n
            best = min(best, score)
        return best, nodes
    else:
        # CHANCE node: gia tri ky vong = trung binh cong
        total = 0
        for nxt in neighbors:
            score, n = _expectimax(nxt, goal, depth - 1, True, visited)
            nodes += n
            total += score
        return total / len(neighbors), nodes


def expectimax(start, goal):
    path = [start[:]]
    current = start[:]
    total_nodes = 0
    visited_global = set()

    for _ in range(100):
        if is_goal(current, goal):
            return path, total_nodes

        visited_global.add(tuple(current))
        neighbors = get_neighbors(current)

        best_score = float('inf')
        best_next = None
        nodes = 0

        for nxt in neighbors:
            score, n = _expectimax(nxt, goal, MAX_DEPTH - 1, False, visited_global)
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
