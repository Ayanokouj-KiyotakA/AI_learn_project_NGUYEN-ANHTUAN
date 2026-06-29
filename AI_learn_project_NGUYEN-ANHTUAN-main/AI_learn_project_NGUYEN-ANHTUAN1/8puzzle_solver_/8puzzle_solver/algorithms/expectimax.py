# expectimax.py
# Nhom 5: Expectimax Search — Game 2 robot (Robot A + Robot ngau nhien)
#
# Mo hinh:
#   Robot A (MAX, luot chan): chon nuoc di co GIA TRI KY VONG tot nhat
#   Robot B (CHANCE, luot le): di NGAU NHIEN — gia tri ky vong = trung binh h
#
# Phan biet voi Minimax:
#   Minimax: B chon nuoc tang h tot nhat (doi thu hoan hao)
#   Expectimax: B chon nuoc ngau nhien → A tinh GIA TRI KY VONG (trung binh h)

import random
from .utils import get_neighbors, is_goal, heuristic


DO_SAU_EX    = 4    # do sau expectimax
SO_LUOT_TDAM = 200  # tong so luot ca 2 robot


def expectimax(trang_thai_dau, muc_tieu):
    """
    Game 2 robot: Robot A dung Expectimax, Robot B di ngau nhien.
    Returns: (duong_di, tong_nodes) hoac (None, nodes) neu A thua
    """
    duong_di      = [trang_thai_dau[:]]
    trang_thai_ht = trang_thai_dau[:]
    tong_nodes    = 0
    da_tham       = {tuple(trang_thai_dau)}

    for luot in range(SO_LUOT_TDAM):
        if is_goal(trang_thai_ht, muc_tieu):
            break

        cac_ke_hop_le = [
            ke for ke in get_neighbors(trang_thai_ht)
            if tuple(ke) not in da_tham
        ]
        if not cac_ke_hop_le:
            break

        la_robot_a = (luot % 2 == 0)

        if la_robot_a:
            diem_tot_nhat = float('inf')
            ke_tot_nhat   = None
            for ke in cac_ke_hop_le:
                diem, so_nodes = _ex_de_quy(
                    ke, muc_tieu, DO_SAU_EX - 1,
                    False, da_tham | {tuple(ke)}
                )
                tong_nodes += so_nodes
                if diem < diem_tot_nhat:
                    diem_tot_nhat = diem
                    ke_tot_nhat   = ke
        else:
            # Robot B: di ngau nhien
            ke_tot_nhat = random.choice(cac_ke_hop_le)
            tong_nodes += 1

        if ke_tot_nhat is None:
            break

        da_tham.add(tuple(ke_tot_nhat))
        trang_thai_ht = ke_tot_nhat[:]
        duong_di.append(trang_thai_ht)

    if is_goal(trang_thai_ht, muc_tieu):
        return duong_di, tong_nodes
    return None, tong_nodes


def _ex_de_quy(trang_thai, muc_tieu, do_sau, la_chance, da_tham):
    if is_goal(trang_thai, muc_tieu):
        return 0, 1
    if do_sau == 0:
        return heuristic(trang_thai, muc_tieu), 1

    cac_ke = [ke for ke in get_neighbors(trang_thai) if tuple(ke) not in da_tham]
    if not cac_ke:
        return heuristic(trang_thai, muc_tieu), 1

    tong_nodes = 1

    if not la_chance:
        # MAX node (Robot A): chon nuoc giam h nhat
        gia_tri_tot = float('inf')
        for ke in cac_ke:
            gia_tri, n = _ex_de_quy(
                ke, muc_tieu, do_sau - 1, True, da_tham | {tuple(ke)})
            tong_nodes += n
            gia_tri_tot = min(gia_tri_tot, gia_tri)
    else:
        # CHANCE node (Robot B): gia tri ky vong = trung binh h
        tong_h = 0
        for ke in cac_ke:
            gia_tri, n = _ex_de_quy(
                ke, muc_tieu, do_sau - 1, False, da_tham | {tuple(ke)})
            tong_nodes += n
            tong_h += gia_tri
        gia_tri_tot = tong_h / len(cac_ke)

    return gia_tri_tot, tong_nodes
