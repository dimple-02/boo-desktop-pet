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

        # Input box subframe at the bottom
        self.input_frame = tk.Frame(self.bubble, bg="#FFFDF3")
        self.input_frame.pack(side="bottom", fill="x", padx=4, pady=(0, 4))

        self.entry = tk.Entry(
            self.input_frame,
            bg="white",
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

    def show(self, text, pet_y, duration_ms=4000):
        """
        Displays the speech bubble with the given text placed dynamically
        above the pet's current Y coordinate.
        """
        # Cancel any pending auto-hide timers
        self._cancel_hide_timer()

        self.text_label.config(text=text)
        
        # Trigger geometry calculations to obtain winfo_reqheight
        self.bubble.update_idletasks()
        bubble_height = self.bubble.winfo_reqheight()

        # Calculate coordinates (placed 6px above the pet Y coordinate, centered horizontally)
        bubble_y = pet_y - bubble_height - 6
        self.bubble.place(relx=0.5, y=bubble_y, anchor="n")

        # Schedule auto-hide if a duration is specified and user is not focusing on the entry
        if duration_ms > 0 and self.root.focus_get() != self.entry:
            self.hide_job = self.root.after(duration_ms, self.hide)

    def hide(self):
        """Hides the speech bubble frame from the window geometry layout."""
        self.bubble.place_forget()
        self._cancel_hide_timer()

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
