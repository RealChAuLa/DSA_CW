"""
Snake and Ladder Game UI Module
Handles all user interface components and game flow
"""
import random
import tkinter as tk

import customtkinter as ctk

from snake_and_ladder import SnakeLadderSolver
from snake_and_ladder.data import (
    get_next_round_id,
    init_database,
    save_algorithm_timings,
    save_player_win,
)


# ============================================================================
# CONSTANTS
# ============================================================================
COLORS = {
    "bg_dark": "#0a0e27",
    "bg_panel": "#151932",
    "bg_board": "#0f172a",
    "cell_dark": "#1e293b",
    "cell_light": "#0f172a",
    "text_white": "white",
    "text_gray": "#cbd5e1",
    "success": "#10b981",
    "error": "#dc2626",
    "primary": "#4f46e5",
    "primary_hover": "#4338ca",
    "bfs": "#3b82f6",
    "dijkstra": "#f59e0b",
}

FONTS = {
    "title": ("SF Pro Display", 32, "bold"),
    "heading": ("SF Pro Display", 24, "bold"),
    "subheading": ("SF Pro Text", 18, "bold"),
    "body": ("SF Pro Text", 16),
    "cell": ("Consolas", 12, "bold"),
}


# ============================================================================
# UI COMPONENTS
# ============================================================================
class BoardContainer(ctk.CTkFrame):
    """Container frame for the game board with fixed dimensions."""

    def __init__(self, parent, width=750, height=600):
        super().__init__(parent, fg_color=COLORS["bg_board"])
        self.pack_propagate(False)
        self.configure(width=width, height=height)


