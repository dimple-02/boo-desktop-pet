import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk
import random
from datetime import datetime
from speech import SpeechBubble

WIDTH = 200
HEIGHT = 240

# For testing: 10 minutes snooze can be dropped to 15000ms (15 sec). Production value: 10 * 60 * 1000
SNOOZE_INTERVAL = 10 * 60 * 1000
class Boo:
    def __init__(self):
        self.root = tk.Tk()

        # Remove title bar and stay on top
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        # Transparency setup
        self.root.config(bg="white")
        self.root.wm_attributes("-transparentcolor", "white")

        # Position bottom-right screen layout
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - WIDTH - 20
        y = screen_height - HEIGHT - 60
        self.root.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")

        # Resolve asset locations cleanly
        BASE_DIR = Path(__file__).resolve().parent.parent
        images_dir = BASE_DIR / "assets" / "images"

        # Image Assets Pipelines
        self.idle_photo = self.load_and_scale_image(images_dir / "boo_idle.png")
        self.blink_photo = self.load_and_scale_image(images_dir / "boo_blink.png")
        self.water_photo = self.load_and_scale_image(images_dir / "boo_water.png")
        self.water_blink_photo = self.load_and_scale_image(images_dir / "boo_water_blink.png")

        # UI Core Presentation Label
        self.label = tk.Label(
            self.root,
            image=self.idle_photo,
            bg="white",
            borderwidth=0,
            highlightthickness=0
        )
        self.base_y = 95
        self.current_y = self.base_y
        self.label.place(x=30, y=self.base_y)

        # Core Components & Flags Engine
        self.speech = SpeechBubble(self.root)
        self.is_water_reminder_active = False
        self.last_reminded_hour = -1
        self.snooze_job_id = None

        # Bindings Layout
        self.label.bind("<Double-Button-1>", self.say_hi)
        self.make_draggable()

        # Start Continuous Loops
        self.root.after(3000, self.blink)
        self.float_offset = 0
        self.float_direction = 1
        self.animate()
        
        # Start Real-Time Watcher Tracker loop
        self.check_time_reminders()

        self.root.mainloop()

    def load_and_scale_image(self, path):
        img = Image.open(path)
        img = img.resize((140, 140), Image.LANCZOS)
        return ImageTk.PhotoImage(img)

    # --- Anim Loops Engines ---
    def blink(self):
        if self.is_water_reminder_active:
            self.label.config(image=self.water_blink_photo)
        else:
            self.label.config(image=self.blink_photo)
        self.root.after(180, self.open_eyes)

    def open_eyes(self):
        if self.is_water_reminder_active:
            self.label.config(image=self.water_photo)
        else:
            self.label.config(image=self.idle_photo)
        next_blink = random.randint(4000, 8000)
        self.root.after(next_blink, self.blink)

    def animate(self):
        self.float_offset += self.float_direction
        if self.float_offset >= 6:
            self.float_direction = -1
        elif self.float_offset <= -6:
            self.float_direction = 1

        self.current_y = self.base_y + self.float_offset
        self.label.place_configure(x=30, y=self.current_y)
        self.root.after(60, self.animate)

    # --- Windows Drag Framework ---
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
        if self.is_water_reminder_active:
            return  # Locked interaction when serving reminders
            
        messages = [
            "Hi! I'm Boo 👻", "You're doing amazing! 🌸", 
            "Don't forget water! 💧", "I'm cheering for you! ⭐"
        ]
        self.speech.show(random.choice(messages), self.current_y, is_reminder=False)

    # --- Real-Time Notifications Core Layout ---
    def check_time_reminders(self):
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute

        # Trigger on top of the hour marks cleanly
        if current_minute == 0 and current_hour != self.last_reminded_hour:
            self.last_reminded_hour = current_hour
            
            # Cancel any running 10-min background snoozes since hourly takes precedence
            if self.snooze_job_id:
                self.root.after_cancel(self.snooze_job_id)
                self.snooze_job_id = None
                
            self.trigger_water_reminder(f"Ding Dong! It's {current_hour if current_hour <= 12 else current_hour - 12} o'clock! Time to drink water! 💧")

        self.root.after(1000, self.check_time_reminders)

    def trigger_water_reminder(self, text_message):
        """Forces Boo into ziddi hydration frame state until explicit user interaction."""
        self.is_water_reminder_active = True
        self.label.config(image=self.water_photo)
        self.speech.show(
            text_message, 
            self.current_y, 
            is_reminder=True, 
            on_yes=self.handle_water_yes, 
            on_no=self.handle_water_no
        )

    def handle_water_yes(self):
        """User drank water! Safe teardown and return to normal."""
        self.speech.hide()
        self.is_water_reminder_active = False
        self.label.config(image=self.idle_photo)
        if self.snooze_job_id:
            self.root.after_cancel(self.snooze_job_id)
            self.snooze_job_id = None
        
        # Visual quick reward feedback message
        self.speech.show("Awesome! Proud of you! ❤️✨", self.current_y, is_reminder=False)

    def handle_water_no(self):
        """User rejected. Go idle but drop a delayed loop trap for 10 minutes later."""
        self.speech.hide()
        self.is_water_reminder_active = False
        self.label.config(image=self.idle_photo)
        
        if self.snooze_job_id:
            self.root.after_cancel(self.snooze_job_id)
            
        # Schedule the persistent nagging reminder
        self.snooze_job_id = self.root.after(
            SNOOZE_INTERVAL, 
            lambda: self.trigger_water_reminder("Tumne bola tha baad mein piogi! Chalo ab piyo! 🥤👀")
        )

if __name__ == "__main__":
    Boo()