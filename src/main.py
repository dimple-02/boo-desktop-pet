import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk
import random
from speech import SpeechBubble

WIDTH = 200
HEIGHT = 240

class Boo:
    def __init__(self):
        self.root = tk.Tk()

        # Remove title bar
        self.root.overrideredirect(True)

        # Always on top
        self.root.attributes("-topmost", True)

        # Transparent background setup
        self.root.config(bg="white")
        self.root.wm_attributes("-transparentcolor", "white")

        # Bottom-right positioning layout
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = screen_width - WIDTH - 20
        y = screen_height - HEIGHT - 60

        self.root.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")

        # Resolve asset base paths cleanly
        BASE_DIR = Path(__file__).resolve().parent.parent
        idle_path = BASE_DIR / "assets" / "images" / "boo_idle.png"
        blink_path = BASE_DIR / "assets" / "images" / "boo_blink.png"

        # Load and scale pet assets to 140x140
        idle = Image.open(idle_path)
        idle = idle.resize((140, 140), Image.LANCZOS)

        blink = Image.open(blink_path)
        blink = blink.resize((140, 140), Image.LANCZOS)

        self.idle_photo = ImageTk.PhotoImage(idle)
        self.blink_photo = ImageTk.PhotoImage(blink)

        # Main Pet Presentation Layer
        self.label = tk.Label(
            self.root,
            image=self.idle_photo,
            bg="white",
            borderwidth=0,
            highlightthickness=0
        )

        # Base Y ko window ke bottom ke close rakha hai taaki niche se na kate
        self.base_y = 95
        self.current_y = self.base_y
        
        # Centered horizontally inside the 200px window
        self.label.place(x=30, y=self.base_y)

        # Initialize speech manager overlay module
        self.speech = SpeechBubble(self.root)

        # Event Wireframes
        self.label.bind("<Double-Button-1>", self.say_hi)
        self.make_draggable()

        # Animation State Engines
        self.root.after(3000, self.blink)
        self.float_offset = 0
        self.float_direction = 1
        self.animate()

        self.root.mainloop()

    # --- Blinking Animation Control Loops ---
    def blink(self):
        self.label.config(image=self.blink_photo)
        self.root.after(180, self.open_eyes)

    def open_eyes(self):
        self.label.config(image=self.idle_photo)
        next_blink = random.randint(4000, 8000)
        self.root.after(next_blink, self.blink)

    # --- Floating Bobbing Loops ---
    def animate(self):
        self.float_offset += self.float_direction

        # Gentle floating boundary
        if self.float_offset >= 6:
            self.float_direction = -1
        elif self.float_offset <= -6:
            self.float_direction = 1

        self.current_y = self.base_y + self.float_offset
        self.label.place_configure(
            x=30,
            y=self.current_y
        )
        self.root.after(60, self.animate)

    # --- Window Drag Hooks ---
    def make_draggable(self):
        self.label.bind("<Button-1>", self.start_move)
        self.label.bind("<B1-Motion>", self.move)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def move(self, event):
        x = self.root.winfo_x() + event.x - self.x
        y = self.root.winfo_y() + event.y - self.y
        self.root.geometry(f"+{x}+{y}")

    # --- Dialogue Generation Event Callbacks ---
    def say_hi(self, event=None):
        messages = [
            "Hi! I'm Boo 👻",
            "You're doing amazing! 🌸",
            "Don't forget water! 💧",
            "I'm cheering for you! ⭐",
            "Let's code together! 💜"
        ]
        # Boo ke current dynamic Y coordinate ko pass kiya taaki bubble uske close bane
        self.speech.show(random.choice(messages), self.current_y)

if __name__ == "__main__":
    Boo()