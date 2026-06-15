import random
from .utils import get_neighbors, is_goal, heuristic

# Local Beam Search(k)
# Theo ma gia cua thay:
# 1. Khoi tao: Current_State_set = {Sinh ngau nhien k trang thai, bat dau tu Start}
# 2. TRONG KHI (dung):
#    Neighbor_States = rong
#    2.1. SINH TRANG THAI LAN CAN:
#         VOI MOI State trong Current_State_set:
#           Sinh tat ca cac trang thai lan can cua State
#           Them cac trang thai lan can nay vao Neighbor_States
#    2.2. KIEM TRA DICH:
#         VOI MOI Neighbor trong Neighbor_States:
#           NEU Neighbor == Goal: TRA VE Neighbor (dung ngay lap tuc)
#    2.3. LUA CHON CHUM (neu chua tim thay dich):
#         Sap xep Neighbor_States theo thu tu gia tri ham muc tieu h tot dan
#         Current_State_set = Lay k trang thai tot nhat tu Neighbor_States da sap xep

def local_beam_search(start, goal, k=3, max_iter=1000):
    # Khoi tao k trang thai: start + (k-1) trang thai ngau nhien
    current_set = [start]
    for _ in range(k - 1):
        s = list(range(9))
        random.shuffle(s)
        current_set.append(s)

    # Track path tu start (chi theo doi beam dau tien)
    path = [start]
    nodes_expanded = 0

    for _ in range(max_iter):
        neighbor_states = []

        # 2.1 Sinh trang thai lan can cua tat ca state trong current_set
        for state in current_set:
            for nb in get_neighbors(state):
                neighbor_states.append(nb)
            nodes_expanded += 1

        # 2.2 Kiem tra dich
        for nb in neighbor_states:
            if is_goal(nb, goal):
                path.append(nb)
                return path, nodes_expanded

        # 2.3 Lua chon chum: lay k trang thai tot nhat theo h
        neighbor_states.sort(key=lambda s: heuristic(s, goal))
        current_set = neighbor_states[:k]

        # Cap nhat path theo beam dau tien
        path.append(current_set[0])

        # Neu tat ca beam bi ket (h khong giam)
        if all(heuristic(s, goal) >= heuristic(path[-2], goal) for s in current_set):
            break

    return None, nodes_expanded
