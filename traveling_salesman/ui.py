import customtkinter as ctk

def launch_game():
    window = ctk.CTkToplevel()
    window.title("Traveling Salesman Problem")
    window.geometry("400x200")

    label = ctk.CTkLabel(
        window,
        text="Traveling Salesman Problem\n(Under Development)",
        font=("Arial", 16)
    )
    label.pack(expand=True)
