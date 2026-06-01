import tkinter as tk
from tkinter import ttk, messagebox
import random
import threading
import time

from algorithms import bfs, dfs, dls, ids, ucs, greedy, astar, idastar, simple_hill_climbing, is_solvable, GOAL

GOAL_STATE = GOAL  # [1,2,3,4,5,6,7,8,0]

COLORS = {
    "bg": "#1e1e2e",
    "tile": "#89b4fa",
    "tile_text": "#1e1e2e",
    "empty": "#313244",
    "btn": "#cba6f7",
    "btn_text": "#1e1e2e",
    "panel": "#181825",
    "text": "#cdd6f4",
    "accent": "#a6e3a1",
    "step_bg": "#313244",
    "step_hl": "#f38ba8",
}

class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle Solver")
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(False, False)

        self.state = [1, 2, 3, 4, 5, 0, 7, 8, 6]  # trang thai mac dinh
        self.solution = []
        self.current_step = 0
        self.running = False
        self.dls_limit = tk.IntVar(value=20)

        self._build_ui()
        self._draw_board()

    def _build_ui(self):
        # --- Left panel: board + controls ---
        left = tk.Frame(self.root, bg=COLORS["bg"], padx=16, pady=16)
        left.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(left, text="8 Puzzle Solver", font=("Courier", 18, "bold"),
                 bg=COLORS["bg"], fg=COLORS["btn"]).pack(pady=(0, 12))

        # Board canvas
        self.canvas = tk.Canvas(left, width=270, height=270, bg=COLORS["panel"],
                                highlightthickness=2, highlightbackground=COLORS["btn"])
        self.canvas.pack()

        # Controls
        ctrl = tk.Frame(left, bg=COLORS["bg"])
        ctrl.pack(pady=10, fill=tk.X)

        tk.Button(ctrl, text="Shuffle", command=self.shuffle,
                  bg=COLORS["btn"], fg=COLORS["btn_text"],
                  font=("Courier", 10, "bold"), relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=4)

        tk.Button(ctrl, text="Reset", command=self.reset,
                  bg=COLORS["step_bg"], fg=COLORS["text"],
                  font=("Courier", 10), relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=4)

        tk.Button(ctrl, text="Clear Log", command=self.clear_log,
                  bg=COLORS["step_bg"], fg=COLORS["text"],
                  font=("Courier", 10), relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=4)

        # Algorithm selection
        algo_frame = tk.Frame(left, bg=COLORS["bg"])
        algo_frame.pack(fill=tk.X, pady=4)

        tk.Label(algo_frame, text="Algorithm:", font=("Courier", 11),
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(side=tk.LEFT)

        self.algo_var = tk.StringVar(value="BFS")
        algo_menu = ttk.Combobox(algo_frame, textvariable=self.algo_var,
                                 values=["BFS", "DFS", "DLS", "IDS", "UCS", "Greedy", "A*", "IDA*", "Hill Climbing"],
                                 width=13, state="readonly", font=("Courier", 11))
        algo_menu.pack(side=tk.LEFT, padx=8)
        algo_menu.bind("<<ComboboxSelected>>", self._on_algo_change)

        # DLS limit (chi hien thi khi chon DLS)
        self.dls_frame = tk.Frame(left, bg=COLORS["bg"])
        tk.Label(self.dls_frame, text="Depth Limit:", font=("Courier", 10),
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(side=tk.LEFT)
        tk.Spinbox(self.dls_frame, from_=1, to=50, textvariable=self.dls_limit,
                   width=5, font=("Courier", 10)).pack(side=tk.LEFT, padx=6)

        # Solve button
        self.solve_btn = tk.Button(left, text="▶  SOLVE", command=self.solve,
                                   bg=COLORS["accent"], fg=COLORS["btn_text"],
                                   font=("Courier", 12, "bold"), relief=tk.FLAT, pady=6)
        self.solve_btn.pack(fill=tk.X, pady=4)

        # Step controls
        step_ctrl = tk.Frame(left, bg=COLORS["bg"])
        step_ctrl.pack(fill=tk.X, pady=2)

        tk.Button(step_ctrl, text="◀ Prev", command=self.prev_step,
                  bg=COLORS["step_bg"], fg=COLORS["text"],
                  font=("Courier", 10), relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=4)

        tk.Button(step_ctrl, text="Next ▶", command=self.next_step,
                  bg=COLORS["step_bg"], fg=COLORS["text"],
                  font=("Courier", 10), relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=4)

        tk.Button(step_ctrl, text="Auto ▶▶", command=self.auto_play,
                  bg=COLORS["step_bg"], fg=COLORS["text"],
                  font=("Courier", 10), relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=4)

        # Speed slider
        spd_frame = tk.Frame(left, bg=COLORS["bg"])
        spd_frame.pack(fill=tk.X, pady=2)
        tk.Label(spd_frame, text="Speed:", font=("Courier", 9),
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(side=tk.LEFT)
        self.speed_var = tk.DoubleVar(value=0.5)
        tk.Scale(spd_frame, from_=0.1, to=2.0, resolution=0.1, orient=tk.HORIZONTAL,
                 variable=self.speed_var, bg=COLORS["bg"], fg=COLORS["text"],
                 highlightthickness=0, length=160, troughcolor=COLORS["step_bg"]).pack(side=tk.LEFT)

        # Status label
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(left, textvariable=self.status_var, font=("Courier", 10),
                 bg=COLORS["bg"], fg=COLORS["accent"]).pack(pady=4)

        # --- Right panel: steps log ---
        right = tk.Frame(self.root, bg=COLORS["panel"], padx=10, pady=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(right, text="Solution Steps", font=("Courier", 13, "bold"),
                 bg=COLORS["panel"], fg=COLORS["btn"]).pack(anchor=tk.W)

        self.step_info = tk.StringVar(value="Step: - / -")
        tk.Label(right, textvariable=self.step_info, font=("Courier", 10),
                 bg=COLORS["panel"], fg=COLORS["text"]).pack(anchor=tk.W)

        # Scrollable text area cho steps
        frame_log = tk.Frame(right, bg=COLORS["panel"])
        frame_log.pack(fill=tk.BOTH, expand=True, pady=6)

        scrollbar = tk.Scrollbar(frame_log)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text = tk.Text(frame_log, width=32, font=("Courier", 9),
                                bg=COLORS["step_bg"], fg=COLORS["text"],
                                yscrollcommand=scrollbar.set, relief=tk.FLAT,
                                state=tk.DISABLED, spacing1=2)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)

        self.log_text.tag_config("highlight", background=COLORS["step_hl"], foreground="#1e1e2e")
        self.log_text.tag_config("header", foreground=COLORS["btn"])
        self.log_text.tag_config("info", foreground=COLORS["accent"])

    def _on_algo_change(self, event=None):
        if self.algo_var.get() == "DLS":
            self.dls_frame.pack(fill=tk.X, pady=2)
        else:
            self.dls_frame.pack_forget()

    def _draw_board(self, state=None):
        if state is None:
            state = self.state
        self.canvas.delete("all")
        size = 84
        pad = 6
        for i, val in enumerate(state):
            r, c = i // 3, i % 3
            x1 = c * (size + pad) + pad
            y1 = r * (size + pad) + pad
            x2 = x1 + size
            y2 = y1 + size
            if val == 0:
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=COLORS["empty"], outline="")
            else:
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=COLORS["tile"], outline="")
                self.canvas.create_text((x1+x2)//2, (y1+y2)//2, text=str(val),
                                        font=("Courier", 26, "bold"), fill=COLORS["tile_text"])

    def _log(self, text, tag=None):
        self.log_text.config(state=tk.NORMAL)
        if tag:
            self.log_text.insert(tk.END, text + "\n", tag)
        else:
            self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _log_step(self, idx, state, highlight=False):
        lines = []
        lines.append(f"Step {idx}:")
        for r in range(3):
            row = state[r*3:(r+1)*3]
            lines.append("  " + " ".join(str(v) if v != 0 else "_" for v in row))
        text = "\n".join(lines) + "\n"
        self.log_text.config(state=tk.NORMAL)
        tag = "highlight" if highlight else None
        if tag:
            self.log_text.insert(tk.END, text, tag)
        else:
            self.log_text.insert(tk.END, text)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

    def shuffle(self):
        import random
        while True:
            s = list(range(9))
            random.shuffle(s)
            if is_solvable(s):
                break
        self.state = s
        self.solution = []
        self.current_step = 0
        self.status_var.set("Shuffled - Press SOLVE")
        self.step_info.set("Step: - / -")
        self._draw_board()

    def reset(self):
        self.state = [1, 2, 3, 4, 5, 0, 7, 8, 6]
        self.solution = []
        self.current_step = 0
        self.status_var.set("Reset")
        self.step_info.set("Step: - / -")
        self._draw_board()
        self.clear_log()

    def solve(self):
        algo = self.algo_var.get()
        start = self.state[:]
        goal = GOAL_STATE

        if not is_solvable(start):
            messagebox.showerror("Error", "Puzzle khong co loi giai!")
            return

        self.clear_log()
        self._log(f"[{algo}] Dang tim kiem...", "info")
        self.status_var.set("Solving...")
        self.solve_btn.config(state=tk.DISABLED)

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
            elapsed = time.time() - t0

            self.root.after(0, lambda: self._on_solve_done(result, nodes, elapsed, algo))

        threading.Thread(target=run, daemon=True).start()

    def _on_solve_done(self, result, nodes, elapsed, algo):
        self.solve_btn.config(state=tk.NORMAL)
        if result is None:
            self.status_var.set("Khong tim duoc loi giai!")
            if algo == "Hill Climbing":
                self._log("Bi ket tai cuc bo (local optimum)!", "highlight")
                self._log("Hill Climbing khong thoat duoc.", "highlight")
            else:
                self._log("Khong tim duoc loi giai.", "highlight")
            return

        self.solution = result
        self.current_step = 0
        steps = len(result) - 1

        self.status_var.set(f"Tim duoc! {steps} buoc | {nodes} nodes | {elapsed:.3f}s")
        self._log(f"[{algo}] Ket qua:", "header")
        self._log(f"  So buoc: {steps}", "info")
        self._log(f"  Nodes mo rong: {nodes}", "info")
        self._log(f"  Thoi gian: {elapsed:.4f}s", "info")
        self._log("─" * 24)

        for i, s in enumerate(self.solution):
            self._log_step(i, s)

        self._draw_board(self.solution[0])
        self.step_info.set(f"Step: 0 / {steps}")

    def next_step(self):
        if not self.solution:
            return
        if self.current_step < len(self.solution) - 1:
            self.current_step += 1
            self._draw_board(self.solution[self.current_step])
            self.step_info.set(f"Step: {self.current_step} / {len(self.solution)-1}")

    def prev_step(self):
        if not self.solution:
            return
        if self.current_step > 0:
            self.current_step -= 1
            self._draw_board(self.solution[self.current_step])
            self.step_info.set(f"Step: {self.current_step} / {len(self.solution)-1}")

    def auto_play(self):
        if not self.solution or self.running:
            return
        self.running = True

        def play():
            while self.current_step < len(self.solution) - 1 and self.running:
                self.current_step += 1
                self.root.after(0, lambda s=self.solution[self.current_step]: self._draw_board(s))
                self.root.after(0, lambda: self.step_info.set(
                    f"Step: {self.current_step} / {len(self.solution)-1}"))
                time.sleep(self.speed_var.get())
            self.running = False

        threading.Thread(target=play, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleApp(root)
    root.mainloop()
