import customtkinter as ctk
from .game import Game

def draw_ui(game: Game) -> None:
	window = ctk.CTk()
	window.title("Traveling Salesman Problem")
	window.geometry("1000x600")

	# --- Main layout split (Left + Right) ---
	main_frame = ctk.CTkFrame(window)
	main_frame.pack(fill="both", expand=True, padx=20, pady=20)

	# Left side (Graph top, Logs bottom)
	left_frame = ctk.CTkFrame(main_frame)
	left_frame.pack(side="left", fill="both", expand=True, padx=10)

	graph_frame = ctk.CTkFrame(left_frame, height=350)
	graph_frame.pack(fill="both", expand=True, pady=(0, 10))
	ctk.CTkLabel(graph_frame, text="Graph", font=("Arial", 18)).pack(pady=20)

	logs_frame = ctk.CTkFrame(left_frame)
	logs_frame.pack(fill="both", expand=True)
	ctk.CTkLabel(logs_frame, text="Algorithm running logs", font=("Arial", 16)).pack(pady=20)

	# Right side (game interaction)
	right_frame = ctk.CTkFrame(main_frame, width=300)
	right_frame.pack(side="right", fill="both", expand=False, padx=10)

	title = ctk.CTkLabel(right_frame, text="Traveling Salesman", font=("Arial", 20))
	title.pack(pady=20)

	main_city_label = ctk.CTkLabel(right_frame, text=f"Main city: {game.main_city}", font=("Arial", 16))
	main_city_label.pack(pady=10)

	select_label = ctk.CTkLabel(right_frame, text="Select cities", font=("Arial", 16))
	select_label.pack(pady=10)

	# list of cities
	city_frame = ctk.CTkFrame(right_frame)
	city_frame.pack(pady=5)

	for c in "ABCDEFGHIJ":
		btn = ctk.CTkCheckBox(city_frame, text=c)
		btn.pack(side="left", padx=1)

	guess_label = ctk.CTkLabel(right_frame, text="Guess path", font=("Arial", 16))
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

	ctk.CTkLabel(popup, text="You won!", font=("Arial", 18)).pack(pady=20)
	ctk.CTkButton(popup, text="OK", command=popup.destroy).pack(pady=10)

def show_lose(correct_path: str) -> None:
	popup = ctk.CTkToplevel()
	popup.title("Result")
	popup.geometry("300x180")

	ctk.CTkLabel(popup, text="You lose!", font=("Arial", 18)).pack(pady=20)
	ctk.CTkLabel(popup, text=f"Correct Path:\n{correct_path}", font=("Arial", 14)).pack(pady=10)
	ctk.CTkButton(popup, text="OK", command=popup.destroy).pack(pady=10)
