import random
from assistant.parser import CommandParser
from assistant.commands.follow import FollowCommand
from assistant.commands.stop import StopCommand
from assistant.commands.search import SearchCommand
from assistant.commands.help import HelpCommand

class Assistant:
    def __init__(self, app):
        self.app = app
        self.parser = CommandParser()

        # Command Pattern Registry
        self.commands = {
            "help": HelpCommand(app),
            "follow": FollowCommand(app),
            "stop": StopCommand(app),
            "search": SearchCommand(app)
        }

    def process_input(self, text):
        """
        Receives user text input, parses it for commands or processes it as a chat dialog,
        and returns a string response for Boo to say.
        """
        # Log conversation metrics in memory
        self.app.memory_manager.record_conversation()

        # Parse text for command matches
        cmd_name, args = self.parser.parse(text)

        if cmd_name in self.commands:
            try:
                return self.commands[cmd_name].execute(args)
            except Exception as e:
                print(f"[Assistant] Error executing command {cmd_name}: {e}")
                return "Something went wrong when I tried to run that command! 🥺"

        # If not a command, process as conversational chat (fact saving/retrieval)
        return self._process_chat(text)

    def _process_chat(self, text):
        clean_text = text.lower().strip()

        # 1. Fact Saving: "my name is [X]"
        if "my name is " in clean_text:
            idx = clean_text.find("my name is ") + len("my name is ")
            name = text[idx:].strip()
            if name:
                self.app.memory_manager.save_fact("user_name", name)
                return f"Nice to meet you, {name}! I will remember that. 💜"

        # 2. Fact Saving: "my favorite color is [Y]"
        if "my favorite color is " in clean_text:
            idx = clean_text.find("my favorite color is ") + len("my favorite color is ")
            color = text[idx:].strip()
            if color:
                self.app.memory_manager.save_fact("favorite_color", color)
                return f"I love {color} too! I'll remember it's your favorite. 🎨"

        # 3. Fact Retrieval: "what is my name"
        if "what is my name" in clean_text:
            name = self.app.memory_manager.get_fact("user_name")
            if name:
                return f"Your name is {name}! I haven't forgotten. 😉"
            return "You haven't told me your name yet! What should I call you?"

        # 4. Fact Retrieval: "what is my favorite color"
        if "what is my favorite color" in clean_text:
            color = self.app.memory_manager.get_fact("favorite_color")
            if color:
                return f"Your favorite color is {color}! 🎨"
            return "You haven't told me your favorite color yet! What is it?"

        # 5. Conversational Fallbacks
        responses = [
            "I'm listening! 👻",
            "Tell me more, buddy.",
            "I like chatting with you! 💜",
            "You are doing great! Let's keep focusing.",
            "Try asking me to 'follow' or 'find main.py'!"
        ]
        return random.choice(responses)
