import tkinter as tk
from ui.speech_bubble import SpeechBubble

class PetWindow:
    def __init__(self, width=160, height=200, on_drag_end=None, on_double_click=None):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        
        # Transparent background setup
        self.root.config(bg="white")
        self.root.wm_attributes("-transparentcolor", "white")
        
        self.width = width
        self.height = height
        self.on_drag_end = on_drag_end
        self.on_double_click = on_double_click

        # Default placement: bottom right corner of the screen
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.x = screen_w - self.width - 20
        self.y = screen_h - self.height - 50
        self.root.geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")

        # The label widget displaying the pet sprite
        self.label = tk.Label(
            self.root,
            bg="white",
            borderwidth=0,
            highlightthickness=0
        )
        # Position label inside the window (leaving padding for speech bubble above it)
        self.base_pet_x = 30
        self.base_pet_y = 90
        self.label.place(x=self.base_pet_x, y=self.base_pet_y)

        # Instantiate SpeechBubble inside the root window
        self.speech_bubble = SpeechBubble(self.root)

        # Dragging state
        self.drag_start_x = 0
        self.drag_start_y = 0

        # Bind mouse interaction events for dragging and double clicking
        self.label.bind("<Button-1>", self._start_drag)
        self.label.bind("<B1-Motion>", self._drag)
        self.label.bind("<ButtonRelease-1>", self._end_drag)
        self.label.bind("<Double-Button-1>", self._double_click)

    def set_image(self, photo_image):
        """Updates the label to display the given PhotoImage."""
        self.label.config(image=photo_image)
        self.label.image = photo_image  # Keep reference to prevent GC

    def set_pet_offset(self, x, y):
        """Sets the position of the pet label relative to the window container."""
        self.label.place_configure(x=x, y=y)

    def set_window_position(self, x, y):
        """Sets the coordinates of the root window."""
        self.x = x
        self.y = y
        self.root.geometry(f"+{x}+{y}")

    def get_window_position(self):
        """Returns the current window (x, y) coordinates."""
        return self.root.winfo_x(), self.root.winfo_y()

    def say(self, text, duration_ms=4000):
        """Displays a dialogue bubble above the pet's current Y coordinate."""
        pet_y = self.label.winfo_y()
        self.speech_bubble.show(text, pet_y, duration_ms)

    def hide_bubble(self):
        """Hides the active dialogue bubble."""
        self.speech_bubble.hide()

    def _start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def _drag(self, event):
        new_x = self.root.winfo_x() + event.x - self.drag_start_x
        new_y = self.root.winfo_y() + event.y - self.drag_start_y
        self.root.geometry(f"+{new_x}+{new_y}")
        self.x = new_x
        self.y = new_y

    def _end_drag(self, event):
        if self.on_drag_end:
            self.on_drag_end(self.x, self.y)

    def _double_click(self, event):
        if self.on_double_click:
            self.on_double_click()

    def start_loop(self):
        """Starts the main event loop."""
        self.root.mainloop()

    def after(self, ms, callback):
        """Schedules a callback after ms milliseconds."""
        return self.root.after(ms, callback)
