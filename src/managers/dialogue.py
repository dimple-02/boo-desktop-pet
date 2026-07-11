import json
import time
import random
from pathlib import Path
from datetime import datetime
from core.config import COOLDOWN_IDLE_SPEECH_SEC

class DialogueManager:
    def __init__(self, base_dir=None):
        if base_dir is None:
            self.base_dir = Path(__file__).resolve().parent.parent.parent
        else:
            self.base_dir = Path(base_dir)
            
        self.dialogues_dir = self.base_dir / "assets" / "dialogues"
        self.dialogues = self._load_dialogues()

        # Cooldown parameters
        self.idle_cooldown = COOLDOWN_IDLE_SPEECH_SEC
        self.last_speech_time = 0

    def _load_dialogues(self):
        """Loads all dialogue JSON files from the dialogues directory into a cached dictionary."""
        dialogues = {}
        if not self.dialogues_dir.exists():
            print(f"[DialogueManager] Dialogues directory not found at {self.dialogues_dir}")
            return dialogues
            
        for file_path in self.dialogues_dir.glob("*.json"):
            name = file_path.stem  # e.g., 'morning', 'winter', 'trust'
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    dialogues[name] = json.load(f)
            except Exception as e:
                print(f"[DialogueManager] Error parsing {file_path.name}: {e}")
        return dialogues

    def get_dialogue(self, relationship_status="Normal", force=False):
        """
        Gathers matching dialogues based on time, month, weekend, festivals,
        and relationship status, returning a randomly chosen dialogue.
        
        If force=False (spontaneous idle speech), checks the speech cooldown.
        If force=True (double click), overrides cooldown.
        """
        now = time.time()
        
        # Check cooldown for spontaneous ticks
        if not force:
            if now - self.last_speech_time < self.idle_cooldown:
                return None

        # Build combined pool of matching dialogues
        pool = []
        now_dt = datetime.now()
        month = now_dt.month
        day = now_dt.day
        hour = now_dt.hour
        weekday = now_dt.weekday()

        # Check relationship-based dialogue overrides first
        trust_dialogues = self.dialogues.get("trust", {})
        
        if relationship_status == "Lonely":
            # Neglected/Absent state recovery prompts
            pool.extend(trust_dialogues.get("lonely", []))
        elif relationship_status == "Distant":
            # Low Trust/Affection responses
            pool.extend(trust_dialogues.get("low_trust", []))
        else:
            # Normal or high relationship status: load standard context pools
            if relationship_status == "Happier":
                pool.extend(trust_dialogues.get("high_relationship", []))
                
            # 1. Festival Check
            festivals = self.dialogues.get("festivals", {})
            if month == 10 and 24 <= day <= 31:
                pool.extend(festivals.get("halloween", []))
            elif month == 12 and 18 <= day <= 25:
                pool.extend(festivals.get("christmas", []))
            elif (month == 12 and day == 31) or (month == 1 and day == 1):
                pool.extend(festivals.get("new_year", []))

            # 2. Season Check
            if month in [12, 1, 2]:
                pool.extend(self.dialogues.get("winter", []))
            elif month in [3, 4, 5]:
                pool.extend(self.dialogues.get("spring", []))
            elif month in [6, 7, 8]:
                pool.extend(self.dialogues.get("summer", []))
            elif month in [9, 10, 11]:
                pool.extend(self.dialogues.get("autumn", []))

            # 3. Weekend Check
            if weekday in [5, 6]:
                pool.extend(self.dialogues.get("weekend", []))

            # 4. Time of Day Check
            if 6 <= hour < 12:
                pool.extend(self.dialogues.get("morning", []))
            elif 12 <= hour < 17:
                pool.extend(self.dialogues.get("afternoon", []))
            elif 17 <= hour < 22:
                pool.extend(self.dialogues.get("evening", []))
            else:
                pool.extend(self.dialogues.get("night", []))

            # 5. General Fallback
            pool.extend(self.dialogues.get("idle", []))

        # Choose a random line
        selected = random.choice(pool) if pool else "Hiiiiii!! ✨"
        
        # Update last speech time
        self.last_speech_time = now
        return selected
