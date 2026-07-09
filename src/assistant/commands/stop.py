from assistant.commands.base import BaseCommand

class StopCommand(BaseCommand):
    def execute(self, args):
        """Stops cursor chasing and returns Boo to float physics."""
        self.app.state_manager.set_activity("Idle")
        self.app.stop_follow_cursor()
        return "Stopped! Back to floating around. 😴"
