# eight_queens/ui.py
"""
Revised UI for the Eight Queens game (modern, interactive board).

Features:
- Modern look using customtkinter (falls back to tkinter/ttk if not available)
- Interactive 8x8 board:  click a cell to place/remove a queen for that row
  (each row can only have 0 or 1 queen; clicking a different column in same row moves the queen)
- Buttons:  Submit, Clear Board, Precompute, Run Sequential, Run Threaded, Hint, Reset Recognized
- Integrates with existing modules:  eight_queens.solver, eight_queens.db_manager, eight_queens.models
  and common.timer, common.validators.
- Uses models. board_to_str / str_to_board / board_is_valid_format when available.
- Does not modify other project files.

Drop this file into eight_queens/ui.py (replacing the previous file).
"""

from typing import List, Optional, Tuple
import random
import traceback

# --- UI toolkit selection ---
try:
    import customtkinter as ctk

    USE_CTK = True
    # convenience map
    FrameType = ctk.CTkFrame
    LabelType = ctk.CTkLabel
    EntryType = ctk.CTkEntry
    ButtonType = ctk.CTkButton
    try:
        TextType = ctk.CTkTextbox
    except Exception:
        import tkinter as tk

        TextType = tk.Text
    RootType = ctk.CTk
except Exception:
    import tkinter as tk
    from tkinter import ttk, messagebox

    USE_CTK = False
    FrameType = tk.Frame
    LabelType = ttk.Label
    EntryType = ttk.Entry
    ButtonType = ttk.Button
    TextType = tk.Text
    RootType = tk.Tk

# --- project helpers ---
from common.timer import measure_execution_time
from common.validator import validate_non_empty_string

# local modules (may be missing during early dev; UI handles gracefully)
try:
    from eight_queens import solver
except Exception:
    solver = None

try:
    from eight_queens import db_manager
except Exception:
    db_manager = None

try:
    from eight_queens import models
except Exception:
    models = None

# --- constants ---
BOARD_SIZE = 8
CELL_SIZE = 64  # px
CANVAS_PADDING = 4
QUEEN_SYMBOL = "♛"  # unicode chess queen (fallback to 'Q' if font lacks glyph)

# --- Color scheme (matching main.py) ---
BG_DARK = "#0a0e27"
CARD_BG = "#151932"
ACCENT = "#6366f1"
ACCENT_HOVER = "#4f46e5"
TEXT_PRIMARY = "#f8fafc"
TEXT_SECONDARY = "#94a3b8"
GAME_COLOR = "#ec4899"  # Pink accent for Eight Queens (from main.py)
BORDER_COLOR = "#1e293b"

# Board colors (darker theme)
CELL_LIGHT = "#2d3154"
CELL_DARK = "#1e2140"


# --- helpers for model conversions (fall back to local logic) ---
def board_to_str(board: List[int]) -> str:
    if models and hasattr(models, "board_to_str"):
        return models.board_to_str(board)
    return ",".join(str(x) for x in board)


def str_to_board(s: str) -> List[int]:
    if models and hasattr(models, "str_to_board"):
        return models.str_to_board(s)
    # basic fallback parse
    parts = [p.strip() for p in s.replace(",", " ").split() if p.strip() != ""]
    return [int(p) for p in parts]


def board_is_valid_format(board: List[int]) -> bool:
    if models and hasattr(models, "board_is_valid_format"):
        try:
            return models.board_is_valid_format(board)
        except Exception:
            return False
    # fallback validation:  length, range, unique columns, diagonals
    if not isinstance(board, list) or len(board) != BOARD_SIZE:
        return False
    if any((not isinstance(x, int) or x < 0 or x >= BOARD_SIZE) for x in board):
        return False
    if len(set(board)) != BOARD_SIZE:
        return False
    for r1 in range(BOARD_SIZE):
        for r2 in range(r1 + 1, BOARD_SIZE):
            if abs(board[r1] - board[r2]) == abs(r1 - r2):
                return False
    return True


