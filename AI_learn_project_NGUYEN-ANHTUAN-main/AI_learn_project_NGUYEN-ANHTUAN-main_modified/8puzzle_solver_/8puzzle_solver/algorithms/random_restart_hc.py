import random
from .utils import get_neighbors, is_goal, heuristic, is_solvable

# Random Restart Hill Climbing
# Theo ma gia cua thay:
# 1. Khoi tao: MAX_RESTART = so lan chay lai toi da
# 2. CHO i = 1 den MAX_RESTART:
#    Current_State = Start
#    TRONG KHI (dung):
#      NEU Current_State == Goal: TRA VE Current_State
#      Sinh tat ca cac trang thai lan can cua Current_State
#      Loc ra tap Better_Neighbors = {Neighbor | Value(Neighbor) tot hon Value(Current_State)}
#      NEU Better_Neighbors RONG:
#        Thoat vong lap TRONG KHI  // Luot nay bi ket, nhay sang luot i tiep theo
#      NGUOC LAI:
#        Next_State = Chon trang thai tot nhat tu tap Better_Neighbors
#        Current_State = Next_State
# 3. TRA VE "That bai" // Chay het MAX_RESTART ma khong cham duoc Goal

def random_restart_hill_climbing(start, goal, max_restart=50):
    nodes_expanded = 0
    full_path = [start]

    for i in range(max_restart):
        # Luot dau dung start, cac luot sau dung trang thai ngau nhien
        if i == 0:
            current_state = start
        else:
            while True:
                s = list(range(9))
                random.shuffle(s)
                if is_solvable(s):
                    break
            current_state = s
            full_path.append(current_state)  # danh dau diem restart

        while True:
            if is_goal(current_state, goal):
                full_path.append(current_state)
                return full_path, nodes_expanded

            neighbors = get_neighbors(current_state)
            nodes_expanded += 1

            current_value = -heuristic(current_state, goal)

            # Loc ra tap Better_Neighbors
            better_neighbors = [nb for nb in neighbors
                                if -heuristic(nb, goal) > current_value]

            if not better_neighbors:
                # Bi ket, nhay sang luot restart tiep theo
                break
            else:
                # Chon trang thai tot nhat tu Better_Neighbors
                next_state = min(better_neighbors, key=lambda s: heuristic(s, goal))
                current_state = next_state
                full_path.append(current_state)

    return None, nodes_expanded
