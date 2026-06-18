import tkinter as tk
from tkinter import messagebox
import random
import threading
import time

from algorithms import (bfs, dfs, dls, ids, ucs, greedy, astar, idastar,
                        simple_hill_climbing, stochastic_hill_climbing,
                        random_restart_hill_climbing, local_beam_search,
                        simulated_annealing, and_or_search, sensorless_search,
                        backtracking_search, forward_checking_search, ac3_search,
                        is_solvable, GOAL)

GOAL_STATE = GOAL

# ══════════════════════════════════════════════════════════════════════════════
#  DESIGN TOKENS
# ══════════════════════════════════════════════════════════════════════════════

# ── Colors ────────────────────────────────────────────────────────────────────
BG_ROOT        = "#0f0f1a"
BG_SIDEBAR     = "#141422"
BG_CARD        = "#1a1a2e"
BG_INPUT       = "#1e1e35"
TILE_BODY      = "#6c63ff"
TILE_HIGHLIGHT = "#8b85ff"
TILE_SHADOW    = "#0a0a15"
EMPTY_SLOT     = "#1e1e32"
ACCENT_BLUE    = "#7aa2f7"
ACCENT_GREEN   = "#9ece6a"
ACCENT_GREEN_H = "#b5e278"
ACCENT_PURPLE  = "#bb9af7"
ACCENT_PINK    = "#f7768e"
ACCENT_CYAN    = "#7dcfff"
TEXT_WHITE     = "#ffffff"
TEXT_PRIMARY   = "#e0e0f0"
TEXT_SECONDARY = "#a0a0c0"
TEXT_MUTED     = "#565f89"
TEXT_DIM       = "#3d4466"
BORDER         = "#2a2a40"
BORDER_LIGHT   = "#3b4261"
SELECTED_BG    = "#1f1f3a"
SELECTED_LEFT  = "#bb9af7"
HOVER_BG       = "#1a1a30"

# ── Fonts ─────────────────────────────────────────────────────────────────────
F_LOGO       = ("Segoe UI", 16, "bold")
F_HEADER     = ("Segoe UI", 13, "bold")
F_SUBHEADER  = ("Segoe UI", 10, "bold")
F_BODY       = ("Segoe UI", 10)
F_SMALL      = ("Segoe UI", 9)
F_TINY       = ("Segoe UI", 8)
F_MONO       = ("Consolas", 9)
F_MONO_BOLD  = ("Consolas", 9, "bold")
F_TILE       = ("Segoe UI", 26, "bold")
F_BTN        = ("Segoe UI", 10, "bold")
F_BTN_LG     = ("Segoe UI", 12, "bold")
F_STAT_VAL   = ("Segoe UI", 16, "bold")
F_STAT_ALGO  = ("Segoe UI", 11, "bold")
F_STAT_LBL   = ("Segoe UI", 8)
F_GROUP_HDR  = ("Segoe UI", 9, "bold")

# ── Dimensions ────────────────────────────────────────────────────────────────
WIN_W        = 1200
WIN_H        = 700
SIDEBAR_W    = 260
RIGHT_W      = 320
BOARD_SIZE   = 350
TILE_SIZE    = 100
TILE_GAP     = 10
TILE_RADIUS  = 14
BOARD_PAD    = 15
SHADOW_OFF   = 3

# ── Algorithm Groups ─────────────────────────────────────────────────────────
ALGO_GROUPS = [
    ("Uninformed Search", "🔍", [
        ("BFS",  "Breadth-First Search"),
        ("DFS",  "Depth-First Search"),
        ("DLS",  "Depth-Limited Search"),
        ("IDS",  "Iterative Deepening"),
        ("UCS",  "Uniform Cost Search"),
    ]),
    ("Informed Search", "🧠", [
        ("Greedy", "Greedy Best-First"),
        ("A*",     "A* Search"),
        ("IDA*",   "Iterative Deepening A*"),
    ]),
    ("Local Search", "📍", [
        ("Hill Climbing",       "Simple Hill Climbing"),
        ("Stochastic HC",       "Stochastic HC"),
        ("Random Restart HC",   "Random Restart HC"),
        ("Local Beam",          "Local Beam Search"),
        ("Simulated Annealing", "Simulated Annealing"),
    ]),
    ("Non-deterministic", "🎲", [
        ("AND-OR Search",     "AND-OR Search"),
        ("Sensorless Search", "Sensorless / Belief State"),
    ]),
    ("Constraint Satisfaction", "🔒", [
        ("Backtracking CSP",    "Backtracking Search"),
        ("Forward Checking",    "Forward Checking"),
        ("AC-3",                "Arc Consistency AC-3"),
    ]),
]

ALL_ALGOS = [algo for _, _, algos in ALGO_GROUPS for algo, _ in algos]


