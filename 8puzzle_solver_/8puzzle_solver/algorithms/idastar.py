from .utils import get_neighbors, is_goal, heuristic

# IDA* - Iterative Deepening A*
# Giong IDS nhung nguong cat la f = g + h thay vi do sau
# Moi vong lap: chay DFS, cat khi f(n) > threshold
# Neu cat: cap nhat threshold = min f bi cat
# Uu diem: tiet kiem bo nho hon A*, van dam bao tim duong ngan nhat

def idastar(start, goal):
    threshold = heuristic(start, goal)
    path = [start]
    nodes_expanded = 0

    while True:
        result, new_threshold, nodes = _search(path, 0, threshold, goal)
        nodes_expanded += nodes

        if result is not None:
            return result, nodes_expanded
        if new_threshold == float('inf'):
            return None, nodes_expanded

        threshold = new_threshold  # tang nguong len muc nho nhat bi cat


def _search(path, g, threshold, goal):
    node = path[-1]
    f = g + heuristic(node, goal)
    nodes_expanded = 0

    if f > threshold:
        return None, f, nodes_expanded  # cat, tra ve f de cap nhat threshold

    if is_goal(node, goal):
        return list(path), threshold, nodes_expanded

    min_threshold = float('inf')
    nodes_expanded += 1

    for child in get_neighbors(node):
        if tuple(child) not in [tuple(p) for p in path]:  # tranh vong lap
            path.append(child)
            result, new_t, nodes = _search(path, g + 1, threshold, goal)
            nodes_expanded += nodes

            if result is not None:
                return result, new_t, nodes_expanded

            if new_t < min_threshold:
                min_threshold = new_t

            path.pop()

    return None, min_threshold, nodes_expanded
