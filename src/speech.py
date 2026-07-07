import tkinter as tk

class SpeechBubble:
    def __init__(self, root):
        self.root = root
        
        # Main bubble container window (Toplevel use karenge taaki buttons cleanly overlay ho sakein)
        self.bubble = tk.Frame(
            root,
            bg="#FFF8DC",
            relief="solid",
            bd=1
        )
        
        self.text_label = tk.Label(
            self.bubble,
            text="",
            bg="#FFF8DC",
            fg="#333333",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=6,
            wraplength=140
        )
        self.text_label.pack(side="top", fill="x")
        
        # Frame for interactive buttons
        self.btn_frame = tk.Frame(self.bubble, bg="#FFF8DC")
        
        self.yes_btn = tk.Button(
            self.btn_frame, 
            text="Yes! 💧", 
            font=("Segoe UI", 8, "bold"),
            bg="#AEEEEE", 
            fg="#333333", 
            bd=1, 
            relief="groove"
        )
        self.no_btn = tk.Button(
            self.btn_frame, 
            text="Later ⏳", 
            font=("Segoe UI", 8, "bold"),
            bg="#FFC0CB", 
            fg="#333333", 
            bd=1, 
            relief="groove"
        )
        
        self.bubble.place_forget()
        self.hide_job = None
        self.on_hide_callback = None

    def show(self, message, pet_y, is_reminder=False, on_yes=None, on_no=None, on_hide=None):
        # Existing timers cancel karein
        if self.hide_job:
            self.root.after_cancel(self.hide_job)
            
        self.text_label.config(text=message)
        self.on_hide_callback = on_hide
        
        # Pack or unpack buttons based on message context
        if is_reminder:
            self.yes_btn.config(command=on_yes)
            self.no_btn.config(command=on_no)
            self.yes_btn.pack(side="left", padx=5, pady=2, expand=True)
            self.no_btn.pack(side="right", padx=5, pady=2, expand=True)
            self.btn_frame.pack(side="bottom", fill="x", pady=2)
        else:
            self.btn_frame.pack_forget()  # Regular chatter needs no buttons
            
        # Position bubble cleanly above Boo's head
        bubble_y = pet_y - (65 if is_reminder else 45)
        self.bubble.place(relx=0.5, y=bubble_y, anchor="n")

        # Auto-hide loops ONLY for regular phrases. Reminders stay forever until clicked!
        if not is_reminder:
            self.hide_job = self.root.after(4000, self.hide)

    def hide(self):
        self.bubble.place_forget()
        self.hide_job = None
        if self.on_hide_callback:
            self.on_hide_callback()
            self.on_hide_callback = None