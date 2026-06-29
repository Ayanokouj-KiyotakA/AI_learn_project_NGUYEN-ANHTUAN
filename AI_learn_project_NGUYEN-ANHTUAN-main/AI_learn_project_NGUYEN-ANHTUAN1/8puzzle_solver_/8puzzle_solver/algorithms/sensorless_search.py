# sensorless_search.py
# Nhom 4: Sensorless Search (Belief State BFS)
#
# Agent khong co cam bien — khong biet dang o trang thai nao.
# Belief state = frozenset cac trang thai co the.
# Mo hinh no-op: hanh dong khong hop le o mot so trang thai se giu nguyen trang thai do.
# Muc tieu: belief state chi con chua 1 trang thai = goal.

import random
from collections import deque
from .utils import is_goal, get_neighbors, is_solvable


SO_BUOC_NGAU_NHIEN = 2   # so buoc di tu start de tao belief ban dau
MAX_NODES = 10000


MOVES = {
    'U': -3, 'D': 3, 'L': -1, 'R': 1
}
VALID = {
    'U': lambda r, c: r > 0,
    'D': lambda r, c: r < 2,
    'L': lambda r, c: c > 0,
    'R': lambda r, c: c < 2,
}
DIRECTIONS = list(MOVES.keys())


def _ap_dung_huong(state, huong):
    lst = list(state)
    blank = lst.index(0)
    r, c = blank // 3, blank % 3
    if not VALID[huong](r, c):
        return None
    swap = blank + MOVES[huong]
    lst[blank], lst[swap] = lst[swap], lst[blank]
    return tuple(lst)


def _ap_dung_belief(belief, huong):
    """No-op model: hanh dong khong hop le giu nguyen trang thai do."""
    belief_moi = set()
    changed = False
    for s in belief:
        s_moi = _ap_dung_huong(s, huong)
        if s_moi is not None:
            belief_moi.add(s_moi)
            changed = True
        else:
            belief_moi.add(s)  # no-op
    if not changed:
        return None
    return frozenset(belief_moi)


def _trang_thai_lan_can(start, k):
    """Tao trang thai bang cach di k buoc ngau nhien tu start."""
    s = tuple(start)
    for _ in range(k):
        hang_xom = [_ap_dung_huong(s, h) for h in DIRECTIONS
                    if _ap_dung_huong(s, h) is not None]
        if hang_xom:
            s = random.choice(hang_xom)
    return s


def sensorless_search(start, goal):
    goal_t = tuple(goal)

    # Tao belief ban dau: start + 2 trang thai lan can
    s0 = tuple(start)
    s1 = _trang_thai_lan_can(start, SO_BUOC_NGAU_NHIEN)
    s2 = _trang_thai_lan_can(start, SO_BUOC_NGAU_NHIEN)
    init_belief = frozenset({s0, s1, s2})

    frontier = deque([(init_belief, [])])
    visited  = {init_belief}
    nodes    = 0

    while frontier and nodes < MAX_NODES:
        belief, actions = frontier.popleft()
        nodes += 1

        if all(s == goal_t for s in belief):
            # Replay tren trang thai start
            state = list(start)
            path  = [state[:]]
            for h in actions:
                kq = _ap_dung_huong(tuple(state), h)
                if kq is not None:
                    state = list(kq)
                path.append(state[:])
            return path, nodes

        for huong in DIRECTIONS:
            new_belief = _ap_dung_belief(belief, huong)
            if new_belief is None:
                continue
            if new_belief not in visited:
                visited.add(new_belief)
                frontier.append((new_belief, actions + [huong]))

    return None, nodes
