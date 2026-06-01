from .utils import get_neighbors, is_goal

# DLS - Depth Limited Search
# Giong DFS nhung co gioi han do sau (limit)
# Neu vuot qua limit thi cutoff

def dls(start, goal, limit=20):
    nodes_expanded = 0

    def recursive_dls(node, path, depth):
        nonlocal nodes_expanded
        if is_goal(node, goal):
            return path, False  # (result, cutoff?)
        if depth == 0:
            return None, True   # cutoff

        cutoff_occurred = False
        nodes_expanded += 1

        for child in get_neighbors(node):
            if tuple(child) not in [tuple(p) for p in path]:  # tranh vong lap
                result, cutoff = recursive_dls(child, path + [child], depth - 1)
                if cutoff:
                    cutoff_occurred = True
                elif result is not None:
                    return result, False

        if cutoff_occurred:
            return None, True
        return None, False

    result, _ = recursive_dls(start, [start], limit)
    return result, nodes_expanded
