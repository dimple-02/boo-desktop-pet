import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk
import random
from datetime import datetime
from speech import SpeechBubble
import ctypes

# Try to make Tkinter DPI aware for high resolution displays on Windows
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

WIDTH = 160
HEIGHT = 200
SNOOZE_INTERVAL = 10 * 60 * 1000 
PATROL_INTERVAL = 7000

class Boo:
    def __init__(self):
        self.root = tk.Tk()

        # Remove title bar and stay on top
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        # Transparency setup
        self.root.config(bg="white")
        self.root.wm_attributes("-transparentcolor", "white")

        # Screen boundary calculation
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()

        # Default bottom-right placement matching downscaled dimensions
        self.default_x = self.screen_w - WIDTH - 20
        self.default_y = self.screen_h - HEIGHT - 50
        
        self.root.geometry(f"{WIDTH}x{HEIGHT}+{self.default_x}+{self.default_y}")

        # Resolve asset locations cleanly
        BASE_DIR = Path(__file__).resolve().parent.parent
        images_dir = BASE_DIR / "assets" / "images"

        # Image Assets Pipelines (100x100)
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
        self.base_y = 90
        self.current_y = self.base_y
        self.label.place(x=30, y=self.base_y)

        # Core State Engine & Flags
        self.speech = SpeechBubble(self.root)
        self.is_water_reminder_active = False
        self.is_patrolling = False
        self.last_reminded_hour = -1
        self.snooze_job_id = None

        # Patrol tracking variables
        self.patrol_x = 0
        self.patrol_y = 0
        self.patrol_step = 0

        # Bindings Layout
        self.label.bind("<Button-1>", self.start_move)
        self.label.bind("<B1-Motion>", self.move)
        self.label.bind("<Double-Button-1>", self.say_hi)

        # Start Continuous Loops
        self.root.after(3000, self.blink)
        self.float_offset = 0
        self.float_direction = 1
        self.animate()
        
        # Start Time Watchers
        self.check_time_reminders()
        self.root.after(PATROL_INTERVAL, self.schedule_next_patrol)

        self.root.mainloop()

    def load_and_scale_image(self, path):
        img = Image.open(path)
        img = img.resize((100, 100), Image.LANCZOS)
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
        if not self.is_patrolling:
            self.float_offset += self.float_direction
            if self.float_offset >= 5:
                self.float_direction = -1
            elif self.float_offset <= -5:
                self.float_direction = 1

            self.current_y = self.base_y + self.float_offset
            self.label.place_configure(x=30, y=self.current_y)
        self.root.after(60, self.animate)

    # --- Windows Drag Framework ---
    def start_move(self, event):
        if self.is_patrolling: 
            return
        self.x = event.x
        self.y = event.y

    def move(self, event):
        if self.is_patrolling: 
            return
        x = self.root.winfo_x() + event.x - self.x
        y = self.root.winfo_y() + event.y - self.y
        self.root.geometry(f"+{x}+{y}")
        self.default_x = x
        self.default_y = y

    def say_hi(self, event=None):
        if self.is_water_reminder_active or self.is_patrolling:
            return
            
        messages = [
            "Hi! I'm Boo 👻", "Mini size, macro care! ✨", 
            "Don't forget water! 💧", "Floating around smoothly~"
        ]
        self.speech.show(random.choice(messages), self.current_y, is_reminder=False)

    # --- Real-Time Clock Reminder Engine ---
    def check_time_reminders(self):
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute

        if current_minute == 0 and current_hour != self.last_reminded_hour:
            self.last_reminded_hour = current_hour
            if self.snooze_job_id:
                self.root.after_cancel(self.snooze_job_id)
                self.snooze_job_id = None
                
            self.is_patrolling = False 
            self.trigger_water_reminder(f"Ding Dong! It's {current_hour if current_hour <= 12 else current_hour - 12} o'clock! Time to drink water! 💧")

        self.root.after(1000, self.check_time_reminders)

    # --- Patrol Automation Loop ---
    def schedule_next_patrol(self):
        if not self.is_water_reminder_active and not self.is_patrolling:
            self.start_screen_patrol()
        self.root.after(PATROL_INTERVAL, self.schedule_next_patrol)

    def start_screen_patrol(self):
        self.is_patrolling = True
        self.speech.hide()
        
        # Force flush current window mapping variables
        self.root.update_idletasks()
        
        self.label.place_configure(x=30, y=self.base_y)
        
        self.patrol_x = int(self.root.winfo_x())
        self.patrol_y = int(self.root.winfo_y())
        self.patrol_step = 0
        
        # Show patrol speech bubble
        self.speech.show("17-min patrol mark hit! Let's run! 🏃‍♂️💨", self.base_y, is_reminder=False)
        
        # Wait 1.5 seconds for the user to read the message, then hide it and start moving
        self.root.after(1500, self._start_movement_after_speech)

    def _start_movement_after_speech(self):
        if self.is_patrolling:
            self.speech.hide()
            self.update_patrol_movement()

    def update_patrol_movement(self):
        if not self.is_patrolling:
            return

        speed = 8

        if self.patrol_step == 0:  # Move Left
            self.patrol_x -= speed
            if self.patrol_x <= 10:
                self.patrol_x = 10
                self.patrol_step = 1
        
        elif self.patrol_step == 1:  # Move Up
            self.patrol_y -= speed
            if self.patrol_y <= 10:
                self.patrol_y = 10
                self.patrol_step = 2

        elif self.patrol_step == 2:  # Move Right
            self.patrol_x += speed
            max_right = self.screen_w - WIDTH - 10
            if self.patrol_x >= max_right:
                self.patrol_x = max_right
                self.patrol_step = 3

        elif self.patrol_step == 3:  # Move Down home
            self.patrol_y += speed
            if self.patrol_y >= self.default_y:
                self.patrol_y = self.default_y
                if self.patrol_x >= self.default_x:
                    self.patrol_x = self.default_x
                    self.is_patrolling = False
                    self.speech.hide()
                    self.speech.show("Done! Returning to default spot~ 😴", self.base_y, is_reminder=False)

        # Apply geometry configuration
        self.root.geometry(f"+{int(self.patrol_x)}+{int(self.patrol_y)}")
        
        # CRITICAL: Force window rendering cycle refresh instantly to prevent UI freezes on Windows OS
        self.root.update()
        
        if self.is_patrolling:
            self.root.after(16, self.update_patrol_movement)

    # --- Water Reminder Section ---
    def trigger_water_reminder(self, text_message):
        self.is_water_reminder_active = True
        self.label.config(image=self.water_photo)
        self.speech.show(
            text_message, 
            self.base_y, 
            is_reminder=True, 
            on_yes=self.handle_water_yes, 
            on_no=self.handle_water_no
        )

    def handle_water_yes(self):
        self.speech.hide()
        self.is_water_reminder_active = False
        self.label.config(image=self.idle_photo)
        if self.snooze_job_id:
            self.root.after_cancel(self.snooze_job_id)
            self.snooze_job_id = None
        self.speech.show("Awesome! Proud of you! ❤️✨", self.base_y, is_reminder=False)

    def handle_water_no(self):
        self.speech.hide()
        self.is_water_reminder_active = False
        self.label.config(image=self.idle_photo)
        
        if self.snooze_job_id:
            self.root.after_cancel(self.snooze_job_id)
            
        self.snooze_job_id = self.root.after(
            SNOOZE_INTERVAL, 
            lambda: self.trigger_water_reminder("Tumne bola tha baad mein piogi! Chalo ab piyo! 🥤👀")
        )

if __name__ == "__main__":
    Boo()