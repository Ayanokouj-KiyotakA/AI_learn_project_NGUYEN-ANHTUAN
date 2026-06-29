# minimax.py
# Nhom 5: Minimax Search - Game 2 robot tren CUNG 1 bang
#
# Mo hinh dung:
#   Robot A (MAX, luot chan): di chuyen o trong de GIAM h → tien ve goal
#   Robot B (MIN, luot le) : di chuyen o trong de TANG h → can tro Robot A
#   Hai robot luan phien di chuyen o trong cua CUNG MOT bang.
#   Robot A thang neu dat goal; B thang neu A het nuoc di hoac qua so luot toi da.

from .utils import get_neighbors, is_goal, heuristic


DO_SAU_MINIMAX = 4    # do sau nhin truoc cua Robot A
SO_LUOT_TOI_DA = 200  # tong so luot ca 2 robot


def minimax(trang_thai_dau, muc_tieu):
    """
    Game 2 robot tren cung 1 bang voi Minimax.
    - Robot A dung Minimax depth=DO_SAU_MINIMAX de chon nuoc di (giam h)
    - Robot B dung greedy: chon nuoc tang h nhieu nhat (doi thu manh)
    Returns: (duong_di, tong_nodes) hoac (None, nodes) neu A thua
    """
    duong_di      = [trang_thai_dau[:]]
    trang_thai_ht = trang_thai_dau[:]
    tong_nodes    = 0
    da_tham       = {tuple(trang_thai_dau)}

    for luot in range(SO_LUOT_TOI_DA):
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
                diem, so_nodes = _minimax_de_quy(
                    ke, muc_tieu, DO_SAU_MINIMAX - 1,
                    False, da_tham | {tuple(ke)}
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


def _minimax_de_quy(trang_thai, muc_tieu, do_sau, la_min, da_tham):
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
            gia_tri, n = _minimax_de_quy(
                ke, muc_tieu, do_sau - 1, True, da_tham | {tuple(ke)})
            tong_nodes += n
            gia_tri_tot = min(gia_tri_tot, gia_tri)
    else:
        gia_tri_tot = float('-inf')
        for ke in cac_ke:
            gia_tri, n = _minimax_de_quy(
                ke, muc_tieu, do_sau - 1, False, da_tham | {tuple(ke)})
            tong_nodes += n
            gia_tri_tot = max(gia_tri_tot, gia_tri)

    return gia_tri_tot, tong_nodes
