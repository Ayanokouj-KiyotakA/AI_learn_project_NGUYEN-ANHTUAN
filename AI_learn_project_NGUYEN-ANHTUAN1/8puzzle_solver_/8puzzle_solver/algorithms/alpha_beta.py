from .utils import get_neighbors, is_goal, heuristic

# Alpha-Beta Pruning - cai tien cua Minimax
# Cat nhanh khi:
#   alpha >= beta (MAX node khong can xet them)
#   beta <= alpha (MIN node khong can xet them)
# Ket qua giong Minimax nhung nhanh hon do cat bo nhieu nhanh

MAX_DEPTH = 6

def _alpha_beta(state, goal, depth, is_max, alpha, beta, path, visited):
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
        best_score = float('inf')
        for nxt in neighbors:
            path.append(nxt)
            result, score, n = _alpha_beta(nxt, goal, depth - 1, False, alpha, beta, path, visited)
            nodes += n
            if score < best_score:
                best_score = score
                best_path = result if result else path[:]
            beta = min(beta, best_score)
            path.pop()
            if beta <= alpha:  # cat nhanh alpha
                break
    else:
        best_score = float('-inf')
        for nxt in neighbors:
            path.append(nxt)
            result, score, n = _alpha_beta(nxt, goal, depth - 1, True, alpha, beta, path, visited)
            nodes += n
            if score > best_score:
                best_score = score
                best_path = result
            alpha = max(alpha, best_score)
            path.pop()
            if beta <= alpha:  # cat nhanh beta
                break

    return best_path, best_score, nodes


def alpha_beta(start, goal):
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
            _, score, n = _alpha_beta(nxt, goal, MAX_DEPTH - 1, False,
                                      float('-inf'), float('inf'), [nxt], visited_global)
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
