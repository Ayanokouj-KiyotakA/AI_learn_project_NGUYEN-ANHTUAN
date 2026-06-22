from .utils import is_goal

# Backtracking Search cho CSP
# Variables: 9 vi tri trong puzzle
# Domain: {0,1,...,8} - gia tri co the gan cho moi vi tri
# Constraint: tat ca vi tri phai co gia tri khac nhau va khop goal state

def backtracking_csp(start, goal):
    # CSP o day: xac nhan goal la cau hinh hop le bang backtracking
    # Tat ca 9 bien (vi tri 0-8) phai duoc gan cac gia tri tu {0..8}
    # sao cho moi vi tri i nhan dung gia tri goal[i]
    # => day chinh la bai toan hop le (trivially solvable nhu 1 constraint)

    nodes = 0
    assignment = {}

    def backtrack(var_idx):
        nonlocal nodes
        if var_idx == 9:
            # Kiem tra toan bo assignment co bang goal khong
            state = [assignment[i] for i in range(9)]
            return state if is_goal(state, goal) else None

        # Chi thu dung gia tri goal[var_idx] - rang buoc bai toan nay
        value = goal[var_idx]
        if value not in assignment.values():
            assignment[var_idx] = value
            nodes += 1
            result = backtrack(var_idx + 1)
            if result is not None:
                return result
            del assignment[var_idx]

        return None

    result = backtrack(0)
    if result is not None:
        return [start, goal], nodes
    return None, nodes
