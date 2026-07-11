import time
from core.config import TRUST_MAX, AFFECTION_MAX, NEGLECT_THRESHOLD_SEC, SLOW_RECOVERY_DURATION_SEC, DAMPING_FACTOR

class StatsManager:
    def __init__(self, persistence_manager):
        self.persistence = persistence_manager

        # Default hidden stats
        self.trust = 50.0
        self.affection = 50.0
        self.last_seen = time.time()

        # Recovery states
        self.in_recovery_mode = False
        self.recovery_start_time = 0.0

        # Load values from persistence
        self.load_stats()
        
        # Check neglect on boot
        self.check_neglect_on_boot()

    def check_neglect_on_boot(self):
        """Checks if Boo was neglected based on elapsed time since last seen."""
        now = time.time()
        elapsed = now - self.last_seen

        if elapsed >= NEGLECT_THRESHOLD_SEC:
            # Apply neglect penalties
            self.trust = max(0.0, self.trust - 10.0)
            self.affection = max(0.0, self.affection - 10.0)
            
            # Trigger slow recovery mode
            self.in_recovery_mode = True
            self.recovery_start_time = now
            print(f"[StatsManager] Neglect detected. Boo was gone for {elapsed/3600:.1f} hours. Entering recovery mode.")
        else:
            print(f"[StatsManager] Welcome back! Boo was last seen {elapsed/60:.1f} minutes ago.")
            
        # Update last seen to now
        self.last_seen = now
        self.save_stats()

    def update_recovery_status(self):
        """Checks if the recovery mode duration has finished and resets it."""
        if self.in_recovery_mode:
            now = time.time()
            if now - self.recovery_start_time >= SLOW_RECOVERY_DURATION_SEC:
                self.in_recovery_mode = False
                print("[StatsManager] Slow emotional recovery finished. Boo is back to normal.")

    def _add_stat(self, affection_gain=0.0, trust_gain=0.0):
        """Helper to increment stats, applying dampening if in recovery mode."""
        self.update_recovery_status()
        
        factor = DAMPING_FACTOR if self.in_recovery_mode else 1.0
        
        if affection_gain > 0:
            self.affection = min(AFFECTION_MAX, self.affection + (affection_gain * factor))
        if trust_gain > 0:
            self.trust = min(TRUST_MAX, self.trust + (trust_gain * factor))

        self.last_seen = time.time()
        self.save_stats()

    def record_pat(self):
        """Adds affection for petting (double click)."""
        self._add_stat(affection_gain=1.0)

    def record_drag(self):
        """Adds affection for gentle dragging."""
        self._add_stat(affection_gain=1.0)

    def record_answer_question(self):
        """Adds trust for answering curiosity questions."""
        self._add_stat(trust_gain=3.0)

    def record_complete_reminder(self):
        """Adds trust and affection for completing self-care reminders."""
        self._add_stat(affection_gain=2.0, trust_gain=5.0)

    def record_ignore_reminder(self):
        """Deducts trust for ignoring reminders."""
        self.trust = max(0.0, self.trust - 3.0)
        self.last_seen = time.time()
        self.save_stats()

    def get_relationship_status(self):
        """
        Returns a descriptive status label of Boo's relationship with the user.
        Emotion > Statistics.
        """
        self.update_recovery_status()
        if self.in_recovery_mode:
            return "Lonely"
        elif self.affection < 30.0 and self.trust < 30.0:
            return "Distant"
        elif self.affection > 70.0 or self.trust > 70.0:
            return "Happier"
        else:
            return "Normal"

    def load_stats(self):
        """Loads trust, affection, and last_seen values from save.json."""
        data = self.persistence.load_save_data()
        self.trust = data.get("trust", 50.0)
        self.affection = data.get("affection", 50.0)
        self.last_seen = data.get("last_seen", time.time())

    def save_stats(self):
        """Writes trust, affection, and last_seen values to save.json."""
        self.persistence.save_save_data({
            "trust": self.trust,
            "affection": self.affection,
            "last_seen": self.last_seen
        })
