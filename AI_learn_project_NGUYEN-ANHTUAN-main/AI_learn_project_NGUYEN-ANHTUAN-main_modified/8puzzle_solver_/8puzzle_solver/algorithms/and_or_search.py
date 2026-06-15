import random
from .utils import get_neighbors, is_goal, heuristic

# AND-OR Search - tim kiem trong moi truong non-deterministic
# Moi nuoc di co the bi "truot" sang trang thai khac voi xac suat nho
# OR node: agent chon hanh dong
# AND node: tat ca ket qua co the deu phai giai duoc

MAX_DEPTH = 40

def _or_search(state, goal, visited, depth):
    if is_goal(state, goal):
        return [state[:]], 1
    if depth > MAX_DEPTH or tuple(state) in visited:
        return None, 0

    visited = visited | {tuple(state)}
    nodes = 1

    neighbors = get_neighbors(state)
    neighbors.sort(key=lambda s: heuristic(s, goal))
    h_curr = heuristic(state, goal)

    for nxt in neighbors:
        # Them 1 ket qua slip ngau nhien neu co lang gieng tot hon
        outcomes = [nxt]
        slips = [s for s in neighbors if s != nxt and heuristic(s, goal) < h_curr]
        if slips:
            outcomes.append(random.choice(slips))

        plan, n = _and_search(outcomes, goal, visited, depth + 1)
        nodes += n
        if plan is not None:
            return [state[:]] + plan, nodes

    return None, nodes


def _and_search(outcomes, goal, visited, depth):
    if not outcomes:
        return [], 0

    nodes = 0
    plan, n = _or_search(outcomes[0], goal, visited, depth)
    nodes += n
    if plan is None:
        return None, nodes

    # Kiem tra cac ket qua phu (slip)
    for side in outcomes[1:]:
        if not is_goal(side, goal):
            _, n2 = _or_search(side, goal, visited, depth)
            nodes += n2

    return plan, nodes


def and_or_search(start, goal):
    return _or_search(start[:], goal, set(), 0)
