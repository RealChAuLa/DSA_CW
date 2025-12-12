import customtkinter as ctk
from .game import Game

def draw_ui(game: Game) -> None:
	window = ctk.CTk()
	window.title("Traveling Salesman Problem")
	window.geometry("1280x720")        # Color scheme

	bg_dark = "#0a0e27"
	card_bg = "#151932"
	accent = "#6366f1"
	accent_hover = "#4f46e5"
	text_primary = "#f8fafc"
	text_secondary = "#94a3b8"

	window.configure(fg_color=bg_dark)

	# --- Main layout split (Left + Right) ---
	main_frame = ctk.CTkFrame(window, fg_color="transparent")
	main_frame.pack(fill="both", expand=True, padx=20, pady=20)

	# Left side (Graph top, Logs bottom)
	left_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
	left_frame.pack(side="left", fill="both", expand=True, padx=10)

	graph_frame = ctk.CTkFrame(left_frame, height=500)
	graph_frame.pack(fill="x", pady=(0, 10))
	graph_frame.pack_propagate(False)
	ctk.CTkLabel(graph_frame, text="Graph", font=("SF Pro Display", 18)).pack(pady=20)

	logs_frame = ctk.CTkFrame(left_frame, height=180)
	logs_frame.pack(fill="x")
	logs_frame.pack_propagate(False)
	ctk.CTkLabel(logs_frame, text="Algorithm running logs", font=("SF Pro Display", 16)).pack(pady=20)

	# Right side (game interaction)
	right_frame = ctk.CTkFrame(main_frame, width=300, fg_color="transparent")
	right_frame.pack(side="right", fill="both", expand=False, padx=10)

	title = ctk.CTkLabel(right_frame, text="Traveling Salesman", font=("SF Pro Display", 20))
	title.pack(pady=20)

	main_city_label = ctk.CTkLabel(right_frame, text=f"Main city: {game.main_city}", font=("SF Pro Display", 16))
	main_city_label.pack(pady=10)

	select_label = ctk.CTkLabel(right_frame, text="Select cities", font=("SF Pro Display", 16))
	select_label.pack(pady=10)

	# list of cities
	city_frame = ctk.CTkFrame(right_frame, fg_color=card_bg)
	city_frame.pack(pady=5)

	row1 = ctk.CTkFrame(city_frame, fg_color="transparent")
	row1.pack(pady=(10, 5))
	row2 = ctk.CTkFrame(city_frame, fg_color="transparent")
	row2.pack(pady=(5, 10))

	cities = "ABCDEFGHIJ"

	for c in cities[:5]:
		btn = ctk.CTkCheckBox(row1, text=c)
		btn.pack(side="left", padx=3)

	for c in cities[5:]:
		btn = ctk.CTkCheckBox(row2, text=c)
		btn.pack(side="left", padx=3)

	guess_label = ctk.CTkLabel(right_frame, text="Guess path", font=("SF Pro Display", 16))
	guess_label.pack(pady=(20, 5))

	guess_entry = ctk.CTkEntry(right_frame, width=200)
	guess_entry.pack(pady=5)

	check_button = ctk.CTkButton(right_frame, text="Check")
	check_button.pack(pady=20)

	window.mainloop()

def show_win() -> None:
	popup = ctk.CTkToplevel()
	popup.title("Result")
	popup.geometry("250x150")

	ctk.CTkLabel(popup, text="You won!", font=("SF Pro Display", 18)).pack(pady=20)
	ctk.CTkButton(popup, text="OK", command=popup.destroy).pack(pady=10)

def show_lose(correct_path: str) -> None:
	popup = ctk.CTkToplevel()
	popup.title("Result")
	popup.geometry("300x180")

	ctk.CTkLabel(popup, text="You lose!", font=("SF Pro Display", 18)).pack(pady=20)
	ctk.CTkLabel(popup, text=f"Correct Path:\n{correct_path}", font=("Arial", 14)).pack(pady=10)
	ctk.CTkButton(popup, text="OK", command=popup.destroy).pack(pady=10)
