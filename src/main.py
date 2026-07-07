import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk
import random
import os
import math
from datetime import datetime
from speech import SpeechBubble

WIDTH = 160
HEIGHT = 200
SNOOZE_INTERVAL = 10 * 60 * 1000 
PATROL_INTERVAL = 17 * 60 * 1000 

class Boo:
    def __init__(self):
        self.root = tk.Tk()

        # Remove title bar and stay on top
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        # Transparent framework engine setup pipelines
        self.root.config(bg="white")
        self.root.wm_attributes("-transparentcolor", "white")

        # Screen boundary calculation layout
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()

        # Default bottom-right safe target placement
        self.default_x = self.screen_w - WIDTH - 20
        self.default_y = self.screen_h - HEIGHT - 50
        
        self.root.geometry(f"{WIDTH}x{HEIGHT}+{self.default_x}+{self.default_y}")

        # Resolve asset locations cleanly
        BASE_DIR = Path(__file__).resolve().parent.parent
        images_dir = BASE_DIR / "assets" / "images"
        self.save_file_path = BASE_DIR / "friendship.txt"

        # --- Base Level State Parameters Engine System Framework ---
        self.level = 1
        self.xp = 0
        self.is_water_reminder_active = False
        self.is_patrolling = False
        self.is_spinning = False
        self.last_reminded_hour = -1
        self.snooze_job_id = None
        self.spin_angle = 0
        self.rotated_photo = None
        self.patrol_x = 0
        self.patrol_y = 0
        self.patrol_step = 0

        # Load Save State System Data Modules
        self.load_friendship_data()

        # Cache base images for rotation handling before conversion to PhotoImage
        self.raw_idle_img = Image.open(images_dir / "boo_idle.png").resize((100, 100), Image.LANCZOS)

        # Base Costumes Asset Pipelines
        self.idle_photo = ImageTk.PhotoImage(self.raw_idle_img)
        self.blink_photo = self.load_and_scale_image(images_dir / "boo_blink.png", (100, 100))
        self.water_photo = self.load_and_scale_image(images_dir / "boo_water.png", (100, 100))
        self.water_blink_photo = self.load_and_scale_image(images_dir / "boo_water_blink.png", (100, 100))

        # Level 2+ Advanced Outfits Pipelines
        self.pink_photo = self.load_with_fallback(images_dir / "boo_pink.png", self.idle_photo)
        self.blue_photo = self.load_with_fallback(images_dir / "boo_blue.png", self.idle_photo)
        self.purple_photo = self.load_with_fallback(images_dir / "boo_purple.png", self.idle_photo)
        self.halloween_photo = self.load_with_fallback(images_dir / "boo_halloween.png", self.idle_photo)
        self.christmas_photo = self.load_with_fallback(images_dir / "boo_christmas.png", self.idle_photo)

        # UI Core Presentation Base Layer
        self.label = tk.Label(
            self.root,
            image=self.get_active_texture("idle"),
            bg="white",
            borderwidth=0,
            highlightthickness=0
        )
        self.base_y = 90
        self.current_y = self.base_y
        self.label.place(x=30, y=self.base_y)

        # Core State Components & Triggers
        self.speech = SpeechBubble(self.root)

        # Bindings Layout
        self.label.bind("<Button-1>", self.start_move)
        self.label.bind("<B1-Motion>", self.move)
        self.label.bind("<Double-Button-1>", self.say_hi)
        self.label.bind("<Triple-Button-1>", self.start_spin_gesture)

        # Start continuous core runtime animation timelines
        self.root.after(3000, self.blink)
        self.float_offset = 0
        self.float_direction = 1
        self.animate()
        
        # Start Time Monitors
        self.check_time_reminders()
        self.root.after(PATROL_INTERVAL, self.schedule_next_patrol)

        self.root.mainloop()

    # --- Save State Progression File Control ---
    def load_friendship_data(self):
        if os.path.exists(self.save_file_path):
            try:
                with open(self.save_file_path, "r") as f:
                    lines = f.readlines()
                    for line in lines:
                        if "level:" in line:
                            self.level = int(line.split(":")[1].strip())
                        elif "xp:" in line:
                            self.xp = int(line.split(":")[1].strip())
            except:
                self.level = 1
                self.xp = 0
        else:
            self.save_friendship_data()

    def save_friendship_data(self):
        try:
            with open(self.save_file_path, "w") as f:
                f.write(f"level: {self.level}\n")
                f.write(f"xp: {self.xp}\n")
        except Exception as e:
            print(f"Error saving progression state: {e}")

    def add_xp(self, amount):
        self.xp += amount
        xp_needed = 100
        
        if self.xp >= xp_needed:
            self.xp -= xp_needed
            self.level += 1
            self.save_friendship_data()
            
            unlock_msg = "Accessory Unlocked! 🎩"
            if self.level == 2: unlock_msg = "Unlocked: Pink & Blue Outfits! 🌸"
            elif self.level == 3: unlock_msg = "Unlocked: Halloween Skin! 🎃"
            
            self.root.after(1200, lambda: self.speech.show(
                f"🎉 LEVEL UP! 🎉\nWe are Level {self.level} now! ❤️\n{unlock_msg}", 
                self.base_y, 
                is_reminder=False
            ))
            self.label.config(image=self.get_active_texture("idle"))
        else:
            self.save_friendship_data()

    def load_and_scale_image(self, path, size):
        if not os.path.exists(path):
            img = Image.new("RGBA", size, (255, 255, 255, 0))
            return ImageTk.PhotoImage(img)
        img = Image.open(path)
        img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)

    def load_with_fallback(self, path, fallback_photo):
        if os.path.exists(path):
            return self.load_and_scale_image(path, (100, 100))
        return fallback_photo

    def get_active_texture(self, state_type):
        if self.is_water_reminder_active:
            return self.water_blink_photo if state_type == "blink" else self.water_photo
            
        if self.level == 2:
            return self.pink_photo if state_type == "idle" else self.blink_photo
        elif self.level == 3:
            return self.halloween_photo if state_type == "idle" else self.blink_photo
        elif self.level >= 4:
            return self.christmas_photo if state_type == "idle" else self.blink_photo

        return self.blink_photo if state_type == "blink" else self.idle_photo

    # --- v1.4 Interactive Spin Gesture Engine ---
    def start_spin_gesture(self, event=None):
        if self.is_spinning or self.is_patrolling:
            return
        self.is_spinning = True
        self.spin_angle = 0
        self.speech.hide()
        self.speech.show("Wuuuhuu! Spinning! 😂🌀", self.base_y, is_reminder=False)
        self.update_spin_loop()

    def update_spin_loop(self):
        if not self.is_spinning:
            return

        self.spin_angle += 15  
        if self.spin_angle >= 360:
            self.is_spinning = False
            self.label.config(image=self.get_active_texture("idle"))
            return

        rotated_img = self.raw_idle_img.rotate(-self.spin_angle, resample=Image.BICUBIC)
        self.rotated_photo = ImageTk.PhotoImage(rotated_img)
        self.label.config(image=self.rotated_photo)

        self.root.after(20, self.update_spin_loop)

    # --- Anim Control Engines Loops ---
    def blink(self):
        if not self.is_spinning:
            self.label.config(image=self.get_active_texture("blink"))
        self.root.after(180, self.open_eyes)

    def open_eyes(self):
        if not self.is_spinning:
            self.label.config(image=self.get_active_texture("idle"))
        next_blink = random.randint(4000, 8000)
        self.root.after(next_blink, self.blink)

    def animate(self):
        if not self.is_patrolling and not self.is_spinning:
            self.float_offset += self.float_direction
            if self.float_offset >= 5:
                self.float_direction = -1
            elif self.float_offset <= -5:
                self.float_direction = 1

            self.current_y = self.base_y + self.float_offset
            self.label.place_configure(x=30, y=self.current_y)
        self.root.after(60, self.animate)

    # --- Windows Drag Interaction Framework ---
    def start_move(self, event):
        if self.is_patrolling or self.is_spinning: 
            return
        self.x = event.x
        self.y = event.y

    def move(self, event):
        if self.is_patrolling or self.is_spinning: 
            return
        x = self.root.winfo_x() + event.x - self.x
        y = self.root.winfo_y() + event.y - self.y
        self.root.geometry(f"+{x}+{y}")
        self.default_x = x
        self.default_y = y

    def say_hi(self, event=None):
        if self.is_water_reminder_active or self.is_patrolling or self.is_spinning:
            return
            
        self.add_xp(2)
        outfit_hint = "Let's level up for cool outfits! 🚀"
        if self.level >= 2: outfit_hint = f"Rocking Level {self.level} styles! 😎"
        
        messages = [
            f"Hiiiiii!! ✨", 
            f"Dosti XP: {self.xp}/100 ⭐", 
            outfit_hint, 
            "Try triple-clicking me! 😉"
        ]
        self.speech.show(random.choice(messages), self.current_y, is_reminder=False)

    # --- Real-Time Clock Notifications Subsystem ---
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
            self.is_spinning = False
            self.trigger_water_reminder(f"Ding Dong! It's {current_hour if current_hour <= 12 else current_hour - 12} o'clock! Drink water! 💧")

        self.root.after(1000, self.check_time_reminders)

    # --- Patrol Tracking Modules ---
    def schedule_next_patrol(self):
        if not self.is_water_reminder_active and not self.is_patrolling:
            self.start_screen_patrol()
        self.root.after(PATROL_INTERVAL, self.schedule_next_patrol)

    def start_screen_patrol(self):
        if self.is_spinning:
            return
        self.is_patrolling = True
        self.speech.hide()
        
        self.root.update_idletasks()
        self.label.place_configure(x=30, y=self.base_y)
        
        self.patrol_x = int(self.root.winfo_x())
        self.patrol_y = int(self.root.winfo_y())
        self.patrol_step = 0
        
        self.speech.show("Patrol time! Let's walk! 🏃‍♂️💨", self.base_y, is_reminder=False)
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
                    self.speech.show("Done! Spot restored~ 😴", self.base_y, is_reminder=False)

        self.root.geometry(f"+{int(self.patrol_x)}+{int(self.patrol_y)}")
        self.root.update()
        
        if self.is_patrolling:
            self.root.after(16, self.update_patrol_movement)

    # --- Water Reminder Section ---
    def trigger_water_reminder(self, text_message):
        self.is_water_reminder_active = True
        self.label.config(image=self.get_active_texture("water"))
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
        self.label.config(image=self.get_active_texture("idle"))
        if self.snooze_job_id:
            self.root.after_cancel(self.snooze_job_id)
            self.snooze_job_id = None
            
        self.add_xp(20)
        self.speech.show(f"Awesome! +20 XP gained! ❤️✨", self.base_y, is_reminder=False)

    def handle_water_no(self):
        self.speech.hide()
        self.is_water_reminder_active = False
        self.label.config(image=self.get_active_texture("idle"))
        
        if self.snooze_job_id:
            self.root.after_cancel(self.snooze_job_id)
            
        self.snooze_job_id = self.root.after(
            SNOOZE_INTERVAL, 
            lambda: self.trigger_water_reminder("Tumne bola tha baad mein piogi! Chalo ab piyo! 🥤👀")
        )

if __name__ == "__main__":
    Boo()