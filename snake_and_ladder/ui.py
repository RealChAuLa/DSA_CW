import customtkinter as ctk

def launch_game():
    # Create independent root window
    window = ctk.CTk()
    window.title("Snake and Ladder")
    window.geometry("800x600")

    # Center the window
    window.eval('tk::PlaceWindow . center')

    label = ctk.CTkLabel(
        window,
        text="Snake and Ladder Game\n(Under Development)",
        font=("Arial", 16)
    )
    label.pack(expand=True)

    # Close button (If needed)
    #close_btn = ctk.CTkButton(
    #    window,
    #    text="Exit Game",
    #    command=window.destroy,
    #   font=("Arial", 14)
    #)
    #close_btn.pack(pady=20)

    window.mainloop()