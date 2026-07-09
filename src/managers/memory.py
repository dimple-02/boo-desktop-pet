import time
from datetime import datetime

class MemoryManager:
    def __init__(self, persistence_manager):
        self.persistence = persistence_manager
        self.facts = {}
        self.stats = {}
        self.load_memory()

    def load_memory(self):
        """Loads facts and statistics from save.json."""
        data = self.persistence.load_save_data()
        
        # Load user facts
        self.facts = data.get("facts", {})
        
        # Load evolution statistics
        self.stats = data.get("stats", {
            "first_launch_date": datetime.now().isoformat(),
            "longest_streak": 0,
            "last_conversation_time": 0.0,
            "times_petted": 0,
            "questions_answered": 0
        })

    def save_memory(self):
        """Writes current facts and statistics back to save.json."""
        self.persistence.save_save_data({
            "facts": self.facts,
            "stats": self.stats
        })

    def save_fact(self, key, value):
        """Saves a user fact (e.g., 'favorite_color': 'blue')."""
        self.facts[key] = value
        self.save_memory()

    def get_fact(self, key, default=None):
        """Retrieves a user fact by key."""
        return self.facts.get(key, default)

    def record_pet(self):
        """Increments the number of times Boo has been petted."""
        self.stats["times_petted"] = self.stats.get("times_petted", 0) + 1
        self.save_memory()

    def record_question_answered(self):
        """Increments the count of questions answered by the user."""
        self.stats["questions_answered"] = self.stats.get("questions_answered", 0) + 1
        self.save_memory()

    def record_conversation(self):
        """Updates the timestamp of the last conversation."""
        self.stats["last_conversation_time"] = time.time()
        self.save_memory()

    def get_first_launch_date(self):
        """Returns the first launch date as a datetime object."""
        date_str = self.stats.get("first_launch_date")
        try:
            return datetime.fromisoformat(date_str)
        except Exception:
            return datetime.now()