# ══════════════════════════════════════════════════════════════════════════════
#  APPLICATION
# ══════════════════════════════════════════════════════════════════════════════

class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle Solver")
        self.root.configure(bg=BG_ROOT)
        self.root.resizable(True, True)

        # Centre window on screen
        self.root.geometry(f"{WIN_W}x{WIN_H}")
        self.root.update_idletasks()
        sx = (self.root.winfo_screenwidth()  - WIN_W) // 2
        sy = (self.root.winfo_screenheight() - WIN_H) // 2
        self.root.geometry(f"{WIN_W}x{WIN_H}+{sx}+{sy}")

        # ── State ──
        self.state        = [1, 2, 3, 4, 5, 0, 7, 8, 6]
        self.solution     = []
        self.current_step = 0
        self.running      = False
        self.dls_limit    = tk.IntVar(value=20)
        self.beam_k       = tk.IntVar(value=3)
        self.algo_var     = tk.StringVar(value="BFS")
        self.speed_var    = tk.DoubleVar(value=0.4)
        self.is_fullscreen = False

        # ── UI bookkeeping ──
        self.algo_items      = {}       # key → dict of widget refs
        self.group_frames    = {}       # group_name → content Frame
        self.group_arrows    = {}       # group_name → arrow Label
        self.group_expanded  = {}       # group_name → bool
        self.stat_labels     = {}       # stat_id → value Label

        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)

        self._build_ui()
        self._draw_board()
        self._update_algo_selection()

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)
        if hasattr(self, "fs_btn"):
            if self.is_fullscreen:
                self.fs_btn.config(text="🗗  Exit Full")
            else:
                self.fs_btn.config(text="⛶  Fullscreen")

    def exit_fullscreen(self, event=None):
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.root.attributes("-fullscreen", False)
            if hasattr(self, "fs_btn"):
                self.fs_btn.config(text="⛶  Fullscreen")

    # ══════════════════════════════════════════════════════════════════════════
    #  LAYOUT SKELETON
    # ══════════════════════════════════════════════════════════════════════════

    def _build_ui(self):
        main = tk.Frame(self.root, bg=BG_ROOT)
        main.pack(fill=tk.BOTH, expand=True)

        # ── Left sidebar ──
        sidebar = tk.Frame(main, bg=BG_SIDEBAR, width=SIDEBAR_W)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Frame(main, bg=BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y)

        # ── Right panel ──
        right = tk.Frame(main, bg=BG_CARD, width=RIGHT_W)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        right.pack_propagate(False)

        tk.Frame(main, bg=BORDER, width=1).pack(side=tk.RIGHT, fill=tk.Y)

        # ── Centre ──
        centre = tk.Frame(main, bg=BG_ROOT)
        centre.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_sidebar(sidebar)
        self._build_centre(centre)
        self._build_right_panel(right)

    # ══════════════════════════════════════════════════════════════════════════
    #  SIDEBAR
    # ══════════════════════════════════════════════════════════════════════════

    def _build_sidebar(self, parent):
        # ── Logo ──
        logo_f = tk.Frame(parent, bg=BG_SIDEBAR, pady=16, padx=16)
        logo_f.pack(fill=tk.X)

        tk.Label(logo_f, text="🧩", font=("Segoe UI", 22),
                 bg=BG_SIDEBAR, fg=TEXT_WHITE).pack(side=tk.LEFT)

        lt = tk.Frame(logo_f, bg=BG_SIDEBAR)
        lt.pack(side=tk.LEFT, padx=(10, 0))
        tk.Label(lt, text="8 Puzzle", font=F_LOGO,
                 bg=BG_SIDEBAR, fg=TEXT_WHITE).pack(anchor=tk.W)
        tk.Label(lt, text="Solver", font=F_SMALL,
                 bg=BG_SIDEBAR, fg=ACCENT_PURPLE).pack(anchor=tk.W)

        tk.Frame(parent, bg=BORDER, height=1).pack(fill=tk.X, padx=12)

        # ── Scrollable algorithm area ──
        algo_outer = tk.Frame(parent, bg=BG_SIDEBAR)
        algo_outer.pack(fill=tk.BOTH, expand=True)

        algo_canvas = tk.Canvas(algo_outer, bg=BG_SIDEBAR,
                                highlightthickness=0, borderwidth=0)
        algo_sb = tk.Scrollbar(algo_outer, orient=tk.VERTICAL,
                               command=algo_canvas.yview)
        self._algo_inner = tk.Frame(algo_canvas, bg=BG_SIDEBAR)

        self._algo_inner.bind(
            "<Configure>",
            lambda e: algo_canvas.configure(scrollregion=algo_canvas.bbox("all"))
        )
        algo_canvas.create_window((0, 0), window=self._algo_inner,
                                  anchor=tk.NW, width=SIDEBAR_W - 14)
        algo_canvas.configure(yscrollcommand=algo_sb.set)

        algo_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        algo_sb.pack(side=tk.RIGHT, fill=tk.Y)

        # Mouse-wheel scrolling
        def _on_mousewheel(e):
            algo_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        algo_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Section title
        tk.Label(self._algo_inner, text="  ALGORITHMS", font=F_GROUP_HDR,
                 bg=BG_SIDEBAR, fg=TEXT_MUTED, anchor=tk.W,
                 pady=8).pack(fill=tk.X)

        for gname, icon, algos in ALGO_GROUPS:
            self._build_accordion(self._algo_inner, gname, icon, algos)

        # ── Parameters ──
        tk.Frame(parent, bg=BORDER, height=1).pack(fill=tk.X, padx=12, pady=(4, 0))

        self.param_frame = tk.Frame(parent, bg=BG_SIDEBAR, padx=16, pady=8)
        self.param_frame.pack(fill=tk.X)

        # ── Speed ──
        spd = tk.Frame(parent, bg=BG_SIDEBAR, padx=16)
        spd.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, 14))

        tk.Label(spd, text="⚡ Speed", font=F_SMALL,
                 bg=BG_SIDEBAR, fg=TEXT_MUTED).pack(anchor=tk.W)

        tk.Scale(spd, from_=0.05, to=1.5, resolution=0.05,
                 orient=tk.HORIZONTAL, variable=self.speed_var,
                 bg=BG_SIDEBAR, fg=TEXT_PRIMARY,
                 highlightthickness=0, troughcolor=BG_INPUT,
                 activebackground=ACCENT_BLUE, sliderrelief=tk.FLAT,
                 showvalue=True, font=F_TINY, length=210).pack(fill=tk.X)

    # ── Accordion helpers ─────────────────────────────────────────────────────

    def _build_accordion(self, parent, gname, icon, algos):
        grp = tk.Frame(parent, bg=BG_SIDEBAR)
        grp.pack(fill=tk.X)

        # Header
        hdr = tk.Frame(grp, bg=BG_SIDEBAR, padx=16, pady=6, cursor="hand2")
        hdr.pack(fill=tk.X)

        arrow = tk.Label(hdr, text="▾", font=F_TINY,
                         bg=BG_SIDEBAR, fg=TEXT_MUTED)
        arrow.pack(side=tk.LEFT)

        tk.Label(hdr, text=f"  {icon}  {gname}", font=F_SMALL,
                 bg=BG_SIDEBAR, fg=TEXT_SECONDARY).pack(side=tk.LEFT)

        # Content
        content = tk.Frame(grp, bg=BG_SIDEBAR)
        content.pack(fill=tk.X)

        for key, desc in algos:
            self._build_algo_item(content, key, desc)

        self.group_frames[gname]   = content
        self.group_arrows[gname]   = arrow
        self.group_expanded[gname] = True

        def toggle(e, g=gname):
            self._toggle_group(g)
        for w in (hdr, arrow) + tuple(hdr.winfo_children()):
            w.bind("<Button-1>", toggle)

    def _build_algo_item(self, parent, key, desc):
        item = tk.Frame(parent, bg=BG_SIDEBAR, cursor="hand2")
        item.pack(fill=tk.X, padx=8, pady=1)

        accent = tk.Frame(item, bg=BG_SIDEBAR, width=3)
        accent.pack(side=tk.LEFT, fill=tk.Y, padx=(4, 0))

        body = tk.Frame(item, bg=BG_SIDEBAR, padx=8, pady=5)
        body.pack(fill=tk.X, side=tk.LEFT, expand=True)

        nlbl = tk.Label(body, text=key, font=F_BODY,
                        bg=BG_SIDEBAR, fg=TEXT_PRIMARY, anchor=tk.W)
        nlbl.pack(fill=tk.X)

        dlbl = tk.Label(body, text=desc, font=F_TINY,
                        bg=BG_SIDEBAR, fg=TEXT_DIM, anchor=tk.W)
        dlbl.pack(fill=tk.X)

        refs = {"frame": item, "accent": accent, "body": body,
                "name": nlbl, "desc": dlbl}
        self.algo_items[key] = refs

        # Click
        def click(e=None, k=key):
            self.algo_var.set(k)
            self._update_algo_selection()
            self._on_algo_change()

        # Hover
        def enter(e=None, k=key, r=refs):
            if self.algo_var.get() != k:
                for w in (r["frame"], r["body"], r["name"], r["desc"]):
                    w.config(bg=HOVER_BG)

        def leave(e=None, k=key, r=refs):
            if self.algo_var.get() != k:
                for w in (r["frame"], r["body"], r["name"], r["desc"]):
                    w.config(bg=BG_SIDEBAR)

        for w in (item, body, nlbl, dlbl, accent):
            w.bind("<Button-1>", click)
            w.bind("<Enter>", enter)
            w.bind("<Leave>", leave)

    def _toggle_group(self, gname):
        if self.group_expanded[gname]:
            self.group_frames[gname].pack_forget()
            self.group_arrows[gname].config(text="▸")
        else:
            self.group_frames[gname].pack(fill=tk.X)
            self.group_arrows[gname].config(text="▾")
        self.group_expanded[gname] = not self.group_expanded[gname]

    def _update_algo_selection(self):
        sel = self.algo_var.get()
        for key, r in self.algo_items.items():
            if key == sel:
                for w in (r["frame"], r["body"], r["name"], r["desc"]):
                    w.config(bg=SELECTED_BG)
                r["accent"].config(bg=SELECTED_LEFT)
                r["name"].config(fg=ACCENT_PURPLE)
                r["desc"].config(fg=TEXT_MUTED)
            else:
                for w in (r["frame"], r["body"], r["name"], r["desc"]):
                    w.config(bg=BG_SIDEBAR)
                r["accent"].config(bg=BG_SIDEBAR)
                r["name"].config(fg=TEXT_PRIMARY)
                r["desc"].config(fg=TEXT_DIM)

    # ══════════════════════════════════════════════════════════════════════════
    #  CENTRE PANEL
    # ══════════════════════════════════════════════════════════════════════════

    def _build_centre(self, parent):
        wrapper = tk.Frame(parent, bg=BG_ROOT)
        wrapper.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # ── Board ──
        self.canvas = tk.Canvas(wrapper, width=BOARD_SIZE, height=BOARD_SIZE,
                                bg=BG_ROOT, highlightthickness=0)
        self.canvas.pack(pady=(0, 16))

        # ── Action buttons ──
        btn_row = tk.Frame(wrapper, bg=BG_ROOT)
        btn_row.pack(fill=tk.X, pady=(0, 8))

        self._styled_btn(btn_row, "🔀  Shuffle", self.shuffle,
                         BG_INPUT, TEXT_PRIMARY).pack(
            side=tk.LEFT, padx=(0, 6), fill=tk.X, expand=True)

        self._styled_btn(btn_row, "↺  Reset", self.reset,
                         BG_INPUT, TEXT_PRIMARY).pack(
            side=tk.LEFT, fill=tk.X, expand=True)

        # ── SOLVE button ──
        self.solve_btn = tk.Button(wrapper, text="▶   SOLVE",
                                   command=self.solve,
                                   bg=ACCENT_GREEN, fg="#1a1b26",
                                   font=F_BTN_LG, relief=tk.FLAT,
                                   pady=10, cursor="hand2",
                                   activebackground=ACCENT_GREEN_H,
                                   activeforeground="#1a1b26")
        self.solve_btn.pack(fill=tk.X, pady=(0, 14))
        self.solve_btn.bind("<Enter>",
                            lambda e: self.solve_btn.config(bg=ACCENT_GREEN_H))
        self.solve_btn.bind("<Leave>", lambda e: (
            self.solve_btn.config(bg=ACCENT_GREEN)
            if self.solve_btn.cget("text") != "⏳  Solving..." else None))

        # ── Separator ──
        tk.Frame(wrapper, bg=BORDER, height=1).pack(fill=tk.X, pady=(0, 10))

        # ── Step info ──
        self.step_info = tk.StringVar(value="Step: — / —")
        tk.Label(wrapper, textvariable=self.step_info,
                 font=F_MONO, bg=BG_ROOT, fg=TEXT_MUTED).pack(anchor=tk.W)

        # ── Progress bar ──
        self.progress_cv = tk.Canvas(wrapper, width=BOARD_SIZE, height=4,
                                     bg=BG_INPUT, highlightthickness=0)
        self.progress_cv.pack(fill=tk.X, pady=(4, 8))
        self.progress_cv.create_rectangle(0, 0, 0, 4,
                                          fill=ACCENT_BLUE, outline="",
                                          tags="bar")

        # ── Step controls ──
        ctrl = tk.Frame(wrapper, bg=BG_ROOT)
        ctrl.pack(fill=tk.X)

        self._styled_btn(ctrl, "◀  Prev", self.prev_step,
                         BG_INPUT, TEXT_PRIMARY).pack(
            side=tk.LEFT, padx=(0, 4), fill=tk.X, expand=True)

        self._styled_btn(ctrl, "Next  ▶", self.next_step,
                         BG_INPUT, TEXT_PRIMARY).pack(
            side=tk.LEFT, padx=(0, 4), fill=tk.X, expand=True)

        self.auto_btn = self._styled_btn(ctrl, "▶▶  Auto", self.auto_play,
                                         BG_INPUT, ACCENT_BLUE)
        self.auto_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # ── Status ──
        self.status_var = tk.StringVar(value="Select an algorithm and press SOLVE")
        tk.Label(wrapper, textvariable=self.status_var,
                 font=F_SMALL, bg=BG_ROOT, fg=TEXT_MUTED,
                 wraplength=BOARD_SIZE, justify=tk.LEFT).pack(
            anchor=tk.W, pady=(10, 0))

    # ══════════════════════════════════════════════════════════════════════════
    #  RIGHT PANEL
    # ══════════════════════════════════════════════════════════════════════════

    def _build_right_panel(self, parent):
        # ── Header ──
        hdr = tk.Frame(parent, bg=BG_CARD, padx=16, pady=14)
        hdr.pack(fill=tk.X)

        tk.Label(hdr, text="📊  Dashboard", font=F_HEADER,
                 bg=BG_CARD, fg=TEXT_WHITE).pack(side=tk.LEFT)

        self._styled_btn(hdr, "Clear", self.clear_log,
                         BORDER, TEXT_MUTED, font=F_TINY).pack(side=tk.RIGHT)

        self.fs_btn = self._styled_btn(hdr, "⛶  Fullscreen", self.toggle_fullscreen,
                                       BORDER, TEXT_MUTED, font=F_TINY)
        self.fs_btn.pack(side=tk.RIGHT, padx=(0, 6))

        tk.Frame(parent, bg=BORDER, height=1).pack(fill=tk.X)

        # ── Stats cards ──
        sf = tk.Frame(parent, bg=BG_CARD, padx=12, pady=10)
        sf.pack(fill=tk.X)

        tk.Label(sf, text="STATISTICS", font=F_GROUP_HDR,
                 bg=BG_CARD, fg=TEXT_MUTED).pack(anchor=tk.W, pady=(0, 6))

        grid = tk.Frame(sf, bg=BG_CARD)
        grid.pack(fill=tk.X)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        self._stat_card(grid, "algo",  "🔬", "Algorithm", "—",
                        ACCENT_PURPLE, 0, 0, val_font=F_STAT_ALGO)
        self._stat_card(grid, "steps", "👣", "Steps",     "—",
                        ACCENT_BLUE,   0, 1)
        self._stat_card(grid, "nodes", "🌐", "Nodes",     "—",
                        ACCENT_CYAN,   1, 0)
        self._stat_card(grid, "time",  "⏱",  "Time",      "—",
                        ACCENT_GREEN,  1, 1)

        tk.Frame(parent, bg=BORDER, height=1).pack(fill=tk.X, padx=12, pady=(6, 0))

        # ── Solution Log ──
        lh = tk.Frame(parent, bg=BG_CARD, padx=16, pady=8)
        lh.pack(fill=tk.X)
        tk.Label(lh, text="SOLUTION LOG", font=F_GROUP_HDR,
                 bg=BG_CARD, fg=TEXT_MUTED).pack(anchor=tk.W)

        lf = tk.Frame(parent, bg=BG_CARD, padx=12)
        lf.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        sb = tk.Scrollbar(lf, bg=BG_CARD, troughcolor=BG_INPUT)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text = tk.Text(
            lf, width=30, font=F_MONO,
            bg=BG_INPUT, fg=TEXT_PRIMARY,
            yscrollcommand=sb.set, relief=tk.FLAT,
            state=tk.DISABLED, spacing1=3,
            padx=10, pady=8,
            insertbackground=TEXT_PRIMARY,
            selectbackground=ACCENT_BLUE,
            borderwidth=0)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.config(command=self.log_text.yview)

        # Tags
        self.log_text.tag_config("err",    foreground=ACCENT_PINK,
                                 font=F_MONO_BOLD)
        self.log_text.tag_config("ok",     foreground=ACCENT_GREEN,
                                 font=F_MONO_BOLD)
        self.log_text.tag_config("header", foreground=ACCENT_PURPLE,
                                 font=F_MONO_BOLD)
        self.log_text.tag_config("muted",  foreground=TEXT_MUTED)
        self.log_text.tag_config("step",   foreground=TEXT_PRIMARY)
        self.log_text.tag_config("cur",    background=ACCENT_BLUE,
                                 foreground="#1a1b26")

    # ── Stat card helper ──────────────────────────────────────────────────────

    def _stat_card(self, parent, sid, icon, label, value,
                   color, row, col, val_font=None):
        card = tk.Frame(parent, bg=BG_INPUT, padx=10, pady=8)
        card.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")

        top = tk.Frame(card, bg=BG_INPUT)
        top.pack(fill=tk.X)
        tk.Label(top, text=icon, font=F_BODY,
                 bg=BG_INPUT, fg=color).pack(side=tk.LEFT)
        tk.Label(top, text=f"  {label}", font=F_TINY,
                 bg=BG_INPUT, fg=TEXT_MUTED).pack(side=tk.LEFT)

        vl = tk.Label(card, text=value,
                      font=val_font or F_STAT_VAL,
                      bg=BG_INPUT, fg=color, anchor=tk.W)
        vl.pack(fill=tk.X, pady=(4, 0))
        self.stat_labels[sid] = vl

    def _update_stats(self, algo="—", steps="—", nodes="—", time_s="—"):
        self.stat_labels["algo"].config(text=algo)
        self.stat_labels["steps"].config(text=str(steps))
        self.stat_labels["nodes"].config(text=str(nodes))
        self.stat_labels["time"].config(text=time_s)

    # ══════════════════════════════════════════════════════════════════════════
    #  STYLED BUTTON HELPER
    # ══════════════════════════════════════════════════════════════════════════

    def _styled_btn(self, parent, text, cmd, bg, fg,
                    hover_bg=None, font=None):
        if font is None:
            font = F_BTN
        if hover_bg is None:
            hover_bg = BORDER_LIGHT

        btn = tk.Button(parent, text=text, command=cmd,
                        bg=bg, fg=fg, font=font,
                        relief=tk.FLAT, padx=10, pady=6,
                        cursor="hand2",
                        activebackground=hover_bg,
                        activeforeground=fg,
                        borderwidth=0)

        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        return btn

    # ══════════════════════════════════════════════════════════════════════════
    #  BOARD DRAWING
    # ══════════════════════════════════════════════════════════════════════════

    @staticmethod
    def _round_rect(cv, x1, y1, x2, y2, r=12, **kw):
        """Draw a rounded rectangle via smooth polygon."""
        pts = [
            x1+r, y1,   x2-r, y1,
            x2,   y1,   x2,   y1+r,
            x2,   y2-r, x2,   y2,
            x2-r, y2,   x1+r, y2,
            x1,   y2,   x1,   y2-r,
            x1,   y1+r, x1,   y1,
        ]
        return cv.create_polygon(pts, smooth=True, **kw)

    def _draw_board(self, state=None):
        if state is None:
            state = self.state
        self.canvas.delete("all")

        # Board background
        self._round_rect(self.canvas, 4, 4,
                         BOARD_SIZE - 4, BOARD_SIZE - 4,
                         r=18, fill=BG_CARD, outline=BORDER)

        for i, val in enumerate(state):
            r, c = i // 3, i % 3
            x1 = BOARD_PAD + c * (TILE_SIZE + TILE_GAP)
            y1 = BOARD_PAD + r * (TILE_SIZE + TILE_GAP)
            x2 = x1 + TILE_SIZE
            y2 = y1 + TILE_SIZE

            if val == 0:
                self._round_rect(self.canvas, x1, y1, x2, y2,
                                 r=TILE_RADIUS, fill=EMPTY_SLOT,
                                 outline=BORDER)
            else:
                # Shadow
                self._round_rect(self.canvas,
                                 x1 + SHADOW_OFF, y1 + SHADOW_OFF,
                                 x2 + SHADOW_OFF, y2 + SHADOW_OFF,
                                 r=TILE_RADIUS,
                                 fill=TILE_SHADOW, outline="")
                # Tile body
                self._round_rect(self.canvas, x1, y1, x2, y2,
                                 r=TILE_RADIUS,
                                 fill=TILE_BODY, outline="")
                # Top highlight strip
                self._round_rect(self.canvas,
                                 x1 + 3, y1 + 3,
                                 x2 - 3, y1 + 32,
                                 r=TILE_RADIUS - 2,
                                 fill=TILE_HIGHLIGHT, outline="")
                # Number
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                self.canvas.create_text(cx, cy, text=str(val),
                                        font=F_TILE, fill=TEXT_WHITE)

    # ══════════════════════════════════════════════════════════════════════════
    #  PROGRESS BAR
    # ══════════════════════════════════════════════════════════════════════════

    def _update_progress(self):
        if not self.solution or len(self.solution) <= 1:
            self.progress_cv.coords("bar", 0, 0, 0, 4)
            return
        self.progress_cv.update_idletasks()
        w = self.progress_cv.winfo_width() or BOARD_SIZE
        frac = self.current_step / (len(self.solution) - 1)
        self.progress_cv.coords("bar", 0, 0, int(w * frac), 4)

    # ══════════════════════════════════════════════════════════════════════════
    #  LOG HELPERS
    # ══════════════════════════════════════════════════════════════════════════

    def _log(self, text, tag="step"):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, text + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _log_step(self, idx, state, current=False):
        tag = f"step_item_{idx}"
        lines = [f"Step {idx}:"]
        for r in range(3):
            row = state[r*3:(r+1)*3]
            lines.append("  " + " ".join(
                str(v) if v != 0 else "·" for v in row))
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, "\n".join(lines) + "\n\n", tag)
        
        if current:
            self.log_text.tag_config(tag, background=ACCENT_BLUE, foreground="#1a1b26", font=F_MONO)
        else:
            self.log_text.tag_config(tag, background="", foreground=TEXT_PRIMARY, font=F_MONO)
        self.log_text.config(state=tk.DISABLED)

    def clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
        self._update_stats()

    # ══════════════════════════════════════════════════════════════════════════
    #  ALGO CHANGE → SHOW / HIDE PARAMS
    # ══════════════════════════════════════════════════════════════════════════

    def _on_algo_change(self):
        for w in self.param_frame.winfo_children():
            w.destroy()

        algo = self.algo_var.get()
        if algo == "DLS":
            tk.Label(self.param_frame, text="Depth Limit:", font=F_SMALL,
                     bg=BG_SIDEBAR, fg=TEXT_MUTED).pack(side=tk.LEFT)
            tk.Spinbox(self.param_frame, from_=1, to=50,
                       textvariable=self.dls_limit, width=5,
                       font=F_MONO, bg=BG_INPUT, fg=TEXT_PRIMARY,
                       buttonbackground=BG_INPUT,
                       relief=tk.FLAT).pack(side=tk.LEFT, padx=6)
        elif algo == "Local Beam":
            tk.Label(self.param_frame, text="Beam k:", font=F_SMALL,
                     bg=BG_SIDEBAR, fg=TEXT_MUTED).pack(side=tk.LEFT)
            tk.Spinbox(self.param_frame, from_=1, to=20,
                       textvariable=self.beam_k, width=5,
                       font=F_MONO, bg=BG_INPUT, fg=TEXT_PRIMARY,
                       buttonbackground=BG_INPUT,
                       relief=tk.FLAT).pack(side=tk.LEFT, padx=6)

    # ══════════════════════════════════════════════════════════════════════════
    #  SHUFFLE / RESET
    # ══════════════════════════════════════════════════════════════════════════

    def shuffle(self):
        self.running = False
        if hasattr(self, "auto_btn"):
            self.auto_btn.config(text="▶▶  Auto", fg=ACCENT_BLUE)
        while True:
            s = list(range(9))
            random.shuffle(s)
            if is_solvable(s):
                break
        self.state        = s
        self.solution     = []
        self.current_step = 0
        self._update_stats()
        self.step_info.set("Step: — / —")
        self.status_var.set("Shuffled — press SOLVE to find solution")
        self._draw_board()
        self._update_progress()

    def reset(self):
        self.running = False
        if hasattr(self, "auto_btn"):
            self.auto_btn.config(text="▶▶  Auto", fg=ACCENT_BLUE)
        self.state        = [1, 2, 3, 4, 5, 0, 7, 8, 6]
        self.solution     = []
        self.current_step = 0
        self._update_stats()
        self.step_info.set("Step: — / —")
        self.status_var.set("Reset")
        self._draw_board()
        self._update_progress()
        self.clear_log()

    # ══════════════════════════════════════════════════════════════════════════
    #  SOLVE
    # ══════════════════════════════════════════════════════════════════════════

    def solve(self):
        self.running = False
        if hasattr(self, "auto_btn"):
            self.auto_btn.config(text="▶▶  Auto", fg=ACCENT_BLUE)
        algo  = self.algo_var.get()
        start = self.state[:]
        goal  = GOAL_STATE

        if not is_solvable(start):
            messagebox.showerror("Error", "This puzzle is unsolvable!")
            return

        self.clear_log()
        self._log(f"Running {algo}…", "muted")
        self.status_var.set(f"Solving with {algo}…")
        self.solve_btn.config(state=tk.DISABLED, text="⏳  Solving…",
                               bg=TEXT_MUTED)

        def run():
            t0 = time.time()
            if   algo == "BFS":               result, nodes = bfs(start, goal)
            elif algo == "DFS":               result, nodes = dfs(start, goal)
            elif algo == "DLS":               result, nodes = dls(start, goal, limit=self.dls_limit.get())
            elif algo == "IDS":               result, nodes = ids(start, goal)
            elif algo == "UCS":               result, nodes = ucs(start, goal)
            elif algo == "Greedy":            result, nodes = greedy(start, goal)
            elif algo == "A*":                result, nodes = astar(start, goal)
            elif algo == "IDA*":              result, nodes = idastar(start, goal)
            elif algo == "Hill Climbing":     result, nodes = simple_hill_climbing(start, goal)
            elif algo == "Stochastic HC":     result, nodes = stochastic_hill_climbing(start, goal)
            elif algo == "Random Restart HC": result, nodes = random_restart_hill_climbing(start, goal)
            elif algo == "Local Beam":        result, nodes = local_beam_search(start, goal, k=self.beam_k.get())
            elif algo == "Simulated Annealing": result, nodes = simulated_annealing(start, goal)
            elif algo == "AND-OR Search":     result, nodes = and_or_search(start, goal)
            elif algo == "Sensorless Search": result, nodes = sensorless_search(start, goal)
            elif algo == "Backtracking CSP":  result, nodes = backtracking_search(start, goal)
            elif algo == "Forward Checking":  result, nodes = forward_checking_search(start, goal)
            elif algo == "AC-3":              result, nodes = ac3_search(start, goal)
            else:                             result, nodes = None, 0
            elapsed = time.time() - t0
            self.root.after(0, lambda: self._on_solve_done(
                result, nodes, elapsed, algo))

        threading.Thread(target=run, daemon=True).start()

    def _on_solve_done(self, result, nodes, elapsed, algo):
        self.solve_btn.config(state=tk.NORMAL, text="▶   SOLVE",
                               bg=ACCENT_GREEN)

        if result is None:
            self.status_var.set("No solution found")
            self._update_stats(algo, "✗", str(nodes), f"{elapsed:.3f}s")
            self._log("✗  No solution found", "err")
            self._log(f"   Nodes expanded: {nodes}", "muted")
            self._log(f"   Time: {elapsed:.4f}s", "muted")
            return

        self.solution     = result
        self.current_step = 0
        steps = len(result) - 1

        self.status_var.set(
            f"✓  {steps} steps  |  {nodes} nodes  |  {elapsed:.3f}s")
        self._update_stats(algo, str(steps), str(nodes), f"{elapsed:.3f}s")
        self.step_info.set(f"Step: 0 / {steps}")
        self._update_progress()

        self._log(f"✓  {algo}", "ok")
        self._log(f"   Steps     : {steps}", "muted")
        self._log(f"   Nodes     : {nodes}", "muted")
        self._log(f"   Time      : {elapsed:.4f}s", "muted")
        self._log("─" * 30, "muted")
        for i, s in enumerate(self.solution):
            self._log_step(i, s, current=(i == 0))

        self._draw_board(self.solution[0])

    # ══════════════════════════════════════════════════════════════════════════
    #  STEP CONTROLS
    # ══════════════════════════════════════════════════════════════════════════

    def _highlight_current_step(self):
        self.step_info.set(
            f"Step: {self.current_step} / {len(self.solution) - 1}")
        self._draw_board(self.solution[self.current_step])
        self._update_progress()

        # Update log tags and auto-scroll
        if hasattr(self, "solution") and self.solution:
            for idx in range(len(self.solution)):
                tag = f"step_item_{idx}"
                if idx == self.current_step:
                    self.log_text.tag_config(tag, background=ACCENT_BLUE, foreground="#1a1b26")
                    self.log_text.config(state=tk.NORMAL)
                    ranges = self.log_text.tag_ranges(tag)
                    if ranges:
                        self.log_text.see(ranges[0])
                    self.log_text.config(state=tk.DISABLED)
                else:
                    self.log_text.tag_config(tag, background="", foreground=TEXT_PRIMARY)

    def next_step(self):
        self.running = False
        if hasattr(self, "auto_btn"):
            self.auto_btn.config(text="▶▶  Auto", fg=ACCENT_BLUE)
        if not self.solution or self.current_step >= len(self.solution) - 1:
            return
        self.current_step += 1
        self._highlight_current_step()

    def prev_step(self):
        self.running = False
        if hasattr(self, "auto_btn"):
            self.auto_btn.config(text="▶▶  Auto", fg=ACCENT_BLUE)
        if not self.solution or self.current_step <= 0:
            return
        self.current_step -= 1
        self._highlight_current_step()

    def auto_play(self):
        if not self.solution:
            return

        if self.running:
            self.running = False
            self.auto_btn.config(text="▶▶  Auto", fg=ACCENT_BLUE)
            return

        self.running = True
        self.auto_btn.config(text="⏸  Pause", fg=ACCENT_PINK)

        def play():
            while (self.current_step < len(self.solution) - 1
                   and self.running):
                self.current_step += 1
                self.root.after(0, self._highlight_current_step)
                time.sleep(self.speed_var.get())
            self.running = False
            self.root.after(0, lambda: self.auto_btn.config(text="▶▶  Auto", fg=ACCENT_BLUE))

        threading.Thread(target=play, daemon=True).start()


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    app  = PuzzleApp(root)
    root.mainloop()
