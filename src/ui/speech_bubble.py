import tkinter as tk

class SpeechBubble:
    def __init__(self, root, on_submit=None):
        self.root = root
        self.on_submit = on_submit
        
        # Dynamic text container frame
        self.bubble = tk.Frame(
            root,
            bg="#FFFDF3",
            bd=1,
            relief="solid",
            highlightthickness=0
        )
        self.bubble.config(highlightbackground="#E2DCB9", highlightcolor="#E2DCB9")

        # Label representing the text contents (increased wraplength to 180 to fit AI answers)
        self.text_label = tk.Label(
            self.bubble,
            text="",
            bg="#FFFDF3",
            fg="#2C3E50",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=8,
            wraplength=180,
            justify="center"
        )
        self.text_label.pack(side="top", fill="both", expand=True)

        # Input box subframe at the bottom (collapsed by default)
        self.input_frame = tk.Frame(self.bubble, bg="#FFFDF3")

        # Off-white Entry to avoid the transparent color ("white") key collision!
        self.entry = tk.Entry(
            self.input_frame,
            bg="#FFFFFE",
            fg="#2C3E50",
            font=("Segoe UI", 8),
            bd=1,
            relief="solid",
            highlightthickness=0
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(2, 2))

        self.submit_btn = tk.Button(
            self.input_frame,
            text="Ask",
            font=("Segoe UI", 8, "bold"),
            bg="#D4F6F6",
            fg="#1F4E5B",
            bd=0,
            relief="flat",
            padx=6,
            pady=1,
            cursor="hand2",
            command=self._on_submit
        )
        self.submit_btn.pack(side="right", padx=(0, 2))

        # Hide states
        self.bubble.place_forget()
        self.hide_job = None

        # Event bindings
        self.entry.bind("<Return>", self._on_submit)
        self.entry.bind("<FocusIn>", self._cancel_hide_timer)
        self.entry.bind("<Button-1>", self._on_entry_click)

    def show(self, text, pet_y, duration_ms=4000, show_input=False):
        """
        Displays the speech bubble with the given text.
        If show_input is True, packs the input frame and forces focus.
        Otherwise, hides the input frame and schedules auto-hide.
        """
        self._cancel_hide_timer()
        self.text_label.config(text=text)
        
        if show_input:
            self.input_frame.pack(side="bottom", fill="x", padx=4, pady=(0, 4))
        else:
            self.input_frame.pack_forget()

        # Trigger geometry calculations to obtain winfo_reqheight
        self.bubble.update_idletasks()
        bubble_height = self.bubble.winfo_reqheight()

        # Calculate coordinates (placed 6px above the pet Y coordinate, centered horizontally)
        bubble_y = pet_y - bubble_height - 6
        self.bubble.place(relx=0.5, y=bubble_y, anchor="n")

        if show_input:
            self.entry.focus_force()
        elif duration_ms > 0:
            self.hide_job = self.root.after(duration_ms, self.hide)

    def show_chat_input(self, pet_y):
        """Displays the speech bubble with the input entry box visible and focused."""
        self._cancel_hide_timer()

        # If the bubble is not currently showing, set default helper text
        if not self.bubble.winfo_manager():
            self.text_label.config(text="How can I help? 👻")
            
        self.input_frame.pack(side="bottom", fill="x", padx=4, pady=(0, 4))
        
        # Trigger layout updates
        self.bubble.update_idletasks()
        bubble_height = self.bubble.winfo_reqheight()
        bubble_y = pet_y - bubble_height - 6
        self.bubble.place(relx=0.5, y=bubble_y, anchor="n")
        
        self.entry.focus_force()

    def hide(self):
        """Hides the speech bubble frame from the window geometry layout."""
        self.bubble.place_forget()
        self._cancel_hide_timer()

    def _on_entry_click(self, event=None):
        """Forces focus when clicked to bypass OS overrideredirect restrictions."""
        self.entry.focus_force()

    def _on_submit(self, event=None):
        """Processes user text input and triggers callback."""
        text = self.entry.get().strip()
        if text:
            self.entry.delete(0, tk.END)
            # Temporarily shift focus away to allow proper layout updates if needed
            self.root.focus_set()
            if self.on_submit:
                self.on_submit(text)

    def _cancel_hide_timer(self, event=None):
        """Cancels the hide job timer so the speech bubble stays open during interaction."""
        if self.hide_job:
            self.root.after_cancel(self.hide_job)
            self.hide_job = None
