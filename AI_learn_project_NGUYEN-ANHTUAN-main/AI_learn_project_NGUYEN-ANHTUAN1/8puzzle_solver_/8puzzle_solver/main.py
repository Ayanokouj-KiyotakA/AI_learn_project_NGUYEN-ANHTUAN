import tkinter as tk
from tkinter import messagebox
import random
import threading
import time

from algorithms import (bfs, dfs, dls, ids, ucs, greedy, astar, idastar,
                        simple_hill_climbing, stochastic_hill_climbing,
                        random_restart_hill_climbing, local_beam_search,
                        simulated_annealing, and_or_search, sensorless_search,
                        minimax, alpha_beta, expectimax,
                        backtracking_csp, forward_checking, ac3,
                        is_solvable, GOAL, get_neighbors)

GOAL_STATE = GOAL

# ── Màu sắc (Light theme) ────────────────────────────────────────────────────
BG        = "#F0F4F8"
PANEL     = "#FFFFFF"
PANEL2    = "#F8FAFC"
BORDER    = "#CBD5E1"
DIVIDER   = "#E2E8F0"
TEXT      = "#1E293B"
MUTED     = "#64748B"
HEADER    = "#1E40AF"
TILE_CLR  = "#2563EB"
TILE_TXT  = "#FFFFFF"
TILE_SHAD = "#BFDBFE"
EMPTY_CLR = "#EFF6FF"
ACCENT    = "#2563EB"
SUCCESS   = "#059669"
DANGER    = "#DC2626"
WARN_CLR  = "#D97706"
BTN_ACT   = "#2563EB"
BTN_NRM   = "#E2E8F0"
BTN_HOV   = "#DBEAFE"
ROBOT_A   = "#059669"
ROBOT_B   = "#DC2626"

FONT_SANS = "Segoe UI"
FONT_MONO = "Consolas"

# ── Nhóm thuật toán ──────────────────────────────────────────────────────────
ALGO_GROUPS = [
    ("Uninformed Search", [
        ("BFS",  "Breadth-First Search"),
        ("DFS",  "Depth-First Search"),
        ("DLS",  "Depth-Limited Search"),
        ("IDS",  "Iterative Deepening"),
        ("UCS",  "Uniform Cost Search"),
    ]),
    ("Informed Search", [
        ("Greedy", "Greedy Best-First"),
        ("A*",     "A* Search"),
        ("IDA*",   "Iterative Deepening A*"),
    ]),
    ("Local Search", [
        ("Hill Climbing",       "Simple Hill Climbing"),
        ("Stochastic HC",       "Stochastic HC"),
        ("Random Restart HC",   "Random Restart HC"),
        ("Local Beam",          "Local Beam Search"),
        ("Simulated Annealing", "Simulated Annealing"),
    ]),
    ("Non-deterministic", [
        ("AND-OR Search",     "AND-OR Search"),
        ("Sensorless Search", "Sensorless / Belief State"),
    ]),
    ("Adversarial Search", [
        ("Minimax",    "Minimax Search"),
        ("Alpha-Beta", "Alpha-Beta Pruning"),
        ("Expectimax", "Expectimax Search"),
    ]),
    ("Constraint Satisfaction", [
        ("Backtracking CSP", "Backtracking Search"),
        ("Forward Checking", "Forward Checking"),
        ("AC-3",             "Arc Consistency AC-3"),
    ]),
]

ALL_ALGOS          = [a for _, algos in ALGO_GROUPS for a, _ in algos]
ADVERSARIAL_ALGOS  = {"Minimax", "Alpha-Beta", "Expectimax"}
NONDETERMINISTIC   = {"AND-OR Search", "Sensorless Search"}
LOCAL_SEARCH_ALGOS = {"Hill Climbing", "Stochastic HC", "Random Restart HC",
                      "Local Beam", "Simulated Annealing"}


