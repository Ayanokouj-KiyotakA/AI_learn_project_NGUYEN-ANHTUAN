from collections import deque
from .utils import is_goal

# Sensorless Search (Belief State BFS)
# Agent khong co cam bien, khong biet dang o trang thai nao
# Belief state = tap hop cac trang thai co the dang xay ra
# Muc tieu: tim chuoi hanh dong hoat dong dung voi moi trang thai trong belief

MAX_BELIEF_SIZE = 6
MAX_NODES = 5000

# 0=len, 1=xuong, 2=trai, 3=phai
MOVES = {0: -3, 1: 3, 2: -1, 3: 1}
VALID = {
    0: lambda r, c: r > 0,
    1: lambda r, c: r < 2,
    2: lambda r, c: c > 0,
    3: lambda r, c: c < 2
}

def _apply_action(belief, action):
    new_belief = set()
    for state in belief:
        lst = list(state)
        blank = lst.index(0)
        r, c = blank // 3, blank % 3
        if not VALID[action](r, c):
            return None
        swap = blank + MOVES[action]
        lst[blank], lst[swap] = lst[swap], lst[blank]
        new_belief.add(tuple(lst))
    return frozenset(new_belief)


def _replay(start, actions):
    state = start[:]
    path = [state[:]]
    for act in actions:
        blank = state.index(0)
        swap = blank + MOVES[act]
        s = state[:]
        s[blank], s[swap] = s[swap], s[blank]
        state = s
        path.append(state[:])
    return path


def sensorless_search(start, goal):
    goal_t = tuple(goal)
    init_belief = frozenset([tuple(start)])

    frontier = deque([(init_belief, [])])
    visited = {init_belief}
    nodes = 0

    while frontier:
        if nodes >= MAX_NODES:
            break

        belief, actions = frontier.popleft()
        nodes += 1

        if all(s == goal_t for s in belief):
            return _replay(start, actions), nodes

        for action in range(4):
            new_belief = _apply_action(belief, action)
            if new_belief is None:
                continue
            if len(new_belief) > MAX_BELIEF_SIZE:
                continue
            if new_belief not in visited:
                visited.add(new_belief)
                frontier.append((new_belief, actions + [action]))

    return None, nodes
