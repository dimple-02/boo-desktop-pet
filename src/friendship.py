import json
import os
from pathlib import Path

class FriendshipManager:
    def __init__(self):
        """Manages player data persistence, levels tracking, and reward unlocking mechanics."""
        BASE_DIR = Path(__file__).resolve().parent.parent
        self.save_path = BASE_DIR / "data" / "save.json"
        
        # Ensure data folder hierarchy exists seamlessly at production runtime
        self.save_path.parent.mkdir(parents=True, exist_ok=True)

        # Production Baseline Fallback Properties
        self.xp = 0
        self.level_id = 1
        self.unlocked_accessories = ["None"]
        self.window_x = None
        self.window_y = None

        # Absolute Mapping Matrix for Friendship Level Milestones
        self.LEVELS_MAP = {
            1: "Stranger",
            2: "Friend",
            3: "Best Friend",
            4: "Soul Buddy",
            5: "Family"
        }
        
        # Load profile configurations instantly upon module initialization
        self.load_data()

    def get_level_title(self):
        """Resolves active string representation token for the current numeric milestone level."""
        return self.LEVELS_MAP.get(self.level_id, "Family")

    def add_xp(self, amount):
        """Applies XP rewards delta matrix, monitors level boundaries and forces sync locks down to disk."""
        self.xp += amount
        xp_threshold = 100
        leveled_up = False

        if self.xp >= xp_threshold:
            if self.level_id < 5:
                self.xp -= xp_threshold
                self.level_id += 1
                leveled_up = True
                self.unlock_rewards_for_current_level()
            else:
                # Cap progress securely once max limit tier is targeted
                self.xp = xp_threshold

        self.save_data()
        return leveled_up

    def deduct_xp(self, amount):
        """Enforces negative penalties loop cleanly without dropping below absolute structural zero bounds."""
        self.xp = max(0, self.xp - amount)
        self.save_data()

    def unlock_rewards_for_current_level(self):
        """Appends accessory unlocks strings into the database based on progression tier jumps."""
        rewards = {
            2: "Wizard Hat",
            3: "Sprout",
            4: "Glasses",
            5: "Crown"
        }
        reward = rewards.get(self.level_id)
        if reward and reward not in self.unlocked_accessories:
            self.unlocked_accessories.append(reward)

    def update_position(self, x, y):
        """Safely caches recent geometric screen positioning matrices inside persistence layout states."""
        self.window_x = x
        self.window_y = y
        self.save_data()

    def load_data(self):
        """Performs raw JSON IO reads and safe fallbacks parsing runtime state frames data blocks."""
        if os.path.exists(self.save_path):
            try:
                with open(self.save_path, "r") as f:
                    data = json.load(f)
                    self.xp = data.get("friendship_xp", 0)
                    self.level_id = data.get("level_id", 1)
                    self.unlocked_accessories = data.get("unlocked_accessories", ["None"])
                    self.window_x = data.get("window_x", None)
                    self.window_y = data.get("window_y", None)
            except Exception as e:
                print(f"[Core Save Engine Error] Reading state profiles corrupted: {e}")
                self.save_data() # Enforce schema generation override instantly
        else:
            self.save_data()

    def save_data(self):
        """Safely write current runtime configuration dictionary parameters into database JSON stream logs."""
        try:
            payload = {
                "friendship_xp": self.xp,
                "level_id": self.level_id,
                "unlocked_accessories": self.unlocked_accessories,
                "window_x": self.window_x,
                "window_y": self.window_y
            }
            with open(self.save_path, "w") as f:
                json.dump(payload, f, indent=4)
        except Exception as e:
            print(f"[Core Save Engine Error] Writing pipeline broken down: {e}")