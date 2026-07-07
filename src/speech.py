import tkinter as tk

class SpeechBubble:
    def __init__(self, root):
        self.root = root
        
        # Transparent overlay label container instead of standard solid frame box
        self.bubble_label = tk.Label(
            root,
            text="",
            bg="white",       # Must match main window transparent color flag
            fg="#2C3E50",     # Deep graphite font text color
            font=("Segoe UI", 9, "bold"), # Increased to font size 9 for easy readability
            compound="center", # Places text right on TOP of the background image center bounds
            justify="center",
            wraplength=120,   # Increased wraplength to 120 so more words fit nicely per line
            borderwidth=0,
            highlightthickness=0
        )
        
        # Frame for placing buttons snuggly under the custom cloud asset
        self.btn_frame = tk.Frame(root, bg="white")
        
        self.yes_btn = tk.Button(
            self.btn_frame, 
            text="Yes! 🥤", 
            font=("Segoe UI", 8, "bold"), # Toggled slightly bigger button font
            bg="#D4F6F6", 
            fg="#1F4E5B", 
            bd=0, 
            relief="flat",
            padx=6,
            pady=2,
            cursor="hand2"
        )
        self.no_btn = tk.Button(
            self.btn_frame, 
            text="Later ✨", 
            font=("Segoe UI", 8, "bold"),
            bg="#FFE3E3", 
            fg="#5C2C2C", 
            bd=0, 
            relief="flat",
            padx=6,
            pady=2,
            cursor="hand2"
        )
        
        self.bubble_label.place_forget()
        self.btn_frame.place_forget()
        self.hide_job = None
        self.on_hide_callback = None

    def show(self, message, pet_y, bg_image, is_reminder=False, on_yes=None, on_no=None, on_hide=None):
        if self.hide_job:
            self.root.after_cancel(self.hide_job)
            
        self.bubble_label.config(image=bg_image, text=message)
        self.on_hide_callback = on_hide
        
        # Shifted up to -92 to give the newly scaled larger bubble perfect headroom
        bubble_y = pet_y - 92
        self.bubble_label.place(relx=0.5, y=bubble_y, anchor="n")
        
        if is_reminder:
            self.yes_btn.config(command=on_yes)
            self.no_btn.config(command=on_no)
            self.yes_btn.pack(side="left", padx=5, expand=True)
            self.no_btn.pack(side="right", padx=5, expand=True)
            # Positioned nicely below the new larger bubble boundaries
            self.btn_frame.place(relx=0.5, y=bubble_y + 90, anchor="n")
        else:
            self.btn_frame.place_forget()

        if not is_reminder:
            self.hide_job = self.root.after(4000, self.hide)

    def hide(self):
        self.bubble_label.place_forget()
        self.btn_frame.place_forget()
        self.hide_job = None
        if self.on_hide_callback:
            self.on_hide_callback()
            self.on_hide_callback = None