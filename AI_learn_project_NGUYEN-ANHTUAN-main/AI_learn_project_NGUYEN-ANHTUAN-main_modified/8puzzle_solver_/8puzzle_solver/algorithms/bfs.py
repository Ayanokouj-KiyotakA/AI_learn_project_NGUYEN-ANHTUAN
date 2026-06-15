from collections import deque
from .utils import get_neighbors, is_goal

# BFS - Breadth First Search (Graph version)
# frontier dung FIFO queue
# explored luu cac state da kham pha

def bfs(start, goal):
    node = start
    if is_goal(node, goal):
        return [node], 0

    frontier = deque()
    frontier.append((node, [node]))  # (state, path)

    explored = set()
    explored.add(tuple(node))

    nodes_expanded = 0

    while frontier:
        node, path = frontier.popleft()
        nodes_expanded += 1

        for child in get_neighbors(node):
            child_tuple = tuple(child)
            if is_goal(child, goal):
                return path + [child], nodes_expanded
            if child_tuple not in explored and not any(tuple(f[0]) == child_tuple for f in frontier):
                explored.add(child_tuple)
                frontier.append((child, path + [child]))

    return None, nodes_expanded
