import tkinter as tk

class SpeechBubble:
    def __init__(self, root):
        """Initializes a dynamic text-adaptive speech bubble container using native geometry auto-sizing."""
        self.root = root
        
        # Clean minimalist adaptive frame wrapper (Auto-resizes based on child label packing)
        self.bubble = tk.Frame(
            root,
            bg="#FFFDF3",       # Soft ivory cream elegant tone
            bd=1,
            relief="solid",
            highlightthickness=0
        )
        # Soft aesthetic border outline configuration
        self.bubble.config(highlightbackground="#E2DCB9", highlightcolor="#E2DCB9")
        
        # Native label that scales vertically and horizontally automatically based on string length
        self.text_label = tk.Label(
            self.bubble,
            text="",
            bg="#FFFDF3",
            fg="#2C3E50",       # Deep slate graphite readable color
            font=("Segoe UI", 9, "bold"),
            padx=12,            # Safe horizontal inner padding
            pady=8,             # Safe vertical inner padding
            wraplength=130,     # Wraps text to next line safely if message is long
            justify="center"
        )
        self.text_label.pack(side="top", fill="both", expand=True)
        
        # Action interactive notification buttons panel frame layer
        self.btn_frame = tk.Frame(self.bubble, bg="#FFFDF3")
        
        self.yes_btn = tk.Button(
            self.btn_frame, 
            text="Yes! 🥤", 
            font=("Segoe UI", 8, "bold"), 
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
        
        self.bubble.place_forget()
        self.btn_frame.place_forget()
        self.hide_job = None
        self.on_hide_callback = None

    def show(self, message, pet_y, is_reminder=False, on_yes=None, on_no=None, on_hide=None):
        """Displays the adaptive bubble, scaling its dimensions instantly to fit the message perfectly."""
        if self.hide_job:
            self.root.after_cancel(self.hide_job)
            
        self.text_label.config(text=message)
        self.on_hide_callback = on_hide
        
        if is_reminder:
            self.yes_btn.config(command=on_yes)
            self.no_btn.config(command=on_no)
            self.yes_btn.pack(side="left", padx=5, pady=4, expand=True)
            self.no_btn.pack(side="right", padx=5, pady=4, expand=True)
            self.btn_frame.pack(side="bottom", fill="x", padx=4)
        else:
            self.btn_frame.pack_forget()
            
        # Forces Tkinter to calculate internal geometry properties before drawing on screen
        self.bubble.update_idletasks()
        bubble_height = self.bubble.winfo_reqheight()
        
        # Absolute dynamic offset to float seamlessly above Boo's head regardless of text size
        bubble_y = pet_y - bubble_height - 6
        self.bubble.place(relx=0.5, y=bubble_y, anchor="n")

        if not is_reminder:
            self.hide_job = self.root.after(4000, self.hide)

    def hide(self):
        """Removes the adaptive bubble framework cleanly from window hierarchy context."""
        self.bubble.place_forget()
        self.btn_frame.place_forget()
        self.hide_job = None
        if self.on_hide_callback:
            self.on_hide_callback()
            self.on_hide_callback = None