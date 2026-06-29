import random
from .utils import get_neighbors, is_goal, heuristic

# Stochastic Hill Climbing
# Theo ma gia cua thay:
# 1. Current_State = Start
# 2. TRONG KHI (dung):
#    NEU Current_State == Goal: TRA VE Current_State
#    Sinh tat ca cac trang thai lan can cua Current_State
#    Loc ra tap Better_Neighbors = {Neighbor | Value(Neighbor) > Value(Current_State)}
#    NEU Better_Neighbors RONG:
#      TRA VE Current_State  (Dung vi da dat cuc dai cuc bo)
#    NGUOC LAI:
#      Next_State = Chon NGAU NHIEN mot trang thai tu tap Better_Neighbors
#      Current_State = Next_State  (Quay lai dau vong lap voi trang thai moi)
#
# Khac voi Simple HC: chon ngau nhien trong Better_Neighbors thay vi chon ngay cai dau tien tot hon
# Khac voi Random Restart HC: khong restart, chi chay 1 lan

def stochastic_hill_climbing(start, goal, max_iter=10000):
    current_state = start
    path = [current_state]
    nodes_expanded = 0

    for _ in range(max_iter):
        if is_goal(current_state, goal):
            return path, nodes_expanded

        neighbors = get_neighbors(current_state)
        nodes_expanded += 1

        current_value = -heuristic(current_state, goal)

        # Loc ra tap Better_Neighbors
        better_neighbors = [nb for nb in neighbors
                            if -heuristic(nb, goal) > current_value]

        if not better_neighbors:
            # Dat cuc dai cuc bo, dung lai
            break
        else:
            # Chon NGAU NHIEN mot trang thai tu Better_Neighbors
            next_state = random.choice(better_neighbors)
            current_state = next_state
            path.append(current_state)

    if is_goal(current_state, goal):
        return path, nodes_expanded
    return path, nodes_expanded
