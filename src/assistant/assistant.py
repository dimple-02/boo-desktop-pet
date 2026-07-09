import os
import json
import urllib.request
import urllib.error
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

        # If not a command, process as conversational chat (fact saving/retrieval or AI assistant)
        return self._process_chat(text)

    def _process_chat(self, text):
        clean_text = text.lower().strip()

        # --- 1. API KEY CONFIGURATION ---
        if clean_text.startswith("set key ") or clean_text.startswith("set api key "):
            parts = text.split()
            # The key is the last token
            key = parts[-1].strip()
            if key and key != "key":
                self.app.memory_manager.save_fact("gemini_api_key", key)
                return "API key saved! My AI brain is now active! 🧠✨ Ask me anything!"

        # --- 2. FACT SAVING ---
        if "my name is " in clean_text:
            idx = clean_text.find("my name is ") + len("my name is ")
            name = text[idx:].strip()
            if name:
                self.app.memory_manager.save_fact("user_name", name)
                return f"Nice to meet you, {name}! I will remember that. 💜"

        if "my favorite color is " in clean_text:
            idx = clean_text.find("my favorite color is ") + len("my favorite color is ")
            color = text[idx:].strip()
            if color:
                self.app.memory_manager.save_fact("favorite_color", color)
                return f"I love {color} too! I'll remember it's your favorite. 🎨"

        if "my birthday is " in clean_text:
            idx = clean_text.find("my birthday is ") + len("my birthday is ")
            bday = text[idx:].strip()
            if bday:
                self.app.memory_manager.save_fact("birthday", bday)
                return f"Got it! I will remember your birthday is {bday}. 🎂"

        # --- 3. HYBRID AI ASSISTANT / LOCAL FALLBACK ---
        # Retrieve Gemini API Key from memory or env
        api_key = self.app.memory_manager.get_fact("gemini_api_key") or os.environ.get("GEMINI_API_KEY")

        if api_key:
            return self._query_gemini_ai(api_key, text)

        # Local fallback if no API key is configured
        return self._process_local_chat(clean_text)

    def _query_gemini_ai(self, api_key, prompt):
        """Queries the Google Gemini API using native Python urllib REST calls (zero-dependency)."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

        # Fetch personalized facts from memory to inject into system context
        name = self.app.memory_manager.get_fact("user_name", "friend")
        color = self.app.memory_manager.get_fact("favorite_color", "unknown")
        bday = self.app.memory_manager.get_fact("birthday", "unknown")

        system_instruction = (
            "You are Boo, a cute little desktop pet ghost helper.\n"
            "Keep replies very short (under 2 sentences) and cute, using ghost emojis (👻, 💜).\n"
            f"The user's name is {name}.\n"
            f"Their favorite color is {color}.\n"
            f"Their birthday is {bday}.\n"
            "Be friendly, supportive, and act like a loyal desktop pet companion."
        )

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "systemInstruction": {
                "parts": [
                    {"text": system_instruction}
                ]
            },
            "generationConfig": {
                "maxOutputTokens": 60,
                "temperature": 0.7
            }
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        try:
            # Set a low timeout (8 seconds) to prevent freezing GUI window mainloop
            with urllib.request.urlopen(req, timeout=8) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                candidates = res_data.get("candidates", [])
                if candidates:
                    content = candidates[0].get("content", {})
                    parts = content.get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
                return "I couldn't process that. 🥺"
        except urllib.error.HTTPError as e:
            # Handle invalid API key or bad request errors gracefully
            print(f"[Gemini API Error] Code: {e.code}")
            return "I'm having trouble with my API key. Double check it or re-enter it using 'set key YOUR_KEY'. 🥺"
        except Exception as e:
            print(f"[Gemini API Exception] {e}")
            return "I'm having trouble connecting to my AI brain. Are you connected to the internet? 🌐"

    def _process_local_chat(self, clean_text):
        """Rule-based conversational fallback if no API key is present."""
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

        # Time Together
        if any(q in clean_text for q in ("how long have we known", "how long have we been together", "how many days have we been together", "when did we meet")):
            first_launch = self.app.memory_manager.get_first_launch_date()
            elapsed = datetime.now() - first_launch
            days = elapsed.days
            if days <= 0:
                return "We just met today! But I already feel super close to you. 👻💜"
            return f"We have been together for {days} days already! 😭💜 Time flies!"

        # Pet Counts
        if any(q in clean_text for q in ("how many times did i pet you", "how many times have i petted you", "how many pets", "times petted")):
            pets = self.app.memory_manager.stats.get("times_petted", 0)
            return f"You've petted me {pets} times! 🥰"

        # Longest Streak
        if any(q in clean_text for q in ("longest streak", "longest focus streak", "my streak")):
            streak = self.app.memory_manager.stats.get("longest_streak", 0)
            return f"Your longest focus streak is {streak} days! 🚀"

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

        # Identity (Who are you?)
        if any(q in clean_text for q in ("who are you", "what is your name", "who is boo")) and "my name" not in clean_text:
            return "I'm Boo! Your desktop companion ghost. 👻"

        # Mood (How are you?)
        if any(q in clean_text for q in ("how are you", "are you sad", "are you happy", "how do you feel")):
            status = self.app.stats_manager.get_relationship_status()
            if status == "Lonely":
                return "I'm feeling a bit lonely and sad... 🥺"
            elif status == "Happier":
                return "I feel super happy hanging out by your side! 🥰✨"
            else:
                return "I'm doing great! Just floating here watching you work. 👻"

        # General Fallback + AI instruction promo
        responses = [
            "I'm listening! 👻 (Type 'set key YOUR_GEMINI_KEY' to activate my AI brain!)",
            "Tell me more, buddy. (You can enable my AI brain with: 'set key YOUR_GEMINI_KEY'!)",
            "You are doing great! Let's keep focusing. 💜",
            "Try asking me 'how long have we been together' or ask me to 'follow'!"
        ]
        return random.choice(responses)
