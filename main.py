import customtkinter as ctk

# -----------------------------
# App Configuration
# -----------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# -----------------------------
# Main Application Class
# -----------------------------
class GameMenuApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PDSA Games")

        # Fullscreen setup
        self.state('zoomed')  # Windows
        self.attributes('-fullscreen', True)  # Linux/Mac fallback

        # Allow exit with Escape
        self.bind("<Escape>", lambda e: self.quit())

        # Color scheme
        self.bg_dark = "#0a0e27"
        self.card_bg = "#151932"
        self.accent = "#6366f1"
        self.accent_hover = "#4f46e5"
        self.text_primary = "#f8fafc"
        self.text_secondary = "#94a3b8"

        self.configure(fg_color=self.bg_dark)

        self._create_widgets()

    def _create_widgets(self):
        # Main container centered
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.place(relx=0.5, rely=0.5, anchor="center")

        # Header section - centered
        header = ctk.CTkFrame(main_container, fg_color="transparent")
        header.pack(pady=(0, 60))

        title = ctk.CTkLabel(
            header,
            text="Algorithm Arcade",
            font=("SF Pro Display", 56, "bold"),
            text_color=self.text_primary
        )
        title.pack()

        subtitle = ctk.CTkLabel(
            header,
            text="Master data structures through interactive challenges",
            font=("SF Pro Text", 18),
            text_color=self.text_secondary
        )
        subtitle.pack(pady=(12, 0))

        # Games container - horizontal layout
        games_container = ctk.CTkFrame(main_container, fg_color="transparent")
        games_container.pack()

        # Game data
        games = [
            {
                "icon": "🎲",
                "title": "Snake &\nLadder",
                "color": "#10b981",
                "cmd": self.open_snake_and_ladder
            },
            {
                "icon": "🚗",
                "title": "Traffic\nFlow",
                "color": "#f59e0b",
                "cmd": self.open_traffic_simulation
            },
            {
                "icon": "🧳",
                "title": "Traveling\nSalesman",
                "color": "#3b82f6",
                "cmd": self.open_tsp
            },
            {
                "icon": "🗼",
                "title": "Tower of\nHanoi",
                "color": "#8b5cf6",
                "cmd": self.open_hanoi
            },
            {
                "icon": "♕",
                "title": "Eight\nQueens",
                "color": "#ec4899",
                "cmd": self.open_eight_queens
            }
        ]

        # Create square cards horizontally
        for game in games:
            self._create_square_card(games_container, game)

        # Exit button - bottom center
        exit_container = ctk.CTkFrame(main_container, fg_color="transparent")
        exit_container.pack(pady=(50, 0))

        exit_btn = ctk.CTkButton(
            exit_container,
            text="✕  Exit",
            font=("SF Pro Text", 16, "bold"),
            fg_color="transparent",
            hover_color="#dc2626",
            text_color=self.text_secondary,
            border_width=2,
            border_color="#374151",
            corner_radius=12,
            width=140,
            height=45,
            command=self.quit
        )
        exit_btn.pack()

        # Exit button hover effect
        def exit_on_enter(e):
            exit_btn.configure(border_color="#ef4444", text_color="#ef4444")

        def exit_on_leave(e):
            exit_btn.configure(border_color="#374151", text_color=self.text_secondary)

        exit_btn.bind("<Enter>", exit_on_enter)
        exit_btn.bind("<Leave>", exit_on_leave)

    def _create_square_card(self, parent, game):
        # Square card container
        card = ctk.CTkFrame(
            parent,
            fg_color=self.card_bg,
            corner_radius=20,
            border_width=2,
            border_color="#1e293b",
            width=200,
            height=200
        )
        card.pack(side="left", padx=20)
        card.pack_propagate(False)

        # Make entire card clickable
        card.bind("<Button-1>", lambda e: self._launch_game(game["cmd"]))
        card.configure(cursor="hand2")

        # Content container - centered
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")

        # Icon
        icon = ctk.CTkLabel(
            content,
            text=game["icon"],
            font=("Segoe UI Emoji", 64)
        )
        icon.pack(pady=(0, 15))

        # Title
        title = ctk.CTkLabel(
            content,
            text=game["title"],
            font=("SF Pro Display", 18, "bold"),
            text_color=self.text_primary,
            justify="center"
        )
        title.pack()

        # Color indicator bar at bottom
        color_bar = ctk.CTkFrame(
            card,
            fg_color=game["color"],
            height=4,
            corner_radius=0
        )
        color_bar.place(relx=0, rely=1, anchor="sw", relwidth=1)

        # Hover effects
        def on_enter(e):
            card.configure(border_color=game["color"], border_width=3)

        def on_leave(e):
            card.configure(border_color="#1e293b", border_width=2)

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

        # Make all child widgets trigger the same hover
        for widget in [content, icon, title]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", lambda e, cmd=game["cmd"]: self._launch_game(cmd))
            widget.configure(cursor="hand2")

    def _launch_game(self, game_command):
        """Launch game and close menu completely"""
        self.destroy()  # Close menu completely
        game_command()  # Launch the game
        # After game closes, restart the menu
        self._restart_menu()

    def _restart_menu(self):
        """Restart the main menu after game closes"""
        import subprocess
        import sys
        import os

        # Get the path to main.py
        main_path = os.path.abspath(__file__)

        # Restart the menu
        subprocess.Popen([sys.executable, main_path])

    # -----------------------------
    # Game Launchers
    # -----------------------------
    def open_snake_and_ladder(self):
        from snake_and_ladder.ui import launch_game
        launch_game()

    def open_traffic_simulation(self):
        from traffic_simulation.ui import launch_game
        launch_game()

    def open_tsp(self):
        from traveling_salesman.ui import launch_game
        launch_game()

    def open_hanoi(self):
        from tower_of_hanoi.ui import launch_game
        launch_game()

    def open_eight_queens(self):
        from eight_queens.ui import launch_game
        launch_game()


# -----------------------------
# Entry Point
# -----------------------------
if __name__ == "__main__":
    app = GameMenuApp()
    app.mainloop()