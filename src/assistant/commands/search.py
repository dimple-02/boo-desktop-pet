import os
from pathlib import Path
from assistant.commands.base import BaseCommand

class SearchCommand(BaseCommand):
    def execute(self, args):
        """Recursively searches the workspace for a file matching the argument query."""
        if not args:
            return "What file should I look for? 🔍"
            
        filename = " ".join(args).strip()
        base_dir = self.app.base_dir
        
        found_paths = []
        
        # Traverse directories recursively
        for root, dirs, files in os.walk(base_dir):
            # Prune hidden and dependencies directories to keep search fast and secure
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("__pycache__", "node_modules", ".venv", "dist", "build")]
            
            for f in files:
                if filename.lower() in f.lower():
                    full_path = Path(root) / f
                    # Calculate path relative to the project root
                    try:
                        rel_path = full_path.relative_to(base_dir)
                        found_paths.append(str(rel_path))
                    except ValueError:
                        found_paths.append(f)
                        
                    # Limit output to prevent bubble text overflow
                    if len(found_paths) >= 3:
                        break
            if len(found_paths) >= 3:
                break
                
        if not found_paths:
            return f"I couldn't find '{filename}' anywhere in our folder. 😢"
            
        response = "Found it! 🔍\n" + "\n".join(found_paths[:3])
        if len(found_paths) > 3:
            response += "\n...and more!"
            
        return response
