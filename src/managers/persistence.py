import json
import os
from pathlib import Path

class PersistenceManager:
    def __init__(self, base_dir=None):
        # Resolve root directory
        if base_dir is None:
            self.base_dir = Path(__file__).resolve().parent.parent.parent
        else:
            self.base_dir = Path(base_dir)
            
        self.data_dir = self.base_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.save_path = self.data_dir / "save.json"
        self.settings_path = self.data_dir / "settings.json"

    def load_save_data(self):
        """Loads state progression and coordinates from save.json."""
        if not self.save_path.exists():
            return {}
        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[PersistenceManager] Error loading save data: {e}")
            return {}

    def save_save_data(self, data):
        """Saves state progression and coordinates to save.json."""
        try:
            existing = self.load_save_data()
            existing.update(data)
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=4)
        except Exception as e:
            print(f"[PersistenceManager] Error saving save data: {e}")

    def load_settings(self):
        """Loads settings from settings.json."""
        if not self.settings_path.exists():
            return {}
        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[PersistenceManager] Error loading settings: {e}")
            return {}

    def save_settings(self, settings):
        """Saves settings configuration to settings.json."""
        try:
            existing = self.load_settings()
            existing.update(settings)
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=4)
        except Exception as e:
            print(f"[PersistenceManager] Error saving settings: {e}")
