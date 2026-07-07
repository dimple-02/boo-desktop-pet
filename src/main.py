import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk
from speech import SpeechBubble
WIDTH = 180
HEIGHT = 180


class Boo:

    def __init__(self):

        self.root = tk.Tk()

        # Remove title bar
        self.root.overrideredirect(True)

        # Always on top
        self.root.attributes("-topmost", True)

        # Transparent background
        self.root.config(bg="white")
        self.root.wm_attributes("-transparentcolor", "white")

        # Bottom-right position
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = screen_width - WIDTH - 20
        y = screen_height - HEIGHT - 70

        self.root.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")

        # ---------------------------
        # Load Boo image
        # ---------------------------

        BASE_DIR = Path(__file__).resolve().parent.parent

        image_path = BASE_DIR / "assets" / "images" / "boo_idle.png"

        image = Image.open(image_path)
        image = image.resize((140, 140))

        self.photo = ImageTk.PhotoImage(image)

        self.label = tk.Label(
            self.root,
            image=self.photo,
            bg="white",
            borderwidth=0,
            highlightthickness=0
        )

        self.label.pack(expand=True)
        self.speech = SpeechBubble(self.root)
        self.label.bind("<Double-Button-1>", self.say_hi)
        # Enable dragging
        self.make_draggable()

        self.root.mainloop()

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

    def say_hi(self, event=None):
        self.speech.show("Hi! I'm Boo 👻")
if __name__ == "__main__":
    Boo()