# and_or_search.py
# Nhom 4: AND-OR Search — moi truong non-deterministic co truot that
#
# Mo hinh: moi nuoc di co xac suat truot sang trang thai lan can xau nhat
# OR node: agent chon hanh dong
# AND node: tat ca ket qua co the deu phai co ke hoach

import random
from .utils import get_neighbors, is_goal, heuristic


DO_SAU_TOI_DA = 50
XAC_SUAT_TRUOT = 0.2   # 20% kha nang truot


def and_or_search(trang_thai_dau, muc_tieu):
    return _or_search(trang_thai_dau[:], muc_tieu, frozenset(), 0, XAC_SUAT_TRUOT, [0], False)


def _or_search(trang_thai, muc_tieu, da_tham, do_sau, slip_prob, dem, is_phuc_hoi):
    if is_goal(trang_thai, muc_tieu):
        return [trang_thai[:]], dem[0]
    if do_sau > DO_SAU_TOI_DA:
        return None, dem[0]

    khoa = tuple(trang_thai)
    if khoa in da_tham:
        return None, dem[0]

    da_tham_moi = da_tham | {khoa}
    dem[0] += 1

    hang_xom = get_neighbors(trang_thai)
    hang_xom.sort(key=lambda s: heuristic(s, muc_tieu))

    h_curr = heuristic(trang_thai, muc_tieu)
    hang_xom_xau = [s for s in hang_xom if heuristic(s, muc_tieu) > h_curr]

    for nuoc_chinh in hang_xom:
        co_truot = bool(hang_xom_xau) and (slip_prob > 0) and not is_phuc_hoi
        if co_truot:
            nuoc_truot = random.choice(hang_xom_xau)
            cac_ket_qua = [nuoc_chinh, nuoc_truot]
        else:
            cac_ket_qua = [nuoc_chinh]

        ke_hoach, so_nodes = _and_search(
            cac_ket_qua, muc_tieu, da_tham_moi, do_sau + 1, slip_prob, dem
        )
        if ke_hoach is not None:
            return [trang_thai[:]] + ke_hoach, so_nodes

    return None, dem[0]


def _and_search(cac_ket_qua, muc_tieu, da_tham, do_sau, slip_prob, dem):
    ke_hoach_chung = []
    for i, ket_qua in enumerate(cac_ket_qua):
        if i == 0:
            ke_hoach_con, so_nodes = _or_search(
                ket_qua, muc_tieu, da_tham, do_sau, slip_prob, dem, False
            )
        else:
            # Ket qua truot: dung fresh da_tham, is_phuc_hoi=True
            ke_hoach_con, so_nodes = _or_search(
                ket_qua, muc_tieu, frozenset(), do_sau, slip_prob, dem, True
            )
        if ke_hoach_con is None:
            return None, dem[0]
        ke_hoach_chung.extend(ke_hoach_con)

    return ke_hoach_chung, dem[0]
