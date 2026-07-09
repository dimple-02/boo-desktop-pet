class BaseCommand:
    def __init__(self, app):
        """
        Base command interface.
        :param app: Reference to the BooApp instance to orchestrate window/state adjustments.
        """
        self.app = app

    def execute(self, args):
        """
        Executes the command and returns a string response for Boo to speak.
        :param args: List of string arguments passed to the command.
        """
        raise NotImplementedError("Command subclass must implement execute().")