# ============================================================================
# MAIN GAME UI
# ============================================================================
class SnakeLadderUI(ctk.CTk):
    """Main UI window for the Snake and Ladder game."""

    def __init__(self):
        super().__init__()
        self._setup_window()
        self._init_game_state()
        self._build_ui()
        # Get player name after UI is displayed
        self.after(100, self._get_player_name)

    # ------------------------------------------------------------------------
    # INITIALIZATION
    # ------------------------------------------------------------------------
    def _setup_window(self):
        """Configure the main window properties."""
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))
        self.title("Snake & Ladder Game")
        self.configure(fg_color=COLORS["bg_dark"])

    def _init_game_state(self):
        """Initialize game state variables."""
        self.board_size = None
        self.snakes = {}
        self.ladders = {}
        self.solver = None
        self.bfs_time = None
        self.dijkstra_time = None
        self.correct_answer = None
        self.current_round_id = None
        self.player_name = None

        # Initialize database
        init_database()

    # ------------------------------------------------------------------------
    # UI BUILDING
    # ------------------------------------------------------------------------
    def _build_ui(self):
        """Build the main user interface."""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Left panel - Game board and controls
        left_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True)

        self._build_left_panel(left_frame)

        # Right panel - Game status and options
        self.right_panel = ctk.CTkFrame(main_frame, width=300, fg_color=COLORS["bg_panel"])
        self.right_panel.pack(side="right", fill="y", padx=10)

        self._build_right_panel()

    def _build_left_panel(self, parent):
        """Build the left panel with title, controls, and board."""
        # Title
        title = ctk.CTkLabel(
            parent,
            text="Snake & Ladder Game",
            font=FONTS["title"],
            text_color=COLORS["text_white"],
        )
        title.pack(pady=10)

        # Board size selector
        self._build_size_selector(parent)

        # Generate board button
        ctk.CTkButton(
            parent,
            text="Generate Board",
            command=self.generate_board,
            width=200,
            height=45,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
        ).pack(pady=15)

        # Board container
        self.board_container = BoardContainer(parent)
        self.board_container.pack(pady=10, expand=True)

        self.canvas = tk.Canvas(
            self.board_container,
            bg=COLORS["bg_board"],
            highlightthickness=0,
        )
        self.canvas.pack(expand=True)

        # Algorithm buttons
        self._build_algorithm_buttons(parent)

        # Result label
        self.result_lbl = ctk.CTkLabel(
            parent,
            text="",
            font=FONTS["subheading"],
            text_color=COLORS["text_white"],
        )
        self.result_lbl.pack(pady=10)

        # Exit button
        ctk.CTkButton(
            parent,
            text="Exit Game",
            command=self.destroy,
            fg_color=COLORS["error"],
            width=150,
        ).pack(pady=10)

    def _build_size_selector(self, parent):
        """Build the board size selection widget."""
        size_frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_panel"])
        size_frame.pack(pady=10)

        ctk.CTkLabel(
            size_frame,
            text="Board Size (6–12):",
            font=FONTS["body"],
            text_color=COLORS["text_white"],
        ).pack(side="left", padx=10)

        self.size_var = ctk.StringVar(value="6")
        ctk.CTkOptionMenu(
            size_frame,
            values=[str(i) for i in range(6, 13)],
            variable=self.size_var,
            width=140,
            height=40,
        ).pack(side="left", padx=10)

    def _build_algorithm_buttons(self, parent):
        """Build the algorithm execution buttons."""
        algo_frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_panel"])
        algo_frame.pack(pady=10)

        ctk.CTkButton(
            algo_frame,
            text="Run BFS",
            command=self.run_bfs,
            width=160,
            fg_color=COLORS["bfs"],
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            algo_frame,
            text="Run Dijkstra",
            command=self.run_dijkstra,
            width=160,
            fg_color=COLORS["dijkstra"],
        ).pack(side="left", padx=10)

    def _build_right_panel(self):
        """Build the right panel for game status."""
        ctk.CTkLabel(
            self.right_panel,
            text="Generate a board to start!",
            font=FONTS["body"],
            text_color=COLORS["text_white"],
        ).pack(pady=20)

    # ------------------------------------------------------------------------
    # PLAYER MANAGEMENT
    # ------------------------------------------------------------------------
    def _get_player_name(self):
        """Show popup to get player name after the game UI is displayed."""
        dialog = ctk.CTkInputDialog(
            text="Enter your name to start the game:",
            title="Welcome to Snake & Ladder!",
        )
        player_name = dialog.get_input()

        if player_name and player_name.strip():
            self.player_name = player_name.strip()
        else:
            self.player_name = "Player"

    def _show_congratulations_popup(self, player_name: str):
        """Show a congratulations popup dialog when player wins."""
        popup = ctk.CTkToplevel(self)
        popup.title("Congratulations!")
        popup.geometry("400x250")
        popup.configure(fg_color=COLORS["bg_dark"])

        # Make it modal
        popup.transient(self)
        popup.grab_set()

        # Center the popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - 200
        y = (popup.winfo_screenheight() // 2) - 125
        popup.geometry(f"400x250+{x}+{y}")

        # Congratulations message
        ctk.CTkLabel(
            popup,
            text="🎉",
            font=("SF Pro Display", 48),
            text_color=COLORS["success"],
        ).pack(pady=(30, 10))

        ctk.CTkLabel(
            popup,
            text=f"Congratulations {player_name}!",
            font=FONTS["heading"],
            text_color=COLORS["success"],
        ).pack(pady=10)

        ctk.CTkLabel(
            popup,
            text="You guessed correctly!",
            font=FONTS["body"],
            text_color=COLORS["text_white"],
        ).pack(pady=5)

        # OK button
        ctk.CTkButton(
            popup,
            text="OK",
            command=popup.destroy,
            width=150,
            height=40,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
        ).pack(pady=20)

        popup.wait_window()

    # ------------------------------------------------------------------------
    # GAME LOGIC
    # ------------------------------------------------------------------------
    def generate_board(self):
        """Generate a new game board with random snakes and ladders."""
        N = int(self.size_var.get())
        total = N * N

        snake_count = N - 2
        ladder_count = N - 2

        pool = list(range(2, total - 1))
        random.shuffle(pool)

        snake_pos = pool[:snake_count]
        ladder_pos = pool[snake_count : snake_count + ladder_count]

        self.snakes = {s: random.randint(1, s - 1) for s in snake_pos}
        self.ladders = {l: random.randint(l + 1, total) for l in ladder_pos}

        self.solver = SnakeLadderSolver(N, self.snakes, self.ladders)
        self.current_round_id = get_next_round_id()

        # Reset timing for new game
        self.bfs_time = None
        self.dijkstra_time = None
        self.correct_answer = None

        self.draw_board()
        self.show_guess_panel()

    # ------------------------------------------------------------------------
    # BOARD RENDERING
    # ------------------------------------------------------------------------
    def draw_board(self):
        """Draw the game board on the canvas."""
        self.canvas.delete("all")

        N = int(self.size_var.get())
        cell_size = 70
        board_px = N * cell_size

        self.canvas.config(width=board_px, height=board_px)

        # Draw cells
        for r in range(N):
            for c in range(N):
                x1, y1 = c * cell_size, r * cell_size
                x2, y2 = x1 + cell_size, y1 + cell_size

                color = COLORS["cell_dark"] if (r + c) % 2 == 0 else COLORS["cell_light"]
                self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=color, outline="#334155"
                )

                # Calculate cell number
                row = N - r
                num = (row - 1) * N + (c + 1 if row % 2 else N - c)
                self.canvas.create_text(
                    x1 + 5,
                    y1 + 5,
                    anchor="nw",
                    text=str(num),
                    fill=COLORS["text_gray"],
                    font=FONTS["cell"],
                )

        # Draw ladders and snakes
        for start, end in self.ladders.items():
            self._draw_line(start, end, "green")
        for start, end in self.snakes.items():
            self._draw_line(start, end, "red")

        self._scale_board_to_fit(board_px)

    def _scale_board_to_fit(self, board_px):
        """Scale the board to fit within the container."""
        self.board_container.update_idletasks()

        w = self.board_container.winfo_width() - 40
        h = self.board_container.winfo_height() - 40

        scale = min(w / board_px, h / board_px, 1.0)

        self.canvas.scale("all", 0, 0, scale, scale)
        self.canvas.config(width=int(board_px * scale), height=int(board_px * scale))

    def _cell_to_xy(self, cell):
        """Convert cell number to canvas coordinates."""
        N = int(self.size_var.get())
        cell -= 1
        r, c = divmod(cell, N)
        r = N - r - 1
        if (N - r) % 2 == 0:
            c = N - c - 1
        return c * 70 + 35, r * 70 + 35

    def _draw_line(self, start, end, color):
        """Draw a line between two cells (for snakes/ladders)."""
        x1, y1 = self._cell_to_xy(start)
        x2, y2 = self._cell_to_xy(end)
        self.canvas.create_line(x1, y1, x2, y2, width=5, fill=color, smooth=True)

    # ------------------------------------------------------------------------
    # ALGORITHM EXECUTION
    # ------------------------------------------------------------------------
    def run_bfs(self):
        """Run BFS algorithm and display results."""
        if not self.solver:
            self.result_lbl.configure(text="Generate board first!")
            return

        moves, _, elapsed_time = self.solver.bfs_min_dice()
        self.bfs_time = elapsed_time
        self.result_lbl.configure(
            text=f"BFS: {moves} moves (Time: {elapsed_time:.6f}s)"
        )

    def run_dijkstra(self):
        """Run Dijkstra algorithm and display results."""
        if not self.solver:
            self.result_lbl.configure(text="Generate board first!")
            return

        moves, _, elapsed_time = self.solver.dijkstra_min_dice()
        self.dijkstra_time = elapsed_time
        self.result_lbl.configure(
            text=f"Dijkstra: {moves} moves (Time: {elapsed_time:.6f}s)"
        )

    # ------------------------------------------------------------------------
    # GAME FLOW
    # ------------------------------------------------------------------------
    def show_guess_panel(self):
        """Show the guess panel with multiple choice options."""
        for widget in self.right_panel.winfo_children():
            widget.destroy()

        # Run both algorithms to get timing information
        correct, _, bfs_elapsed = self.solver.bfs_min_dice()
        _, _, dijkstra_elapsed = self.solver.dijkstra_min_dice()

        # Store timing and correct answer
        self.bfs_time = bfs_elapsed
        self.dijkstra_time = dijkstra_elapsed
        self.correct_answer = correct

        # Save algorithm timings for this round
        if self.current_round_id:
            save_algorithm_timings(
                round_id=self.current_round_id,
                bfs_time=bfs_elapsed,
                dijkstra_time=dijkstra_elapsed,
            )

        # Generate options
        options = [correct, correct + random.randint(1, 4), max(1, correct - 1)]
        random.shuffle(options)

        ctk.CTkLabel(
            self.right_panel,
            text="Guess minimum dice throws",
            font=FONTS["subheading"],
            text_color=COLORS["text_white"],
        ).pack(pady=15)

        for option in options:
            ctk.CTkButton(
                self.right_panel,
                text=str(option),
                width=200,
                command=lambda x=option: self.evaluate_guess(x, correct),
            ).pack(pady=8)

    def evaluate_guess(self, selected, correct):
        """Evaluate the player's guess and handle win/loss."""
        for widget in self.right_panel.winfo_children():
            widget.destroy()

        if selected == correct:
            # Save player win to database
            if self.player_name and self.current_round_id:
                save_player_win(
                    round_id=self.current_round_id,
                    player_name=self.player_name,
                    correct_answer=correct,
                )

            # Show congratulations popup
            player_display_name = self.player_name if self.player_name else "Player"
            self._show_congratulations_popup(player_display_name)

            txt = f"Congratulations {player_display_name}! 🎉\n\nYou Win!"
            color = COLORS["success"]
        else:
            txt = f"YOU LOSE ❌\nCorrect: {correct}"
            color = COLORS["error"]

        ctk.CTkLabel(
            self.right_panel,
            text=txt,
            font=FONTS["heading"],
            text_color=color,
        ).pack(pady=30)

        ctk.CTkButton(
            self.right_panel,
            text="Play Again",
            command=self.generate_board,
            width=200,
            height=40,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
        ).pack(pady=10)

        ctk.CTkButton(
            self.right_panel,
            text="Exit",
            command=self.destroy,
            fg_color=COLORS["error"],
            width=200,
            height=40,
        ).pack(pady=5)


# ============================================================================
# ENTRY POINT
# ============================================================================
def launch_game():
    """Launch the Snake and Ladder game."""
    app = SnakeLadderUI()
    app.mainloop()


if __name__ == "__main__":
    launch_game()
