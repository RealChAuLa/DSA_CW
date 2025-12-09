import customtkinter as ctk

def launch_game():
    window = ctk.CTkToplevel()
    window.title("Traffic Simulation")
    window.geometry("400x200")

    label = ctk.CTkLabel(
        window,
        text="Traffic Simulation Game\n(Under Development)",
        font=("Arial", 16)
    )
    label.pack(expand=True)