# --- small UI fallbacks for messageboxes ---
def show_info(msg: str):
    if USE_CTK:
        try:
            import tkinter.messagebox as mb
            mb.showinfo("Info", msg)
        except Exception:
            print("INFO:", msg)
    else:
        from tkinter import messagebox
        messagebox.showinfo("Info", msg)


def show_error(msg: str):
    if USE_CTK:
        try:
            import tkinter.messagebox as mb
            mb.showerror("Error", msg)
        except Exception:
            print("ERROR:", msg)
    else:
        from tkinter import messagebox
        messagebox.showerror("Error", msg)


# --- UI class ---
class EightQueensUI:
    def __init__(self, root: RootType):
        self.root = root
        self.root.title("Eight Queens — Play & Compare")

        # Fullscreen setup (matching main.py)
        if USE_CTK:
            try:
                ctk.set_appearance_mode("dark")
                ctk.set_default_color_theme("blue")
            except Exception:
                pass

        # Fullscreen
        self.root.state('zoomed')  # Windows
        try:
            self.root.attributes('-fullscreen', True)  # Linux/Mac fallback
        except Exception:
            pass

        # Allow exit with Escape
        self.root.bind("<Escape>", lambda e: self._go_back())

        # Configure root background
        if USE_CTK:
            self.root.configure(fg_color=BG_DARK)
        else:
            self.root.configure(bg=BG_DARK)

        # initialize DB if available
        try:
            if db_manager and hasattr(db_manager, "initialize"):
                db_manager.initialize("App.db")
        except Exception:
            # non-fatal
            pass

        # app state:  board is list of ints (col for each row) or -1 if empty
        self.board: List[int] = [-1] * BOARD_SIZE

        # UI layout:  left = game board, right = controls/log
        self._build_ui()

        # refresh recognized list on start
        self.refresh_recognized_list()

    def _go_back(self):
        """Close the game window"""
        self.root.destroy()

    def _create_styled_button(self, parent, text, command, color=None, width=200):
        """Create a styled button matching main.py aesthetic"""
        btn_color = color if color else ACCENT
        hover_color = ACCENT_HOVER if color == ACCENT or color is None else self._darken_color(color)

        if USE_CTK:
            btn = ctk.CTkButton(
                parent,
                text=text,
                command=command,
                font=("SF Pro Text", 14, "bold"),
                fg_color=btn_color,
                hover_color=hover_color,
                text_color=TEXT_PRIMARY,
                corner_radius=12,
                width=width,
                height=40
            )
        else:
            btn = ButtonType(parent, text=text, command=command)
        return btn

    def _darken_color(self, hex_color):
        """Darken a hex color by 20%"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        r = int(r * 0.8)
        g = int(g * 0.8)
        b = int(b * 0.8)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _build_ui(self):
        if USE_CTK:
            # Main container centered
            main_container = ctk.CTkFrame(self.root, fg_color="transparent")
            main_container.place(relx=0.5, rely=0.5, anchor="center")

            # Header section
            header = ctk.CTkFrame(main_container, fg_color="transparent")
            header.pack(pady=(0,40))

            # Back button (top left of header)
            back_btn = ctk.CTkButton(
                header,
                text="← Back",
                font=("SF Pro Text", 14, "bold"),
                fg_color="transparent",
                hover_color=CARD_BG,
                text_color=TEXT_SECONDARY,
                border_width=2,
                border_color=BORDER_COLOR,
                corner_radius=12,
                width=100,
                height=35,
                command=self._go_back
            )
            # allign back button top left
            back_btn.pack(anchor= "center" , pady=(0, 20))

            title = ctk.CTkLabel(
                header,
                text="♕ Eight Queens",
                font=("SF Pro Display", 48, "bold"),
                text_color=TEXT_PRIMARY
            )
            title.pack()

            subtitle = ctk.CTkLabel(
                header,
                text="Place 8 queens on the board so none can attack each other",
                font=("SF Pro Text", 16),
                text_color=TEXT_SECONDARY
            )
            subtitle.pack(pady=(8, 0))

            # Content container - horizontal layout
            content_container = ctk.CTkFrame(main_container, fg_color="transparent")
            content_container.pack()

            # Board card (left side)
            board_card = ctk.CTkFrame(
                content_container,
                fg_color=CARD_BG,
                corner_radius=20,
                border_width=2,
                border_color=BORDER_COLOR
            )
            board_card.pack(side="left", padx=(0,30), pady=10)

            # Board canvas
            canvas_w = BOARD_SIZE * CELL_SIZE + CANVAS_PADDING * 2
            canvas_h = BOARD_SIZE * CELL_SIZE + CANVAS_PADDING * 2

            import tkinter as tk
            self.canvas = tk.Canvas(
                board_card,
                width=canvas_w,
                height=canvas_h,
                highlightthickness=0,
                bg=CARD_BG
            )
            self.canvas.pack(padx=20, pady=20)

            # Controls card (right side)
            controls_card = ctk.CTkFrame(
                content_container,
                fg_color=CARD_BG,
                corner_radius=20,
                border_width=2,
                border_color=BORDER_COLOR
            )
            controls_card.pack(side="left", pady=10)

            controls_inner = ctk.CTkFrame(controls_card, fg_color="transparent")
            controls_inner.pack(padx=30, pady=30)

            # Player name section
            name_label = ctk.CTkLabel(
                controls_inner,
                text="Player Name",
                font=("SF Pro Text", 14, "bold"),
                text_color=TEXT_PRIMARY
            )
            name_label.pack(anchor="w", pady=(0, 8))

            self.name_var = tk.StringVar()
            self.name_entry = ctk.CTkEntry(
                controls_inner,
                textvariable=self.name_var,
                width=220,
                height=40,
                font=("SF Pro Text", 14),
                fg_color=BG_DARK,
                border_color=BORDER_COLOR,
                text_color=TEXT_PRIMARY,
                corner_radius=10
            )
            self.name_entry.pack(pady=(0, 20))

            # Game buttons
            self.submit_btn = self._create_styled_button(
                controls_inner, "✓ Submit Solution", self.on_submit, GAME_COLOR, 220
            )
            self.submit_btn.pack(pady=6)

            self.clear_btn = self._create_styled_button(
                controls_inner, "⟲ Clear Board", self.clear_board, "#374151", 220
            )
            self.clear_btn.pack(pady=6)

            self.hint_btn = self._create_styled_button(
                controls_inner, "💡 Hint", self.show_hint, "#f59e0b", 220
            )
            self.hint_btn.pack(pady=6)

            # Separator
            sep = ctk.CTkFrame(controls_inner, height=2, fg_color=BORDER_COLOR)
            sep.pack(fill="x", pady=15)

            # Solver section label
            solver_label = ctk.CTkLabel(
                controls_inner,
                text="Solver Tools",
                font=("SF Pro Text", 14, "bold"),
                text_color=TEXT_PRIMARY
            )
            solver_label.pack(anchor="w", pady=(0, 10))

            self.precompute_btn = self._create_styled_button(
                controls_inner, "⚡ Precompute & Store", self.on_precompute, "#10b981", 220
            )
            self.precompute_btn.pack(pady=6)

            self.seq_btn = self._create_styled_button(
                controls_inner, "▶ Run Sequential", self.on_run_sequential, "#3b82f6", 220
            )
            self.seq_btn.pack(pady=6)

            self.thread_btn = self._create_styled_button(
                controls_inner, "⧉ Run Threaded", self.on_run_threaded, "#8b5cf6", 220
            )
            self.thread_btn.pack(pady=6)

            self.reset_btn = self._create_styled_button(
                controls_inner, "↺ Reset Recognized", self.on_reset_flags, "#ef4444", 220
            )
            self.reset_btn.pack(pady=6)

            # Bottom section - Recognized solutions and Log
            bottom_container = ctk.CTkFrame(main_container, fg_color="transparent")
            bottom_container.pack(pady=(30, 0))

            # Recognized solutions card
            recognized_card = ctk.CTkFrame(
                bottom_container,
                fg_color=CARD_BG,
                corner_radius=20,
                border_width=2,
                border_color=BORDER_COLOR
            )
            recognized_card.pack(side="left", padx=(0, 15))

            recognized_inner = ctk.CTkFrame(recognized_card, fg_color="transparent")
            recognized_inner.pack(padx=20, pady=20)

            recognized_label = ctk.CTkLabel(
                recognized_inner,
                text="🏆 Recognized Solutions",
                font=("SF Pro Text", 14, "bold"),
                text_color=TEXT_PRIMARY
            )
            recognized_label.pack(anchor="w", pady=(0, 10))

            self.recognized_box = ctk.CTkTextbox(
                recognized_inner,
                width=300,
                height=120,
                font=("SF Pro Text", 12),
                fg_color=BG_DARK,
                text_color=TEXT_SECONDARY,
                corner_radius=10
            )
            self.recognized_box.pack()
            self.recognized_box.configure(state="disabled")

            # Log card
            log_card = ctk.CTkFrame(
                bottom_container,
                fg_color=CARD_BG,
                corner_radius=20,
                border_width=2,
                border_color=BORDER_COLOR
            )
            log_card.pack(side="left", padx=(15, 0))

            log_inner = ctk.CTkFrame(log_card, fg_color="transparent")
            log_inner.pack(padx=20, pady=20)

            log_label = ctk.CTkLabel(
                log_inner,
                text="📋 Activity Log",
                font=("SF Pro Text", 14, "bold"),
                text_color=TEXT_PRIMARY
            )
            log_label.pack(anchor="w", pady=(0, 10))

            self.log_box = ctk.CTkTextbox(
                log_inner,
                width=300,
                height=120,
                font=("SF Pro Text", 12),
                fg_color=BG_DARK,
                text_color=TEXT_SECONDARY,
                corner_radius=10
            )
            self.log_box.pack()
            self.log_box.configure(state="disabled")

        else:
            # Fallback for non-CTK (basic styling)
            import tkinter as tk
            root_container = FrameType(self.root, padx=12, pady=12, bg=BG_DARK)
            root_container.pack(fill="both", expand=True)

            board_frame = FrameType(root_container, bg=BG_DARK)
            board_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
            control_frame = FrameType(root_container, bg=BG_DARK)
            control_frame.grid(row=0, column=1, sticky="nsew")

            canvas_w = BOARD_SIZE * CELL_SIZE + CANVAS_PADDING * 2
            canvas_h = BOARD_SIZE * CELL_SIZE + CANVAS_PADDING * 2
            self.canvas = tk.Canvas(board_frame, width=canvas_w, height=canvas_h, highlightthickness=0, bg=CARD_BG)
            self.canvas.pack(expand=True, fill="both")

            # Controls
            title = LabelType(control_frame, text="Controls", font=("Helvetica", 16, "bold"))
            title.grid(row=0, column=0, pady=(0, 8), sticky="w")

            LabelType(control_frame, text="Player name: ").grid(row=1, column=0, sticky="w")
            self.name_var = tk.StringVar()
            self.name_entry = EntryType(control_frame, textvariable=self.name_var, width=22)
            self.name_entry.grid(row=2, column=0, sticky="ew", pady=(0, 8))

            self.submit_btn = ButtonType(control_frame, text="Submit Solution", command=self.on_submit)
            self.submit_btn.grid(row=3, column=0, pady=(6, 6), sticky="ew")

            self.clear_btn = ButtonType(control_frame, text="Clear Board", command=self.clear_board)
            self.clear_btn.grid(row=4, column=0, pady=(6, 6), sticky="ew")

            self.hint_btn = ButtonType(control_frame, text="Hint", command=self.show_hint)
            self.hint_btn.grid(row=5, column=0, pady=(6, 6), sticky="ew")

            self.precompute_btn = ButtonType(control_frame, text="Precompute & Store", command=self.on_precompute)
            self.precompute_btn.grid(row=7, column=0, pady=(6, 6), sticky="ew")

            self.seq_btn = ButtonType(control_frame, text="Run Sequential", command=self.on_run_sequential)
            self.seq_btn.grid(row=8, column=0, pady=(6, 6), sticky="ew")

            self.thread_btn = ButtonType(control_frame, text="Run Threaded", command=self.on_run_threaded)
            self.thread_btn.grid(row=9, column=0, pady=(6, 6), sticky="ew")

            self.reset_btn = ButtonType(control_frame, text="Reset Recognized", command=self.on_reset_flags)
            self.reset_btn.grid(row=10, column=0, pady=(6, 6), sticky="ew")

            LabelType(control_frame, text="Recognized solutions:").grid(row=11, column=0, sticky="w", pady=(10, 0))
            self.recognized_box = TextType(control_frame, width=28, height=10)
            self.recognized_box.grid(row=12, column=0, pady=(4, 8))
            self.recognized_box.configure(state="disabled")

            LabelType(control_frame, text="Log:").grid(row=13, column=0, sticky="w", pady=(8, 0))
            self.log_box = TextType(control_frame, width=28, height=6)
            self.log_box.grid(row=14, column=0, pady=(4, 0))
            self.log_box.configure(state="disabled")

        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self._cell_rect_ids = [[None] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self._cell_queen_ids = [[None] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self._draw_board()

    # --- Board drawing & interaction ---
    def _draw_board(self):
        self.canvas.delete("all")
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x1 = CANVAS_PADDING + c * CELL_SIZE
                y1 = CANVAS_PADDING + r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                # alternating colors (dark theme)
                fill = CELL_LIGHT if (r + c) % 2 == 0 else CELL_DARK
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=BORDER_COLOR)
                self._cell_rect_ids[r][c] = rect
                # draw queen if present
                if self.board[r] == c:
                    q = self.canvas.create_text(
                        x1 + CELL_SIZE / 2,
                        y1 + CELL_SIZE / 2,
                        text=QUEEN_SYMBOL,
                        font=("Helvetica", int(CELL_SIZE / 1.8)),
                        fill=GAME_COLOR
                    )
                    self._cell_queen_ids[r][c] = q
                else:
                    self._cell_queen_ids[r][c] = None

    def _on_canvas_click(self, event):
        # translate x,y to row,col
        x = event.x - CANVAS_PADDING
        y = event.y - CANVAS_PADDING
        if x < 0 or y < 0:
            return
        col = int(x // CELL_SIZE)
        row = int(y // CELL_SIZE)
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            return
        # toggle/move queen for that row:
        old_col = self.board[row]
        if old_col == col:
            # remove queen
            self.board[row] = -1
            self._update_cell(row, col, remove=True)
            self._log(f"Removed queen at row {row}, col {col}")
        else:
            # place/move queen in that row to clicked column
            # remove old queen in that row if any
            if old_col != -1:
                self._update_cell(row, old_col, remove=True)
            self.board[row] = col
            self._update_cell(row, col, remove=False)
            self._log(f"Placed queen at row {row}, col {col}")

    def _update_cell(self, row: int, col: int, remove: bool):
        # redraw a single cell to add/remove queen
        # clear old queen id for that row (if any)
        # remove any queen graphic in this row
        for c in range(BOARD_SIZE):
            qid = self._cell_queen_ids[row][c]
            if qid:
                try:
                    self.canvas.delete(qid)
                except Exception:
                    pass
                self._cell_queen_ids[row][c] = None

        if not remove:
            x1 = CANVAS_PADDING + col * CELL_SIZE
            y1 = CANVAS_PADDING + row * CELL_SIZE
            # create text for queen
            q = self.canvas.create_text(
                x1 + CELL_SIZE / 2,
                y1 + CELL_SIZE / 2,
                text=QUEEN_SYMBOL,
                font=("Helvetica", int(CELL_SIZE / 1.8)),
                fill=GAME_COLOR
            )
            self._cell_queen_ids[row][col] = q

    def clear_board(self):
        self.board = [-1] * BOARD_SIZE
        self._draw_board()
        self._log("Board cleared.")

    # --- hint:  fill the board with one valid solution (random) ---
    def show_hint(self):
        try:
            if solver and hasattr(solver, "find_all_solutions_sequential"):
                sols = solver.find_all_solutions_sequential()
                if not sols:
                    raise RuntimeError("No solutions available from solver.")
                s = random.choice(sols)
                self.board = s.copy()
                self._draw_board()
                self._log("Hint: board filled with a valid solution.")
            else:
                show_error("Solver not available to provide a hint.")
        except Exception as e:
            tb = traceback.format_exc()
            self._log(f"Hint failed: {e}\n{tb}", error=True)
            show_error(f"Hint failed: {e}")

    # --- submission & DB integration ---
    def on_submit(self):
        # validate name
        name = self.name_var.get()
        try:
            name = validate_non_empty_string(name)
        except Exception as e:
            show_error(f"Invalid name: {e}")
            return

        # ensure board complete
        if any(v == -1 for v in self.board):
            show_error("Please place a queen in every row (8 queens) before submitting.")
            return

        # validate board correctness via models or fallback
        try:
            if not board_is_valid_format(self.board):
                show_error("Board is not a valid non-attacking configuration.")
                return
        except Exception as e:
            show_error(f"Validation error: {e}")
            return

        sol_str = board_to_str(self.board)

        try:
            # check existence
            exists = False
            if db_manager and hasattr(db_manager, "solution_exists"):
                exists = db_manager.solution_exists(sol_str)
            else:
                # fallback to solver membership
                if solver and hasattr(solver, "find_all_solutions_sequential"):
                    all_sols = solver.find_all_solutions_sequential()
                    exists = any(board_to_str(s) == sol_str for s in all_sols)
                else:
                    raise RuntimeError("No way to verify solution (db_manager or solver missing).")

            if not exists:
                show_error("This configuration is not one of the valid solutions.")
                return

            # attempt to mark recognized
            marked = True
            if db_manager and hasattr(db_manager, "mark_solution_recognized"):
                marked = db_manager.mark_solution_recognized(sol_str)
                if not marked:
                    show_info("This solution has already been recognized by another player.  Try a different one.")
                    self._log(f"Submission '{sol_str}' already recognized.")
                    return

            # save player submission record
            try:
                if db_manager and hasattr(db_manager, "save_player_submission"):
                    db_manager.save_player_submission(name, sol_str)
            except Exception:
                # ignore save error but inform user
                self._log("Warning: failed to persist player submission to DB.")

            show_info("Correct! Your solution was recorded.")
            self._log(f"Player '{name}' recorded solution: {sol_str}")
            self.refresh_recognized_list()

            # ✅ Only reset when ALL 92 solutions have been recognized
            try:
                if db_manager and hasattr(db_manager, "get_recognized_count"):
                    count = db_manager.get_recognized_count()
                    if count >= 92:
                        db_manager.reset_all_recognized_flags()
                        show_info("All 92 solutions found! Flags reset for new players.")
                        self._log("All solutions recognized.  Flags reset.")
            except Exception:
                pass

        except Exception as e:
            tb = traceback.format_exc()
            self._log(f"Submit failed: {e}\n{tb}", error=True)
            show_error(f"Submit failed:  {e}")

    # --- solver & timing integration ---
    def on_precompute(self):
        try:
            if solver and hasattr(solver, "run_sequential_timed"):
                sols, t = solver.run_sequential_timed()
            elif solver and hasattr(solver, "find_all_solutions_sequential"):
                import time
                start = time.perf_counter()
                sols = solver.find_all_solutions_sequential()
                t = time.perf_counter() - start

            #to Store Solution using threading
            #if solver and hasattr(solver, "run_threaded_timed"):
            #    sols, t = solver.run_threaded_timed()  # ← THREADED
            #elif solver and hasattr(solver, "run_sequential_timed"):
            #    sols, t = solver.run_sequential_timed()  # ← Fallback
            #else:
            #    raise RuntimeError("Solver not available.")

            # insert to DB if available
            inserted = 0
            for s in sols:
                s_str = board_to_str(s)
                try:
                    if db_manager and hasattr(db_manager, "insert_solution"):
                        db_manager.insert_solution(s_str)
                    else:
                        # fallback:  skip persistence
                        pass
                    inserted += 1
                except Exception:
                    # ignore duplicate or insert errors
                    pass

            self._log(f"Precomputed {len(sols)} solutions. (Inserted {inserted} into DB)")
            show_info(f"Precomputed {len(sols)} solutions in {t:.6f}s.")
            # save timing
            try:
                if db_manager and hasattr(db_manager, "save_timing"):
                    db_manager.save_timing("sequential_precompute", 1, t)
            except Exception:
                pass
            self.refresh_recognized_list()
        except Exception as e:
            tb = traceback.format_exc()
            self._log(f"Precompute failed: {e}\n{tb}", error=True)
            show_error(f"Precompute failed:  {e}")

    def on_run_sequential(self):
        try:
            if solver and hasattr(solver, "run_sequential_timed"):
                sols, t = solver.run_sequential_timed()
            elif solver and hasattr(solver, "find_all_solutions_sequential"):
                import time
                start = time.perf_counter()
                sols = solver.find_all_solutions_sequential()
                t = time.perf_counter() - start
            else:
                raise RuntimeError("Solver not available.")

            self._log(f"Sequential:  {len(sols)} solutions in {t:.6f}s")
            show_info(f"Sequential: {len(sols)} solutions in {t:.6f}s")
            try:
                if db_manager and hasattr(db_manager, "save_timing"):
                    db_manager.save_timing("sequential", 1, t)
            except Exception:
                pass
        except Exception as e:
            tb = traceback.format_exc()
            self._log(f"Run sequential failed: {e}\n{tb}", error=True)
            show_error(f"Run sequential failed: {e}")

    def on_run_threaded(self):
        try:
            if solver and hasattr(solver, "run_threaded_timed"):
                sols, t = solver.run_threaded_timed()
            else:
                raise RuntimeError("Threaded solver not available.")
            self._log(f"Threaded: {len(sols)} solutions in {t:.6f}s")
            show_info(f"Threaded: {len(sols)} solutions in {t:.6f}s")
            try:
                if db_manager and hasattr(db_manager, "save_timing"):
                    db_manager.save_timing("threaded", 1, t)
            except Exception:
                pass
        except Exception as e:
            tb = traceback.format_exc()
            self._log(f"Run threaded failed: {e}\n{tb}", error=True)
            show_error(f"Run threaded failed: {e}")

    def on_reset_flags(self):
        try:
            if db_manager and hasattr(db_manager, "reset_all_recognized_flags"):
                db_manager.reset_all_recognized_flags()
                show_info("All recognized flags reset.")
                self._log("Recognized flags reset.")
                self.refresh_recognized_list()
            else:
                show_error("reset_all_recognized_flags not implemented in db_manager.")
        except Exception as e:
            tb = traceback.format_exc()
            self._log(f"Reset flags failed: {e}\n{tb}", error=True)
            show_error(f"Reset flags failed:  {e}")

    # --- recognized list and logging ---
    def refresh_recognized_list(self):
        try:
            content = ""
            if db_manager and hasattr(db_manager, "get_recognized_solutions"):
                rows = db_manager.get_recognized_solutions()
                for (sol, name, ts) in rows:
                    content += f"{sol} — {name} ({ts})\n"
            else:
                # fallback: no DB
                content = "(No DB available)"
            try:
                self.recognized_box.configure(state="normal")
                self.recognized_box.delete("1.0", "end")
                self.recognized_box.insert("end", content)
                self.recognized_box.configure(state="disabled")
            except Exception:
                pass
        except Exception as e:
            self._log(f"Refresh recognized failed: {e}", error=True)

    def _log(self, msg: str, error: bool = False):
        try:
            self.log_box.configure(state="normal")
            self.log_box.insert("end", msg + "\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        except Exception:
            print(("ERROR: " if error else "INFO: ") + msg)


# --- launcher helper ---
def launch_game():
    if USE_CTK:
        app = RootType()
        ui = EightQueensUI(app)
        app.mainloop()
    else:
        root = RootType()
        ui = EightQueensUI(root)
        root.mainloop()


if __name__ == "__main__":
    launch_game()