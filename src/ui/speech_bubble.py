import tkinter as tk

class SpeechBubble:
    def __init__(self, root):
        self.root = root
        
        # Dynamic text container frame
        self.bubble = tk.Frame(
            root,
            bg="#FFFDF3",
            bd=1,
            relief="solid",
            highlightthickness=0
        )
        self.bubble.config(highlightbackground="#E2DCB9", highlightcolor="#E2DCB9")

        # Label representing the text contents
        self.text_label = tk.Label(
            self.bubble,
            text="",
            bg="#FFFDF3",
            fg="#2C3E50",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=8,
            wraplength=130,
            justify="center"
        )
        self.text_label.pack(side="top", fill="both", expand=True)

        self.bubble.place_forget()
        self.hide_job = None

    def show(self, text, pet_y, duration_ms=4000):
        """
        Displays the speech bubble with the given text placed dynamically
        above the pet's current Y coordinate.
        """
        # Cancel any pending auto-hide timers
        if self.hide_job:
            self.root.after_cancel(self.hide_job)
            self.hide_job = None

        self.text_label.config(text=text)
        
        # Trigger geometry calculations to obtain winfo_reqheight
        self.bubble.update_idletasks()
        bubble_height = self.bubble.winfo_reqheight()

        # Calculate coordinates (placed 6px above the pet Y coordinate, centered horizontally)
        bubble_y = pet_y - bubble_height - 6
        self.bubble.place(relx=0.5, y=bubble_y, anchor="n")

        # Schedule auto-hide if a duration is specified
        if duration_ms > 0:
            self.hide_job = self.root.after(duration_ms, self.hide)

    def hide(self):
        """Hides the speech bubble frame from the window geometry layout."""
        self.bubble.place_forget()
        if self.hide_job:
            self.root.after_cancel(self.hide_job)
            self.hide_job = None
