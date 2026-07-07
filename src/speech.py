import tkinter as tk


class SpeechBubble:

    def __init__(self, root):

        self.root = root

        self.bubble = tk.Label(
            root,
            text="",
            bg="#FFF8DC",
            fg="#333333",
            font=("Segoe UI", 10),
            padx=12,
            pady=8,
            relief="solid",
            bd=1
        )

        self.bubble.place_forget()

    def show(self, message):

        self.bubble.config(text=message)

        # Bubble appears above Boo
        self.bubble.place(relx=0.5, y=10, anchor="n")

        # Hide after 3 seconds
        self.root.after(3000, self.hide)

    def hide(self):

        self.bubble.place_forget()