from .utils import get_neighbors, is_goal, heuristic

# Simple Hill Climbing
# Theo ma gia cua thay:
# 1. Khoi tao Current_State = Start, tinh gia tri danh gia
# 2. TRONG KHI (dung):
#    a. Sinh lan luot cac trang thai lan can cua Current_State
#    b. Voi moi Next_State:
#       i.  Tinh gia tri danh gia cua Next_State
#       ii. NEU Value(Next_State) > Value(Current_State):
#           Current_State = Next_State  <-- chon ngay neighbor dau tien tot hon
#           Chuyen sang lan lap tiep theo
#    c. NEU khong ton tai trang thai lan can nao tot hon:
#       Dung vi da dat cuc dai cuc bo
# 3. TRA VE Current_State
#
# Luu y: Hill Climbing dung Value = -h(n) (gia tri cang cao cang tot)
# Neu h = 0 thi da den dich, neu h nho hon thi tot hon
# => Value(Next) > Value(Current) tuong duong h(Next) < h(Current)

def simple_hill_climbing(start, goal):
    current_state = start
    path = [current_state]
    nodes_expanded = 0

    current_value = -heuristic(current_state, goal)  # value = -h, cang lon cang tot

    while True:
        neighbors = get_neighbors(current_state)
        nodes_expanded += 1

        moved = False
        # Sinh lan luot tung neighbor, chon ngay cai dau tien tot hon
        for next_state in neighbors:
            next_value = -heuristic(next_state, goal)

            # NEU Value(Next_State) > Value(Current_State)
            if next_value > current_value:
                current_state = next_state
                current_value = next_value
                path.append(current_state)
                moved = True
                break  # chuyen sang lan lap tiep theo ngay

        # NEU khong ton tai trang thai lan can nao tot hon: dung
        if not moved:
            break

    if is_goal(current_state, goal):
        return path, nodes_expanded
    else:
        # Bi ket cuc bo, khong tim duoc loi giai
        return None, nodes_expanded
