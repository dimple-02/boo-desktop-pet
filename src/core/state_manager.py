class StateManager:
    def __init__(self):
        # Orthogonal states for Boo
        self.mood = "Neutral"       # e.g., Neutral, Happy, Sad, Lonely, Excited, Sleepy
        self.activity = "Idle"      # e.g., Idle, Walking, Reminder, Celebrating, Sleeping
        self.animation = "Idle"     # e.g., Idle, Blink, Yawn, Tilt, Bounce, LookLeft, LookRight

    def set_animation(self, anim_state):
        """Updates the active animation state."""
        self.animation = anim_state

    def set_activity(self, activity_state):
        """Updates the active activity state."""
        self.activity = activity_state

    def set_mood(self, mood_state):
        """Updates the active mood state."""
        self.mood = mood_state

    def get_texture_name(self):
        """
        Returns the appropriate base texture file name based on the current state.
        For v0.4, this maps to idle.png or blink.png.
        """
        if self.animation == "Blink":
            return "blink.png"
        return "idle.png"
