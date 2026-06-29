import math
import random
from .utils import get_neighbors, is_goal, heuristic

# Simulated Annealing - mo phong qua trinh lam nguoi kim loai
# Nhiet do T cao: chap nhan ca nuoc xau (thoat cuc bo)
# Nhiet do T thap: chi chap nhan nuoc tot (hoi tu)

def simulated_annealing(start, goal, T_max=1000.0, T_min=0.01, alpha=0.995, max_iter=100000):
    current = start[:]
    path = [current[:]]
    visited = {tuple(current)}
    nodes = 0
    T = T_max

    for _ in range(max_iter):
        if is_goal(current, goal):
            return path, nodes
        if T < T_min:
            break

        neighbors = get_neighbors(current)
        nodes += 1
        next_state = random.choice(neighbors)

        # delta_E = h(current) - h(next): duong nghia la next tot hon
        delta_E = heuristic(current, goal) - heuristic(next_state, goal)

        if delta_E > 0:
            accept = True
        else:
            accept = random.random() < math.exp(delta_E / T)

        if accept:
            current = next_state[:]
            if tuple(current) not in visited:
                path.append(current[:])
                visited.add(tuple(current))

        T *= alpha

    if is_goal(current, goal):
        return path, nodes
    return None, nodes
