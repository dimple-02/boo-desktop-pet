from assistant.commands.base import BaseCommand

class HelpCommand(BaseCommand):
    def execute(self, args):
        """Returns a list of all commands Boo supports."""
        return (
            "Here is what I can do: 💜\n"
            "- 'follow': I'll chase your cursor\n"
            "- 'stop': Return to float\n"
            "- 'find <name>': Search files\n"
            "- Or ask me anything!"
        )
