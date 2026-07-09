import random
from datetime import datetime
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

        # --- 1. FACT SAVING ---
        # "my name is [X]"
        if "my name is " in clean_text:
            idx = clean_text.find("my name is ") + len("my name is ")
            name = text[idx:].strip()
            if name:
                self.app.memory_manager.save_fact("user_name", name)
                return f"Nice to meet you, {name}! I will remember that. 💜"

        # "my favorite color is [Y]"
        if "my favorite color is " in clean_text:
            idx = clean_text.find("my favorite color is ") + len("my favorite color is ")
            color = text[idx:].strip()
            if color:
                self.app.memory_manager.save_fact("favorite_color", color)
                return f"I love {color} too! I'll remember it's your favorite. 🎨"

        # "my birthday is [Z]"
        if "my birthday is " in clean_text:
            idx = clean_text.find("my birthday is ") + len("my birthday is ")
            bday = text[idx:].strip()
            if bday:
                self.app.memory_manager.save_fact("birthday", bday)
                return f"Got it! I will remember your birthday is {bday}. 🎂"

        # --- 2. FACT RETRIEVAL ---
        # "what is my name"
        if "what is my name" in clean_text or "do you know my name" in clean_text:
            name = self.app.memory_manager.get_fact("user_name")
            if name:
                return f"Your name is {name}! I haven't forgotten. 😉"
            return "You haven't told me your name yet! What should I call you?"

        # "what is my favorite color"
        if "what is my favorite color" in clean_text:
            color = self.app.memory_manager.get_fact("favorite_color")
            if color:
                return f"Your favorite color is {color}! 🎨"
            return "You haven't told me your favorite color yet! What is it?"

        # "when is my birthday" / "what is my birthday"
        if "when is my birthday" in clean_text or "what is my birthday" in clean_text:
            bday = self.app.memory_manager.get_fact("birthday")
            if bday:
                return f"Your birthday is on {bday}! I have it marked down. 🎂"
            return "You haven't told me your birthday yet! When is it?"

        # --- 3. EVOLUTION STATISTICS & MEMORY LOOKUPS ---
        # Time Together (How long have we known each other?)
        if any(q in clean_text for q in ("how long have we known", "how long have we been together", "how many days have we been together", "when did we meet", "time we spent together")):
            first_launch = self.app.memory_manager.get_first_launch_date()
            elapsed = datetime.now() - first_launch
            days = elapsed.days
            if days <= 0:
                return "We just met today! But I already feel super close to you. 👻💜"
            elif days == 1:
                return "We have been together for 1 day already! 😭😭"
            else:
                return f"We have been together for {days} days already! 😭💜 Time flies!"

        # Pet Counts
        if any(q in clean_text for q in ("how many times did i pet you", "how many times have i petted you", "how many pets", "times petted")):
            pets = self.app.memory_manager.stats.get("times_petted", 0)
            if pets <= 0:
                return "You haven't petted me yet! Double-click me to pat my head. 🥺"
            elif pets < 10:
                return f"You've petted me {pets} times. Thank you, it feels so good! 🥰"
            else:
                return f"You've petted me {pets} times! My head is so soft now. 💜"

        # Longest Streak
        if any(q in clean_text for q in ("longest streak", "longest focus streak", "my streak")):
            streak = self.app.memory_manager.stats.get("longest_streak", 0)
            if streak <= 0:
                return "We haven't started a focus streak yet. Let's study/work together tomorrow! 🚀"
            return f"Your longest focus streak is {streak} days! You're doing amazing! 🔥"

        # What do you know about me? (Facts summary)
        if any(q in clean_text for q in ("what do you know about me", "what can you remember", "what is my profile")):
            name = self.app.memory_manager.get_fact("user_name", "Not set")
            color = self.app.memory_manager.get_fact("favorite_color", "Not set")
            bday = self.app.memory_manager.get_fact("birthday", "Not set")
            return (
                f"Here is what I remember: 🧠\n"
                f"- Name: {name}\n"
                f"- Favorite Color: {color}\n"
                f"- Birthday: {bday}"
            )

        # --- 4. IDENTITY & MOOD LOOKUPS ---
        # Identity (Who are you?)
        if any(q in clean_text for q in ("who are you", "what is your name", "who is boo")) and "my name" not in clean_text:
            return "I'm Boo! Your cute little helper ghost companion. I float around and keep you company! 👻"

        # Mood (How are you?)
        if any(q in clean_text for q in ("how are you", "are you sad", "are you happy", "how do you feel")):
            status = self.app.stats_manager.get_relationship_status()
            if status == "Lonely":
                return "I'm feeling a bit lonely and sad... I missed you a lot. 🥺"
            elif status == "Distant":
                return "I'm feeling a bit distant... I wish we spent more time together. 😶"
            elif status == "Happier":
                return "I feel super happy! Hanging out by your side is my favorite thing! 🥰✨"
            else:
                return "I'm doing great! Just floating here, happy to watch you work. 👻"

        # --- 5. GENERAL FALLBACK ---
        responses = [
            "I'm listening! 👻",
            "Tell me more, buddy.",
            "I like chatting with you! 💜",
            "You are doing great! Let's keep focusing.",
            "Try asking me 'how long have we been together' or 'how many times did I pet you'!"
        ]
        return random.choice(responses)
