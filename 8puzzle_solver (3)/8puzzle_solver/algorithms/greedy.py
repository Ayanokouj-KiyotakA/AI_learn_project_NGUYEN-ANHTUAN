import heapq
from .utils import get_neighbors, is_goal, heuristic

# Greedy Best-First Search
# Theo ma gia cua thay:
# 1. Khoi tao FRONTIER = {Start}, tinh h(Start)
# 2. Khoi tao REACHED = {}
# 3. TRONG KHI frontier khong rong:
#    a. Chon trang thai n co h(n) nho nhat tu FRONTIER
#    b. NEU n == Goal: tra ve thanh cong
#    c. Loai n khoi FRONTIER, them n vao REACHED
#    d. Voi moi trang thai m ke voi n:
#       i. NEU m chua co trong FRONTIER va REACHED:
#          gan cha cua m la n, tinh h(m), them m vao FRONTIER
#       ii. NEU m da co trong FRONTIER hoac REACHED: bo qua

def greedy(start, goal):
    h_start = heuristic(start, goal)

    counter = 0
    # (h(n), id, state, path)
    frontier = [(h_start, counter, start, [start])]
    heapq.heapify(frontier)

    reached = set()
    nodes_expanded = 0

    while frontier:
        h, _, node, path = heapq.heappop(frontier)

        node_tuple = tuple(node)

        if is_goal(node, goal):
            return path, nodes_expanded

        # loai n khoi frontier, them vao reached
        reached.add(node_tuple)
        nodes_expanded += 1

        frontier_states = {tuple(f[2]) for f in frontier}

        for m in get_neighbors(node):
            m_tuple = tuple(m)
            # NEU m chua co trong FRONTIER va REACHED
            if m_tuple not in reached and m_tuple not in frontier_states:
                h_m = heuristic(m, goal)
                counter += 1
                heapq.heappush(frontier, (h_m, counter, m, path + [m]))
            # NEU da co trong FRONTIER hoac REACHED: bo qua

    return None, nodes_expanded
