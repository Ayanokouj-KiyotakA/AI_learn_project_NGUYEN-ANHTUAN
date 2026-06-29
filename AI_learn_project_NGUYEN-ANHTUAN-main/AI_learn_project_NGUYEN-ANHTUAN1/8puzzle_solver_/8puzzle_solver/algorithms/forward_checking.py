from .utils import is_goal

# Forward Checking cho CSP
# Sau khi gan gia tri cho bien, loai gia tri do khoi domain cac bien chua gan
# Neu domain nao rong => dead-end, backtrack ngay

def forward_checking(start, goal):
    nodes = 0
    assignment = {}

    def fc_backtrack(var_idx, available):
        nonlocal nodes
        if var_idx == 9:
            state = [assignment[i] for i in range(9)]
            return state if is_goal(state, goal) else None

        value = goal[var_idx]

        if value not in available:
            return None  # forward check: gia tri nay da bi loai

        assignment[var_idx] = value
        nodes += 1

        # Forward check: loai value khoi domain cac bien tiep theo
        new_available = [v for v in available if v != value]

        # Kiem tra dead-end: con du gia tri cho cac bien con lai khong
        remaining_vars = 9 - var_idx - 1
        if len(new_available) >= remaining_vars:
            result = fc_backtrack(var_idx + 1, new_available)
            if result is not None:
                return result

        del assignment[var_idx]
        return None

    all_values = list(range(9))
    result = fc_backtrack(0, all_values)

    if result is not None:
        return [start, goal], nodes
    return None, nodes
