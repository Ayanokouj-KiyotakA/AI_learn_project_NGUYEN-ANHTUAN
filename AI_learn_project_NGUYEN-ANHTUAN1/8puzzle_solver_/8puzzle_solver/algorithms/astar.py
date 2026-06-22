import heapq
from .utils import get_neighbors, is_goal, heuristic

# A* Search
# Theo ma gia cua thay:
# 1. Khoi tao FRONTIER = {Start} voi f(Start) = g(Start) + h(Start) = 0 + h(Start)
# 2. Khoi tao REACHED = {}
# 3. TRONG KHI frontier khong rong:
#    a. Chon n co f(n) nho nhat
#    b. NEU n == Goal: tra ve thanh cong
#    c. Loai n khoi FRONTIER, them n vao REACHED
#    d. Voi moi m ke voi n:
#       i.  Tinh g_new(m) = g(n) + cost(m)  [cost = 1 moi buoc]
#       ii. NEU m da nam trong REACHED:
#           - NEU g_new(m) >= g(m): bo qua (te hon)
#           - NGUOC LAI: xoa m khoi REACHED, cap nhat g(m) = g_new(m)
#       iii.NEU m da nam trong FRONTIER:
#           - NEU g_new(m) < g(m): cap nhat g(m), f(m) = g(m) + h(m), cap nhat cha
#       iv. NEU m chua co trong FRONTIER va REACHED:
#           gan g(m) = g_new(m), tinh f(m) = g(m) + h(m), gan cha, them m vao FRONTIER

def astar(start, goal):
    h_start = heuristic(start, goal)
    g_start = 0
    f_start = g_start + h_start

    counter = 0
    # (f(n), id, g(n), state, path)
    frontier = [(f_start, counter, g_start, start, [start])]
    heapq.heapify(frontier)

    reached = {}         # state_tuple -> g value
    frontier_map = {}    # state_tuple -> g value (de check nhanh)
    frontier_map[tuple(start)] = g_start

    nodes_expanded = 0

    while frontier:
        f, _, g, node, path = heapq.heappop(frontier)

        node_tuple = tuple(node)

        # co the da bi update, bo qua entry cu
        if node_tuple in frontier_map and frontier_map[node_tuple] < g:
            continue
        if node_tuple in reached and reached[node_tuple] < g:
            continue

        if is_goal(node, goal):
            return path, nodes_expanded

        # loai n khoi frontier, them vao reached
        if node_tuple in frontier_map:
            del frontier_map[node_tuple]
        reached[node_tuple] = g
        nodes_expanded += 1

        for m in get_neighbors(node):
            m_tuple = tuple(m)
            g_new = g + 1  # cost moi buoc = 1

            if m_tuple in reached:
                # NEU g_new >= g(m) hien tai: bo qua
                if g_new >= reached[m_tuple]:
                    continue
                # NGUOC LAI: xoa khoi reached, them lai vao frontier
                del reached[m_tuple]

            if m_tuple in frontier_map:
                # NEU g_new < g(m) hien tai: cap nhat
                if g_new < frontier_map[m_tuple]:
                    frontier_map[m_tuple] = g_new
                    h_m = heuristic(m, goal)
                    f_m = g_new + h_m
                    counter += 1
                    heapq.heappush(frontier, (f_m, counter, g_new, m, path + [m]))
            else:
                # m chua co trong FRONTIER va REACHED
                h_m = heuristic(m, goal)
                f_m = g_new + h_m
                frontier_map[m_tuple] = g_new
                counter += 1
                heapq.heappush(frontier, (f_m, counter, g_new, m, path + [m]))

    return None, nodes_expanded
