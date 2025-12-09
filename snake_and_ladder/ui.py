import customtkinter as ctk

def launch_game():
    window = ctk.CTkToplevel()
    window.title("Snake and Ladder")
    window.geometry("400x200")

    label = ctk.CTkLabel(
        window,
        text="Snake and Ladder Game\n(Under Development)",
        font=("Arial", 16)
    )
    label.pack(expand=True)
