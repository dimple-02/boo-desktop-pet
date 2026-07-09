class CommandParser:
    def parse(self, text):
        """
        Parses raw user input text to match commands.
        Returns a tuple of (command_name, args_list).
        If no command matches, returns (None, None).
        """
        clean_text = text.lower().strip()

        # 1. Help Commands
        if clean_text in ("help", "?", "commands", "cmd"):
            return "help", []

        # 2. Follow Commands
        if clean_text in ("follow", "follow cursor", "follow me", "chase"):
            return "follow", []

        # 3. Stop Commands
        if clean_text in ("stop", "stay", "stop following", "stop follow", "freeze"):
            return "stop", []

        # 4. Workspace Search Commands (supporting prefixes like 'find', 'where is', 'search')
        search_prefixes = ["find", "search", "where is", "locate", "file"]
        for prefix in search_prefixes:
            if clean_text.startswith(prefix + " "):
                args_str = clean_text[len(prefix):].strip()
                args = args_str.split()
                return "search", args

        return None, None
