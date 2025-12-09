import customtkinter as ctk

def launch_game():
    window = ctk.CTkToplevel()
    window.title("Eight Queens Puzzle")
    window.geometry("400x200")

    label = ctk.CTkLabel(
        window,
        text="Eight Queens Puzzle\n(Under Development)",
        font=("Arial", 16)
    )
    label.pack(expand=True)
