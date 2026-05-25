# Ham dung chung cho cac thuat toan

GOAL = [1, 2, 3, 4, 5, 6, 7, 8, 0]  # 0 la o trong

def is_goal(state, goal):
    return state == goal

def get_blank_pos(state):
    return state.index(0)

# Lay cac trang thai ke tiep (cac nuoc di hop le)
def get_neighbors(state):
    neighbors = []
    blank = get_blank_pos(state)
    row, col = blank // 3, blank % 3

    moves = []
    if row > 0: moves.append(-3)  # len
    if row < 2: moves.append(3)   # xuong
    if col > 0: moves.append(-1)  # trai
    if col < 2: moves.append(1)   # phai

    for move in moves:
        new_state = state[:]
        swap_pos = blank + move
        new_state[blank], new_state[swap_pos] = new_state[swap_pos], new_state[blank]
        neighbors.append(new_state)

    return neighbors

# Kiem tra co giai duoc khong (tinh so nghich the)
def is_solvable(state):
    tiles = [x for x in state if x != 0]
    inversions = 0
    for i in range(len(tiles)):
        for j in range(i + 1, len(tiles)):
            if tiles[i] > tiles[j]:
                inversions += 1
    return inversions % 2 == 0
