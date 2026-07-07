import tkinter as tk

class SpeechBubble:
    def __init__(self, root):
        self.root = root
        self.bubble = tk.Label(
            root,
            text="",
            bg="#FFF8DC",
            fg="#333333",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=6,
            relief="solid",
            bd=1,
            wraplength=140
        )
        self.bubble.place_forget()
        self.hide_job = None

    def show(self, message, pet_y):
        if self.hide_job:
            self.root.after_cancel(self.hide_job)
            
        self.bubble.config(text=message)
        
        # Boo ke head ke just upar dynamically position karne ke liye (pet_y - 45) use kiya hai
        bubble_y = pet_y - 45
        self.bubble.place(relx=0.5, y=bubble_y, anchor="n")

        # Hide after 3 seconds
        self.hide_job = self.root.after(3000, self.hide)

    def hide(self):
        self.bubble.place_forget()
        self.hide_job = None