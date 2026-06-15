from .utils import get_neighbors, is_goal

# DFS - Depth First Search (Graph version)
# frontier dung LIFO stack
# explored luu cac state da kham pha

def dfs(start, goal):
    node = start
    if is_goal(node, goal):
        return [node], 0

    frontier = [(node, [node])]  # stack: (state, path)

    explored = set()
    explored.add(tuple(node))

    nodes_expanded = 0

    while frontier:
        node, path = frontier.pop()
        nodes_expanded += 1

        for child in get_neighbors(node):
            child_tuple = tuple(child)
            if is_goal(child, goal):
                return path + [child], nodes_expanded
            if child_tuple not in explored:
                explored.add(child_tuple)
                frontier.append((child, path + [child]))

    return None, nodes_expanded
