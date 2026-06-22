import tkinter as tk
from tkinter import ttk, messagebox
import random
import threading
import time

from algorithms import (bfs, dfs, dls, ids, ucs, greedy, astar, idastar,
                        simple_hill_climbing, stochastic_hill_climbing,
                        random_restart_hill_climbing, local_beam_search,
                        simulated_annealing, and_or_search, sensorless_search,
                        minimax, alpha_beta, expectimax,
                        backtracking_csp, forward_checking, ac3,
                        is_solvable, GOAL)

GOAL_STATE = GOAL

# ── Màu sắc ──────────────────────────────────────────────────────────────────
BG        = "#1a1b26"
PANEL     = "#16161e"
TILE_CLR  = "#7aa2f7"
TILE_TXT  = "#1a1b26"
EMPTY_CLR = "#24283b"
ACCENT    = "#9ece6a"
WARN      = "#f7768e"
MUTED     = "#565f89"
TEXT      = "#c0caf5"
HEADER    = "#bb9af7"
BTN_ACT   = "#7aa2f7"
BTN_NRM   = "#292e42"
BORDER    = "#3b4261"

FONT_MONO = "Courier"

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
        ("Hill Climbing",      "Simple Hill Climbing"),
        ("Stochastic HC",      "Stochastic HC"),
        ("Random Restart HC",  "Random Restart HC"),
        ("Local Beam",         "Local Beam Search"),
        ("Simulated Annealing","Simulated Annealing"),
    ]),
    ("Non-deterministic", [
        ("AND-OR Search",    "AND-OR Search"),
        ("Sensorless Search","Sensorless / Belief State"),
    ]),
    ("Adversarial Search", [
        ("Minimax",     "Minimax Search"),
        ("Alpha-Beta",  "Alpha-Beta Pruning"),
        ("Expectimax",  "Expectimax Search"),
    ]),
    ("Constraint Satisfaction", [
        ("Backtracking CSP", "Backtracking Search"),
        ("Forward Checking", "Forward Checking"),
        ("AC-3",             "Arc Consistency AC-3"),
    ]),
]

ALL_ALGOS = [algo for _, algos in ALGO_GROUPS for algo, _ in algos]


