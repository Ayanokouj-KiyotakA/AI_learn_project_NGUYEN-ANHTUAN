from collections import deque
from .utils import is_goal

# AC-3 (Arc Consistency Algorithm 3)
# Dam bao tinh nhat quan cung (arc consistency) trong CSP
# Arc (Xi, Xj): moi gia tri trong domain[Xi] phai co it nhat 1 gia tri khac trong domain[Xj]
# Rang buoc: all-different (moi bien nhan gia tri khac nhau)

def _revise(domains, xi, xj):
    revised = False
    for val in list(domains[xi]):
        # Khong ton tai gia tri nao trong xj != val => loai val khoi xi
        if not any(v != val for v in domains[xj]):
            domains[xi].remove(val)
            revised = True
    return revised


def _run_ac3(domains, variables):
    queue = deque((i, j) for i in variables for j in variables if i != j)
    nodes = 0
    while queue:
        xi, xj = queue.popleft()
        nodes += 1
        if _revise(domains, xi, xj):
            if not domains[xi]:
                return False, nodes
            for xk in variables:
                if xk != xj:
                    queue.append((xk, xi))
    return True, nodes


def ac3(start, goal):
    variables = list(range(9))
    # Domain ban dau: moi bien co the nhan bat ky gia tri 0-8
    domains = {i: list(range(9)) for i in variables}

    # AC-3 giam domain truoc
    consistent, nodes = _run_ac3(domains, variables)
    if not consistent:
        return None, nodes

    # Backtrack voi AC-3 domains
    assignment = {}

    def backtrack(var_idx):
        nonlocal nodes
        if var_idx == 9:
            state = [assignment[i] for i in range(9)]
            return state if is_goal(state, goal) else None

        value = goal[var_idx]

        if value in domains[var_idx] and value not in assignment.values():
            assignment[var_idx] = value
            nodes += 1

            # Cap nhat domains va chay AC-3 lai
            new_domains = {k: list(v) for k, v in domains.items()}
            new_domains[var_idx] = [value]
            ok, n = _run_ac3(new_domains, variables)
            nodes += n

            if ok:
                result = backtrack(var_idx + 1)
                if result is not None:
                    return result

            del assignment[var_idx]

        return None

    result = backtrack(0)
    if result is not None:
        return [start, goal], nodes
    return None, nodes
