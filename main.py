import customtkinter as ctk

# -----------------------------
# App Configuration
# -----------------------------
ctk.set_appearance_mode("System")      # Light / Dark follows system
ctk.set_default_color_theme("blue")

APP_WIDTH = 500
APP_HEIGHT = 500


# -----------------------------
# Main Application Class
# -----------------------------
class GameMenuApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PDSA Game Suite")
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.resizable(False, False)

        self._create_widgets()

    def _create_widgets(self):
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Programming Data Structures & Algorithms",
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=30)

        subtitle_label = ctk.CTkLabel(
            self,
            text="Select a Game",
            font=("Arial", 14)
        )
        subtitle_label.pack(pady=10)

        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20)

        ctk.CTkButton(
            button_frame,
            text="Snake and Ladder",
            width=250,
            command=self.open_snake_and_ladder
        ).pack(pady=8)

        ctk.CTkButton(
            button_frame,
            text="Traffic Simulation",
            width=250,
            command=self.open_traffic_simulation
        ).pack(pady=8)

        ctk.CTkButton(
            button_frame,
            text="Traveling Salesman Problem",
            width=250,
            command=self.open_tsp
        ).pack(pady=8)

        ctk.CTkButton(
            button_frame,
            text="Tower of Hanoi",
            width=250,
            command=self.open_hanoi
        ).pack(pady=8)

        ctk.CTkButton(
            button_frame,
            text="Eight Queens Puzzle",
            width=250,
            command=self.open_eight_queens
        ).pack(pady=8)

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