class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle Solver")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        # Lay kich thuoc man hinh va dat cua so full
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{sw}x{sh}+0+0")
        self.root.state("zoomed")  # Windows: maximize

        self.state        = [1, 2, 3, 4, 5, 0, 7, 8, 6]
        self.solution     = []
        self.current_step = 0
        self.running      = False
        self.dls_limit    = tk.IntVar(value=20)
        self.beam_k       = tk.IntVar(value=3)
        self.algo_var     = tk.StringVar(value="BFS")
        self.speed_var    = tk.DoubleVar(value=0.4)

        self._build_ui()
        self._draw_board()

    # ── Build UI ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        # 3 cột chính
        col_board = tk.Frame(self.root, bg=BG, padx=18, pady=18)
        col_board.pack(side=tk.LEFT, fill=tk.Y)

        col_algo = tk.Frame(self.root, bg=PANEL, padx=14, pady=18)
        col_algo.pack(side=tk.LEFT, fill=tk.Y)

        col_log = tk.Frame(self.root, bg=PANEL, padx=14, pady=18)
        col_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_board_col(col_board)
        self._build_algo_col(col_algo)
        self._build_log_col(col_log)

    # ── Cột 1: Board + điều khiển ────────────────────────────────────────────

    def _build_board_col(self, parent):
        tk.Label(parent, text="8 Puzzle Solver",
                 font=(FONT_MONO, 16, "bold"),
                 bg=BG, fg=HEADER).pack(pady=(0, 12))

        # Board
        self.canvas = tk.Canvas(parent, width=285, height=285,
                                bg=PANEL, highlightthickness=1,
                                highlightbackground=BORDER)
        self.canvas.pack()

        # Nút Shuffle / Reset
        row1 = tk.Frame(parent, bg=BG)
        row1.pack(fill=tk.X, pady=(12, 4))

        self._btn(row1, "🔀  Shuffle", self.shuffle, BTN_ACT, TILE_TXT, bold=True).pack(side=tk.LEFT, padx=(0,6), fill=tk.X, expand=True)
        self._btn(row1, "↺  Reset",   self.reset,   BTN_NRM, TEXT).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Nút SOLVE
        self.solve_btn = tk.Button(parent, text="▶   SOLVE",
                                   command=self.solve,
                                   bg=ACCENT, fg=TILE_TXT,
                                   font=(FONT_MONO, 12, "bold"),
                                   relief=tk.FLAT, pady=8, cursor="hand2")
        self.solve_btn.pack(fill=tk.X, pady=(10, 4))

        # Điều khiển từng bước
        sep = tk.Frame(parent, bg=BORDER, height=1)
        sep.pack(fill=tk.X, pady=6)

        self.step_info = tk.StringVar(value="Step: — / —")
        tk.Label(parent, textvariable=self.step_info,
                 font=(FONT_MONO, 9), bg=BG, fg=MUTED).pack(anchor=tk.W)

        row2 = tk.Frame(parent, bg=BG)
        row2.pack(fill=tk.X, pady=4)
        self._btn(row2, "◀ Prev", self.prev_step, BTN_NRM, TEXT).pack(side=tk.LEFT, padx=(0,4), fill=tk.X, expand=True)
        self._btn(row2, "Next ▶", self.next_step, BTN_NRM, TEXT).pack(side=tk.LEFT, padx=(0,4), fill=tk.X, expand=True)
        self._btn(row2, "▶▶ Auto", self.auto_play, BTN_NRM, TEXT).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Speed
        row3 = tk.Frame(parent, bg=BG)
        row3.pack(fill=tk.X, pady=(4, 0))
        tk.Label(row3, text="Speed:", font=(FONT_MONO, 9),
                 bg=BG, fg=MUTED).pack(side=tk.LEFT)
        tk.Scale(row3, from_=0.05, to=1.5, resolution=0.05,
                 orient=tk.HORIZONTAL, variable=self.speed_var,
                 bg=BG, fg=TEXT, highlightthickness=0,
                 troughcolor=BTN_NRM, length=180,
                 showvalue=False).pack(side=tk.LEFT, padx=6)

        # Khung tham số (hiện tuỳ theo algo)
        self.param_frame = tk.Frame(parent, bg=BG)
        self.param_frame.pack(fill=tk.X, pady=(6, 0))

        # Status
        self.status_var = tk.StringVar(value="Chon thuat toan va nhan SOLVE")
        tk.Label(parent, textvariable=self.status_var,
                 font=(FONT_MONO, 8), bg=BG, fg=MUTED,
                 wraplength=280, justify=tk.LEFT).pack(anchor=tk.W, pady=(8, 0))

    # ── Cột 2: Chọn thuật toán theo nhóm ─────────────────────────────────────

    def _build_algo_col(self, parent):
        tk.Label(parent, text="Algorithm", font=(FONT_MONO, 13, "bold"),
                 bg=PANEL, fg=HEADER).pack(anchor=tk.W, pady=(0, 6))

        self.algo_var.trace_add("write", lambda *_: self._on_algo_change())

        # Scrollable frame cho danh sach thuat toan
        canvas = tk.Canvas(parent, bg=PANEL, highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=PANEL)

        scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        for group_name, algos in ALGO_GROUPS:
            tk.Label(scroll_frame, text=group_name.upper(),
                     font=(FONT_MONO, 8, "bold"),
                     bg=PANEL, fg=MUTED).pack(anchor=tk.W, pady=(8, 2))

            tk.Frame(scroll_frame, bg=BORDER, height=1).pack(fill=tk.X, pady=(0, 4))

            for key, desc in algos:
                row = tk.Frame(scroll_frame, bg=PANEL)
                row.pack(fill=tk.X, pady=1)

                rb = tk.Radiobutton(row, variable=self.algo_var, value=key,
                                    text=key,
                                    font=(FONT_MONO, 10, "bold"),
                                    bg=PANEL, fg=TEXT,
                                    activebackground=PANEL,
                                    activeforeground=HEADER,
                                    selectcolor=PANEL,
                                    indicatoron=True,
                                    cursor="hand2",
                                    relief=tk.FLAT)
                rb.pack(side=tk.LEFT)

                tk.Label(row, text=f"  {desc}",
                         font=(FONT_MONO, 8),
                         bg=PANEL, fg=MUTED).pack(side=tk.LEFT)

        # Bind mouse scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # ── Cột 3: Log kết quả ───────────────────────────────────────────────────

    def _build_log_col(self, parent):
        header_row = tk.Frame(parent, bg=PANEL)
        header_row.pack(fill=tk.X, pady=(0, 8))

        tk.Label(header_row, text="Solution Log",
                 font=(FONT_MONO, 13, "bold"),
                 bg=PANEL, fg=HEADER).pack(side=tk.LEFT)

        self._btn(header_row, "Clear", self.clear_log, BTN_NRM, MUTED,
                  font_size=8).pack(side=tk.RIGHT)

        # Stats bar
        self.stats_var = tk.StringVar(value="")
        self.stats_lbl = tk.Label(parent, textvariable=self.stats_var,
                                  font=(FONT_MONO, 9),
                                  bg=PANEL, fg=ACCENT,
                                  anchor=tk.W, justify=tk.LEFT)
        self.stats_lbl.pack(fill=tk.X, pady=(0, 6))

        # Log text
        frame_log = tk.Frame(parent, bg=PANEL)
        frame_log.pack(fill=tk.BOTH, expand=True)

        sb = tk.Scrollbar(frame_log)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text = tk.Text(frame_log, width=30,
                                font=(FONT_MONO, 9),
                                bg=EMPTY_CLR, fg=TEXT,
                                yscrollcommand=sb.set,
                                relief=tk.FLAT,
                                state=tk.DISABLED,
                                spacing1=3,
                                padx=8, pady=6)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.config(command=self.log_text.yview)

        self.log_text.tag_config("err",    foreground=WARN,   font=(FONT_MONO, 9, "bold"))
        self.log_text.tag_config("ok",     foreground=ACCENT, font=(FONT_MONO, 9, "bold"))
        self.log_text.tag_config("header", foreground=HEADER, font=(FONT_MONO, 9, "bold"))
        self.log_text.tag_config("muted",  foreground=MUTED)
        self.log_text.tag_config("step",   foreground=TEXT)
        self.log_text.tag_config("cur",    background=BTN_ACT, foreground=TILE_TXT)

    # ── Helper tạo button ─────────────────────────────────────────────────────

    def _btn(self, parent, text, cmd, bg, fg, bold=False, font_size=9):
        style = "bold" if bold else ""
        return tk.Button(parent, text=text, command=cmd,
                         bg=bg, fg=fg,
                         font=(FONT_MONO, font_size, style),
                         relief=tk.FLAT, padx=8, pady=4,
                         cursor="hand2",
                         activebackground=HEADER,
                         activeforeground=TILE_TXT)

    # ── Vẽ board ──────────────────────────────────────────────────────────────

    def _draw_board(self, state=None):
        if state is None:
            state = self.state
        self.canvas.delete("all")
        size = 88
        pad  = 5
        for i, val in enumerate(state):
            r, c = i // 3, i % 3
            x1 = c * (size + pad) + pad
            y1 = r * (size + pad) + pad
            x2, y2 = x1 + size, y1 + size
            if val == 0:
                self.canvas.create_rectangle(x1, y1, x2, y2,
                                             fill=EMPTY_CLR, outline=BORDER, width=1)
            else:
                self.canvas.create_rectangle(x1, y1, x2, y2,
                                             fill=TILE_CLR, outline="", width=0)
                self.canvas.create_text((x1+x2)//2, (y1+y2)//2,
                                        text=str(val),
                                        font=(FONT_MONO, 28, "bold"),
                                        fill=TILE_TXT)

    # ── Log helpers ───────────────────────────────────────────────────────────

    def _log(self, text, tag="step"):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, text + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _log_step(self, idx, state, current=False):
        tag = "cur" if current else "step"
        lines = [f"Step {idx}:"]
        for r in range(3):
            row = state[r*3:(r+1)*3]
            lines.append("  " + " ".join(str(v) if v != 0 else "·" for v in row))
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, "\n".join(lines) + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.stats_var.set("")

    # ── Algo change → hiện/ẩn tham số ────────────────────────────────────────

    def _on_algo_change(self):
        for w in self.param_frame.winfo_children():
            w.destroy()

        algo = self.algo_var.get()
        if algo == "DLS":
            tk.Label(self.param_frame, text="Depth Limit:",
                     font=(FONT_MONO, 9), bg=BG, fg=MUTED).pack(side=tk.LEFT)
            tk.Spinbox(self.param_frame, from_=1, to=50,
                       textvariable=self.dls_limit, width=5,
                       font=(FONT_MONO, 9), bg=BTN_NRM, fg=TEXT,
                       buttonbackground=BTN_NRM, relief=tk.FLAT).pack(side=tk.LEFT, padx=6)

        elif algo == "Local Beam":
            tk.Label(self.param_frame, text="Beam k:",
                     font=(FONT_MONO, 9), bg=BG, fg=MUTED).pack(side=tk.LEFT)
            tk.Spinbox(self.param_frame, from_=1, to=20,
                       textvariable=self.beam_k, width=5,
                       font=(FONT_MONO, 9), bg=BTN_NRM, fg=TEXT,
                       buttonbackground=BTN_NRM, relief=tk.FLAT).pack(side=tk.LEFT, padx=6)

    # ── Shuffle / Reset ───────────────────────────────────────────────────────

    def shuffle(self):
        while True:
            s = list(range(9))
            random.shuffle(s)
            if is_solvable(s):
                break
        self.state        = s
        self.solution     = []
        self.current_step = 0
        self.stats_var.set("")
        self.step_info.set("Step: — / —")
        self.status_var.set("Shuffled — nhan SOLVE de giai")
        self._draw_board()

    def reset(self):
        self.state        = [1, 2, 3, 4, 5, 0, 7, 8, 6]
        self.solution     = []
        self.current_step = 0
        self.stats_var.set("")
        self.step_info.set("Step: — / —")
        self.status_var.set("Reset")
        self._draw_board()
        self.clear_log()

    # ── Solve ─────────────────────────────────────────────────────────────────

    def solve(self):
        algo  = self.algo_var.get()
        start = self.state[:]
        goal  = GOAL_STATE

        # CSP khong can kiem tra is_solvable theo cach thong thuong
        csp_algos = ["Backtracking CSP", "Forward Checking", "AC-3"]
        if algo not in csp_algos and not is_solvable(start):
            messagebox.showerror("Lỗi", "Puzzle không có lời giải!")
            return

        self.clear_log()
        self._log(f"Đang chạy {algo}...", "muted")
        self.status_var.set(f"Solving — {algo}...")
        self.solve_btn.config(state=tk.DISABLED, text="⏳  Solving...")

        def run():
            t0 = time.time()
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
            elapsed = time.time() - t0
            self.root.after(0, lambda: self._on_solve_done(result, nodes, elapsed, algo))

        threading.Thread(target=run, daemon=True).start()

    def _on_solve_done(self, result, nodes, elapsed, algo):
        self.solve_btn.config(state=tk.NORMAL, text="▶   SOLVE")

        if result is None:
            self.status_var.set("Không tìm được lời giải")
            self.stats_var.set(f"✗  {algo}  |  {nodes} nodes  |  {elapsed:.3f}s")
            self._log(f"✗  Không tìm được lời giải", "err")
            self._log(f"   Nodes mở rộng: {nodes}", "muted")
            self._log(f"   Thời gian: {elapsed:.4f}s", "muted")
            return

        self.solution     = result
        self.current_step = 0
        steps = len(result) - 1

        self.status_var.set(f"✓  {steps} bước  |  {nodes} nodes  |  {elapsed:.3f}s")
        self.stats_var.set(f"✓  {algo}  |  {steps} bước  |  {nodes} nodes  |  {elapsed:.3f}s")
        self.step_info.set(f"Step: 0 / {steps}")

        self._log(f"✓  {algo}", "ok")
        self._log(f"   Số bước    : {steps}", "muted")
        self._log(f"   Nodes      : {nodes}", "muted")
        self._log(f"   Thời gian  : {elapsed:.4f}s", "muted")
        self._log("─" * 26, "muted")
        for i, s in enumerate(self.solution):
            self._log_step(i, s, current=(i == 0))

        self._draw_board(self.solution[0])

    # ── Điều khiển từng bước ──────────────────────────────────────────────────

    def _highlight_current_step(self):
        self.step_info.set(f"Step: {self.current_step} / {len(self.solution)-1}")
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
                    f"Step: {self.current_step} / {len(self.solution)-1}"))
                time.sleep(self.speed_var.get())
            self.running = False

        threading.Thread(target=play, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app  = PuzzleApp(root)
    root.mainloop()
