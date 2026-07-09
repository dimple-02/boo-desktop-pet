from assistant.commands.base import BaseCommand

class FollowCommand(BaseCommand):
    def execute(self, args):
        """Triggers Boo's activity state to cursor chasing."""
        self.app.state_manager.set_activity("Walking")
        self.app.start_follow_cursor()
        return "Okay! I am following your cursor! 👻✨"
