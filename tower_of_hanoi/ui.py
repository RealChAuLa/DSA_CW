import customtkinter as ctk

def launch_game():
    # Create independent root window
    window = ctk.CTk()
    window.title("Tower of Hanoi")
    window.geometry("400x200")

    label = ctk.CTkLabel(
        window,
        text="Tower of Hanoi Game\n(Under Development)",
        font=("Arial", 16)
    )
    label.pack(expand=True)

    # Close button (If needed)
    # close_btn = ctk.CTkButton(
    #    window,
    #    text="Exit Game",
    #    command=window.destroy,
    #   font=("Arial", 14)
    # )
    # close_btn.pack(pady=20)

    window.mainloop()
