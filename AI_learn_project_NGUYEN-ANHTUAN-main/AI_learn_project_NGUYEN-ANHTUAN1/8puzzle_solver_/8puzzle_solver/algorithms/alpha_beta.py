# alpha_beta.py
# Nhom 5: Alpha-Beta Pruning — Game 2 robot tren CUNG 1 bang
#
# Giong Minimax nhung cat nhanh khong can khao sat:
#   alpha: gia tri tot nhat Robot A co the dam bao
#   beta:  gia tri tot nhat Robot B co the dam bao
#   Cat nhanh khi alpha >= beta

from .utils import get_neighbors, is_goal, heuristic


DO_SAU_AB    = 4    # do sau alpha-beta
SO_LUOT_TDAM = 200  # tong so luot ca 2 robot


def alpha_beta(trang_thai_dau, muc_tieu):
    """
    Game 2 robot tren cung 1 bang voi Alpha-Beta Pruning.
    Robot A (luot chan): Alpha-Beta, giam h tien ve goal
    Robot B (luot le) : greedy, tang h can tro Robot A
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
                diem, so_nodes = _ab_de_quy(
                    ke, muc_tieu, DO_SAU_AB - 1,
                    False, float('-inf'), float('inf'),
                    da_tham | {tuple(ke)}
                )
                tong_nodes += so_nodes
                if diem < diem_tot_nhat:
                    diem_tot_nhat = diem
                    ke_tot_nhat   = ke
        else:
            ke_tot_nhat = max(cac_ke_hop_le,
                              key=lambda s: heuristic(s, muc_tieu))
            tong_nodes += 1

        if ke_tot_nhat is None:
            break

        da_tham.add(tuple(ke_tot_nhat))
        trang_thai_ht = ke_tot_nhat[:]
        duong_di.append(trang_thai_ht)

    if is_goal(trang_thai_ht, muc_tieu):
        return duong_di, tong_nodes
    return None, tong_nodes


def _ab_de_quy(trang_thai, muc_tieu, do_sau, la_min, alpha, beta, da_tham):
    if is_goal(trang_thai, muc_tieu):
        return 0, 1
    if do_sau == 0:
        return heuristic(trang_thai, muc_tieu), 1

    cac_ke = [ke for ke in get_neighbors(trang_thai) if tuple(ke) not in da_tham]
    if not cac_ke:
        return heuristic(trang_thai, muc_tieu), 1

    tong_nodes = 1

    if not la_min:
        gia_tri_tot = float('inf')
        for ke in cac_ke:
            gia_tri, n = _ab_de_quy(
                ke, muc_tieu, do_sau - 1, True,
                alpha, beta, da_tham | {tuple(ke)})
            tong_nodes += n
            gia_tri_tot = min(gia_tri_tot, gia_tri)
            beta = min(beta, gia_tri_tot)
            if alpha >= beta:
                break
    else:
        gia_tri_tot = float('-inf')
        for ke in cac_ke:
            gia_tri, n = _ab_de_quy(
                ke, muc_tieu, do_sau - 1, False,
                alpha, beta, da_tham | {tuple(ke)})
            tong_nodes += n
            gia_tri_tot = max(gia_tri_tot, gia_tri)
            alpha = max(alpha, gia_tri_tot)
            if alpha >= beta:
                break

    return gia_tri_tot, tong_nodes
