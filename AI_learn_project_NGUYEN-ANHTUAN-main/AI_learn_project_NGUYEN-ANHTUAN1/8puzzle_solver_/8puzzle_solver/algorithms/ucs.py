import heapq
from .utils import get_neighbors, is_goal

# UCS - Uniform Cost Search
# frontier dung priority queue, sap xep theo cost
# Moi buoc di co cost = 1, nen tuong tu BFS nhung tong quat hon

def ucs(start, goal):
    if is_goal(start, goal):
        return [start], 0

    # (cost, id, state, path) - them id de tranh so sanh list
    counter = 0
    frontier = [(0, counter, start, [start])]
    heapq.heapify(frontier)

    explored = set()
    nodes_expanded = 0

    while frontier:
        cost, _, node, path = heapq.heappop(frontier)

        node_tuple = tuple(node)
        if node_tuple in explored:
            continue
        explored.add(node_tuple)
        nodes_expanded += 1

        if is_goal(node, goal):
            return path, nodes_expanded

        for child in get_neighbors(node):
            child_tuple = tuple(child)
            if child_tuple not in explored:
                new_cost = cost + 1  # moi buoc di cost = 1
                counter += 1
                heapq.heappush(frontier, (new_cost, counter, child, path + [child]))

    return None, nodes_expanded