class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle Solver")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)
        self.root.state("zoomed")

        self.state        = [1, 2, 3, 4, 5, 0, 7, 8, 6]
        self.solution     = []
        self.current_step = 0
        self.running      = False
        self.dls_limit    = tk.IntVar(value=20)
        self.beam_k       = tk.IntVar(value=3)
        self.slip_prob    = tk.DoubleVar(value=0.3)
        self.algo_var     = tk.StringVar(value="BFS")
        self.speed_var    = tk.DoubleVar(value=0.4)
        self.do_kho       = tk.IntVar(value=10)

        self._build_ui()
        self._draw_board()

    # =====================================================
    # XAY DUNG GIAO DIEN
    # =====================================================

    def _build_ui(self):
        col_board = tk.Frame(self.root, bg=BG, padx=20, pady=16)
        col_board.pack(side=tk.LEFT, fill=tk.Y)

        col_algo = tk.Frame(self.root, bg=PANEL,
                            padx=16, pady=16,
                            highlightthickness=1,
                            highlightbackground=DIVIDER)
        col_algo.pack(side=tk.LEFT, fill=tk.Y)

        col_log = tk.Frame(self.root, bg=PANEL,
                           padx=16, pady=16,
                           highlightthickness=1,
                           highlightbackground=DIVIDER)
        col_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_board_col(col_board)
        self._build_algo_col(col_algo)
        self._build_log_col(col_log)

    # ── Cột 1: Board + điều khiển ────────────────────────────────────────────

    def _build_board_col(self, parent):
        tk.Label(parent, text="8 Puzzle Solver",
                 font=(FONT_SANS, 17, "bold"),
                 bg=BG, fg=HEADER).pack(pady=(0, 14))

        board_wrap = tk.Frame(parent, bg=BORDER, padx=2, pady=2)
        board_wrap.pack()
        self.canvas = tk.Canvas(board_wrap, width=358, height=358,
                                bg=BG, highlightthickness=0)
        self.canvas.pack()

        row1 = tk.Frame(parent, bg=BG)
        row1.pack(fill=tk.X, pady=(14, 4))
        self._btn(row1, "Shuffle", self.shuffle,
                  BTN_ACT, TILE_TXT, bold=True, fs=10).pack(
                      side=tk.LEFT, padx=(0, 6), fill=tk.X, expand=True)
        self._btn(row1, "Reset", self.reset,
                  BTN_NRM, TEXT, fs=10).pack(
                      side=tk.LEFT, fill=tk.X, expand=True)

        # Slider độ khó
        row_kho = tk.Frame(parent, bg=BG)
        row_kho.pack(fill=tk.X, pady=(6, 0))
        tk.Label(row_kho, text="Do kho:",
                 font=(FONT_MONO, 8), bg=BG, fg=MUTED).pack(side=tk.LEFT)
        self.do_kho_lbl = tk.Label(row_kho, text="De",
                                   font=(FONT_MONO, 8, "bold"),
                                   bg=BG, fg=SUCCESS, width=6)
        self.do_kho_lbl.pack(side=tk.RIGHT)
        tk.Scale(row_kho, from_=5, to=40, resolution=5,
                 orient=tk.HORIZONTAL, variable=self.do_kho,
                 bg=BG, fg=TEXT, highlightthickness=0,
                 troughcolor=BTN_NRM, length=160,
                 showvalue=True, font=(FONT_MONO, 7),
                 command=self._cap_nhat_do_kho_lbl).pack(side=tk.LEFT, padx=4)

        self.solve_btn = tk.Button(parent, text="SOLVE",
                                   command=self.solve,
                                   bg=BTN_ACT, fg=TILE_TXT,
                                   font=(FONT_SANS, 12, "bold"),
                                   relief=tk.FLAT, pady=10, cursor="hand2")
        self.solve_btn.pack(fill=tk.X, pady=(12, 4))

        tk.Frame(parent, bg=BORDER, height=1).pack(fill=tk.X, pady=6)

        self.step_info = tk.StringVar(value="Buoc: — / —")
        tk.Label(parent, textvariable=self.step_info,
                 font=(FONT_MONO, 9), bg=BG, fg=MUTED).pack(anchor=tk.W)

        row2 = tk.Frame(parent, bg=BG)
        row2.pack(fill=tk.X, pady=4)
        self._btn(row2, "< Prev", self.prev_step, BTN_NRM, TEXT, fs=9).pack(
            side=tk.LEFT, padx=(0, 4), fill=tk.X, expand=True)
        self._btn(row2, "Next >", self.next_step, BTN_NRM, TEXT, fs=9).pack(
            side=tk.LEFT, padx=(0, 4), fill=tk.X, expand=True)
        self._btn(row2, "Auto >>", self.auto_play, BTN_ACT, TILE_TXT, fs=9).pack(
            side=tk.LEFT, fill=tk.X, expand=True)

        row3 = tk.Frame(parent, bg=BG)
        row3.pack(fill=tk.X, pady=(4, 0))
        tk.Label(row3, text="Speed:", font=(FONT_MONO, 8),
                 bg=BG, fg=MUTED).pack(side=tk.LEFT)
        tk.Scale(row3, from_=0.05, to=1.5, resolution=0.05,
                 orient=tk.HORIZONTAL, variable=self.speed_var,
                 bg=BG, fg=TEXT, highlightthickness=0,
                 troughcolor=BTN_NRM, length=170,
                 showvalue=False).pack(side=tk.LEFT, padx=4)

        self.param_frame = tk.Frame(parent, bg=BG)
        self.param_frame.pack(fill=tk.X, pady=(6, 0))

        self.status_var = tk.StringVar(value="Chon thuat toan va nhan SOLVE")
        tk.Label(parent, textvariable=self.status_var,
                 font=(FONT_MONO, 8), bg=BG, fg=MUTED,
                 wraplength=300, justify=tk.LEFT).pack(anchor=tk.W, pady=(8, 0))

    # ── Cột 2: Chọn thuật toán ────────────────────────────────────────────────

    def _build_algo_col(self, parent):
        tk.Label(parent, text="Thuat Toan",
                 font=(FONT_SANS, 14, "bold"),
                 bg=PANEL, fg=HEADER).pack(anchor=tk.W, pady=(0, 8))

        self.algo_var.trace_add("write", lambda *_: self._on_algo_change())

        cv = tk.Canvas(parent, bg=PANEL, highlightthickness=0, width=260)
        sb = tk.Scrollbar(parent, orient=tk.VERTICAL, command=cv.yview)
        sf = tk.Frame(cv, bg=PANEL)

        sf.bind("<Configure>",
                lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0, 0), window=sf, anchor="nw")
        cv.configure(yscrollcommand=sb.set)
        cv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        for group_name, algos in ALGO_GROUPS:
            tk.Label(sf, text=group_name.upper(),
                     font=(FONT_MONO, 8, "bold"),
                     bg=PANEL, fg=ACCENT).pack(anchor=tk.W, pady=(10, 2))
            tk.Frame(sf, bg=BORDER, height=1).pack(fill=tk.X, pady=(0, 4))

            for key, desc in algos:
                row = tk.Frame(sf, bg=PANEL)
                row.pack(fill=tk.X, pady=1)
                tk.Radiobutton(row, variable=self.algo_var, value=key,
                               text=key,
                               font=(FONT_MONO, 10, "bold"),
                               bg=PANEL, fg=TEXT,
                               activebackground=PANEL,
                               activeforeground=ACCENT,
                               selectcolor=PANEL,
                               cursor="hand2",
                               relief=tk.FLAT).pack(side=tk.LEFT)
                tk.Label(row, text=f"  {desc}",
                         font=(FONT_MONO, 8),
                         bg=PANEL, fg=MUTED).pack(side=tk.LEFT)

        cv.bind_all("<MouseWheel>",
                    lambda e: cv.yview_scroll(int(-1*(e.delta/120)), "units"))

    # ── Cột 3: Log kết quả ───────────────────────────────────────────────────

    def _build_log_col(self, parent):
        hdr = tk.Frame(parent, bg=PANEL)
        hdr.pack(fill=tk.X, pady=(0, 8))
        tk.Label(hdr, text="Ket Qua",
                 font=(FONT_SANS, 14, "bold"),
                 bg=PANEL, fg=HEADER).pack(side=tk.LEFT)
        self._btn(hdr, "Xoa", self.clear_log, BTN_NRM, MUTED, fs=8).pack(side=tk.RIGHT)

        self.stats_var = tk.StringVar(value="")
        self.stats_lbl = tk.Label(parent, textvariable=self.stats_var,
                                  font=(FONT_MONO, 9, "bold"),
                                  bg=PANEL, fg=SUCCESS,
                                  anchor=tk.W, justify=tk.LEFT)
        self.stats_lbl.pack(fill=tk.X, pady=(0, 6))

        frame_log = tk.Frame(parent, bg=PANEL)
        frame_log.pack(fill=tk.BOTH, expand=True)

        sb2 = tk.Scrollbar(frame_log)
        sb2.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text = tk.Text(frame_log, width=34,
                                font=(FONT_MONO, 9),
                                bg=PANEL2, fg=TEXT,
                                yscrollcommand=sb2.set,
                                relief=tk.FLAT,
                                state=tk.DISABLED,
                                spacing1=3,
                                padx=8, pady=6)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb2.config(command=self.log_text.yview)

        self.log_text.tag_config("err",    foreground=DANGER,  font=(FONT_MONO, 9, "bold"))
        self.log_text.tag_config("warn",   foreground=WARN_CLR, font=(FONT_MONO, 9, "bold"))
        self.log_text.tag_config("ok",     foreground=SUCCESS, font=(FONT_MONO, 9, "bold"))
        self.log_text.tag_config("header", foreground=HEADER,  font=(FONT_MONO, 9, "bold"))
        self.log_text.tag_config("muted",  foreground=MUTED)
        self.log_text.tag_config("step",   foreground=TEXT)
        self.log_text.tag_config("cur",    background=TILE_SHAD, foreground=HEADER)

    # ── Helper button ─────────────────────────────────────────────────────────

    def _btn(self, parent, text, cmd, bg, fg, bold=False, fs=9):
        return tk.Button(parent, text=text, command=cmd,
                         bg=bg, fg=fg,
                         font=(FONT_SANS, fs, "bold" if bold else ""),
                         relief=tk.FLAT, padx=8, pady=4,
                         cursor="hand2",
                         activebackground=BTN_HOV,
                         activeforeground=ACCENT)

    # =====================================================
    # VE BOARD
    # =====================================================

    def _draw_board(self, state=None):
        if state is None:
            state = self.state
        self.canvas.delete("all")
        size = 110
        pad  = 6
        for i, val in enumerate(state):
            r, c = i // 3, i % 3
            x1 = c * (size + pad) + pad
            y1 = r * (size + pad) + pad
            x2, y2 = x1 + size, y1 + size
            if val == 0:
                self.canvas.create_rectangle(x1, y1, x2, y2,
                                             fill=EMPTY_CLR, outline=BORDER, width=2)
            else:
                # Bong mo
                self.canvas.create_rectangle(x1+3, y1+3, x2+3, y2+3,
                                             fill=TILE_SHAD, outline="")
                self.canvas.create_rectangle(x1, y1, x2, y2,
                                             fill=TILE_CLR, outline="", width=0)
                self.canvas.create_text((x1+x2)//2, (y1+y2)//2,
                                        text=str(val),
                                        font=(FONT_SANS, 30, "bold"),
                                        fill=TILE_TXT)

    # =====================================================
    # LOG HELPERS
    # =====================================================

    def _log(self, text, tag="step"):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, text + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _log_step(self, idx, state, current=False):
        tag = "cur" if current else "step"
        lines = [f"Buoc {idx}:"]
        for r in range(3):
            row = state[r*3:(r+1)*3]
            lines.append("  " + " ".join(str(v) if v != 0 else "." for v in row))
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, "\n".join(lines) + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.stats_var.set("")

    # =====================================================
    # DO KHO LABEL
    # =====================================================

    def _cap_nhat_do_kho_lbl(self, val=None):
        k = self.do_kho.get()
        if k <= 10:
            ten, mau = "De", SUCCESS
        elif k <= 20:
            ten, mau = "Trung binh", WARN_CLR
        elif k <= 30:
            ten, mau = "Kho", DANGER
        else:
            ten, mau = "Rat kho", DANGER
        self.do_kho_lbl.config(text=ten, fg=mau)

    # =====================================================
    # SHUFFLE / RESET
    # =====================================================

    def shuffle(self):
        """
        Sinh trang thai ngau nhien bang cach di K buoc tu goal.
        Bao dam h <= K va luon co loi giai.
        """
        k = self.do_kho.get()
        s = GOAL_STATE[:]
        prev = None
        for _ in range(k):
            hang_xom = get_neighbors(s)
            ung_vien = [n for n in hang_xom if n != prev] or hang_xom
            prev = s[:]
            s = random.choice(ung_vien)
        self.state        = s
        self.solution     = []
        self.current_step = 0
        self.stats_var.set("")
        self.step_info.set("Buoc: — / —")
        self.status_var.set(f"Shuffled (k={k}) — nhan SOLVE de giai")
        self._draw_board()

    def reset(self):
        self.state        = [1, 2, 3, 4, 5, 0, 7, 8, 6]
        self.solution     = []
        self.current_step = 0
        self.stats_var.set("")
        self.step_info.set("Buoc: — / —")
        self.status_var.set("Reset")
        self._draw_board()
        self.clear_log()

    # =====================================================
    # ALGO CHANGE
    # =====================================================

    def _on_algo_change(self):
        for w in self.param_frame.winfo_children():
            w.destroy()

        algo = self.algo_var.get()
        if algo == "DLS":
            tk.Label(self.param_frame, text="Depth Limit:",
                     font=(FONT_MONO, 8), bg=BG, fg=MUTED).pack(side=tk.LEFT)
            tk.Spinbox(self.param_frame, from_=1, to=60,
                       textvariable=self.dls_limit, width=5,
                       font=(FONT_MONO, 9), bg=BTN_NRM, fg=TEXT,
                       relief=tk.FLAT).pack(side=tk.LEFT, padx=6)

        elif algo == "Local Beam":
            tk.Label(self.param_frame, text="Beam k:",
                     font=(FONT_MONO, 8), bg=BG, fg=MUTED).pack(side=tk.LEFT)
            tk.Spinbox(self.param_frame, from_=1, to=20,
                       textvariable=self.beam_k, width=5,
                       font=(FONT_MONO, 9), bg=BTN_NRM, fg=TEXT,
                       relief=tk.FLAT).pack(side=tk.LEFT, padx=6)

        elif algo == "AND-OR Search":
            tk.Label(self.param_frame, text="Slip prob:",
                     font=(FONT_MONO, 8), bg=BG, fg=MUTED).pack(side=tk.LEFT)
            tk.Scale(self.param_frame, from_=0.0, to=0.9, resolution=0.05,
                     orient=tk.HORIZONTAL, variable=self.slip_prob,
                     bg=BG, fg=TEXT, highlightthickness=0,
                     troughcolor=BTN_NRM, length=120,
                     showvalue=True, font=(FONT_MONO, 7)).pack(side=tk.LEFT, padx=4)

    # =====================================================
    # SOLVE
    # =====================================================

    def solve(self):
        algo  = self.algo_var.get()
        start = self.state[:]
        goal  = GOAL_STATE

        csp_algos = {"Backtracking CSP", "Forward Checking", "AC-3"}
        if algo not in csp_algos and not is_solvable(start):
            messagebox.showerror("Loi", "Puzzle khong co loi giai!")
            return

        self.clear_log()
        self._log(f"Dang chay {algo}...", "muted")
        self.status_var.set(f"Solving — {algo}...")
        self.solve_btn.config(state=tk.DISABLED, text="Solving...")

        def run():
            t0 = time.time()
            try:
                if algo == "BFS":
                    result, nodes = bfs(start, goal)
                elif algo == "DFS":
                    result, nodes = dfs(start, goal)
                elif algo == "DLS":
                    result, nodes = dls(start, goal, limit=self.dls_limit.get())
                elif algo == "IDS":
                    result, nodes = ids(start, goal)
                elif algo == "UCS":
                    result, nodes = ucs(start, goal)
                elif algo == "Greedy":
                    result, nodes = greedy(start, goal)
                elif algo == "A*":
                    result, nodes = astar(start, goal)
                elif algo == "IDA*":
                    result, nodes = idastar(start, goal)
                elif algo == "Hill Climbing":
                    result, nodes = simple_hill_climbing(start, goal)
                elif algo == "Stochastic HC":
                    result, nodes = stochastic_hill_climbing(start, goal)
                elif algo == "Random Restart HC":
                    result, nodes = random_restart_hill_climbing(start, goal)
                elif algo == "Local Beam":
                    result, nodes = local_beam_search(start, goal, k=self.beam_k.get())
                elif algo == "Simulated Annealing":
                    result, nodes = simulated_annealing(start, goal)
                elif algo == "AND-OR Search":
                    result, nodes = and_or_search(start, goal)
                elif algo == "Sensorless Search":
                    result, nodes = sensorless_search(start, goal)
                elif algo == "Minimax":
                    result, nodes = minimax(start, goal)
                elif algo == "Alpha-Beta":
                    result, nodes = alpha_beta(start, goal)
                elif algo == "Expectimax":
                    result, nodes = expectimax(start, goal)
                elif algo == "Backtracking CSP":
                    result, nodes = backtracking_csp(start, goal)
                elif algo == "Forward Checking":
                    result, nodes = forward_checking(start, goal)
                elif algo == "AC-3":
                    result, nodes = ac3(start, goal)
                else:
                    result, nodes = None, 0
            except Exception as e:
                result, nodes = None, 0
            elapsed = time.time() - t0
            self.root.after(0, lambda: self._on_solve_done(result, nodes, elapsed, algo))

        threading.Thread(target=run, daemon=True).start()

    def _on_solve_done(self, result, nodes, elapsed, algo):
        self.solve_btn.config(state=tk.NORMAL, text="SOLVE")

        if result is None or len(result) == 0:
            self.status_var.set("Khong tim duoc loi giai")
            self.stats_var.set(f"x  {algo}  |  {nodes} nodes  |  {elapsed:.3f}s")
            self.stats_lbl.config(fg=DANGER)
            self._log(f"x  Khong tim duoc loi giai", "err")
            self._log(f"   Nodes mo rong: {nodes}", "muted")
            self._log(f"   Thoi gian: {elapsed:.4f}s", "muted")
            if algo in ADVERSARIAL_ALGOS:
                self._log("   Robot B chan duoc Robot A (thu Shuffle lai)", "muted")
            elif algo in NONDETERMINISTIC:
                self._log("   Het node/do sau (thu Shuffle de co trang thai de hon)", "muted")
            return

        # Kiem tra co dat goal hay bi ket cuc bo
        dat_goal = (result[-1] == GOAL_STATE)
        steps    = len(result) - 1

        self.solution     = result
        self.current_step = 0
        self.step_info.set(f"Buoc: 0 / {steps}")

        if dat_goal:
            nhan = f"OK  {algo}  |  {steps} buoc  |  {nodes} nodes  |  {elapsed:.3f}s"
            self.stats_var.set(nhan)
            self.stats_lbl.config(fg=SUCCESS)
            self.status_var.set(f"Giai xong!  {steps} buoc  |  {nodes} nodes  |  {elapsed:.3f}s")
            self._log(f"OK  {algo}", "ok")
            self._log(f"   So buoc   : {steps}", "muted")
            self._log(f"   Nodes     : {nodes}", "muted")
            self._log(f"   Thoi gian : {elapsed:.4f}s", "muted")
        else:
            from algorithms.utils import heuristic
            h_cuoi = heuristic(result[-1], GOAL_STATE)
            nhan = f"!  {algo}  |  ket sau {steps} buoc  |  h={h_cuoi}"
            self.stats_var.set(nhan)
            self.stats_lbl.config(fg=WARN_CLR)
            self.status_var.set(f"Ket cuc bo sau {steps} buoc  (h={h_cuoi})")
            self._log(f"!  {algo}  — ket cuc bo", "warn")
            self._log(f"   Da di {steps} buoc, h cuoi = {h_cuoi}", "muted")
            self._log(f"   Nodes : {nodes}  |  {elapsed:.4f}s", "muted")
            if algo in LOCAL_SEARCH_ALGOS:
                self._log("   Bi ket cuc bo (local optimum)", "muted")
                self._log("   Dung Random Restart HC / SA de co co hoi hon", "muted")
            elif algo in ADVERSARIAL_ALGOS:
                self._log("   Robot B chan duoc Robot A (thu Shuffle lai)", "muted")

        self._log("-" * 30, "muted")
        for i, s in enumerate(self.solution):
            self._log_step(i, s, current=(i == 0))

        self._draw_board(self.solution[0])

    # =====================================================
    # DIEU KHIEN TUNG BUOC
    # =====================================================

    def _highlight_current_step(self):
        self.step_info.set(f"Buoc: {self.current_step} / {len(self.solution)-1}")
        self._draw_board(self.solution[self.current_step])

    def next_step(self):
        if not self.solution or self.current_step >= len(self.solution) - 1:
            return
        self.current_step += 1
        self._highlight_current_step()

    def prev_step(self):
        if not self.solution or self.current_step <= 0:
            return
        self.current_step -= 1
        self._highlight_current_step()

    def auto_play(self):
        if not self.solution or self.running:
            return
        self.running = True

        def play():
            while self.current_step < len(self.solution) - 1 and self.running:
                self.current_step += 1
                s = self.solution[self.current_step]
                self.root.after(0, lambda st=s: self._draw_board(st))
                self.root.after(0, lambda: self.step_info.set(
                    f"Buoc: {self.current_step} / {len(self.solution)-1}"))
                time.sleep(self.speed_var.get())
            self.running = False

        threading.Thread(target=play, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app  = PuzzleApp(root)
    root.mainloop()
