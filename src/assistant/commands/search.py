import os
import time
from pathlib import Path
from assistant.commands.base import BaseCommand

class SearchCommand(BaseCommand):
    def execute(self, args):
        """
        Recursively searches directories for a matching filename.
        Supports query syntax like:
        - "find file.txt" (defaults to project workspace)
        - "find file.txt on desktop"
        - "find file.txt in documents"
        - "find file.txt in downloads"
        - "find file.txt in D:\Pictures"
        """
        if not args:
            return "What file should I look for? 🔍"

        query = " ".join(args).strip()
        filename = query
        search_dir = self.app.base_dir  # default

        # Patterns to check search locations, e.g. "in [path]", "on [path]"
        path_indicators = [" in ", " on ", " at "]
        for indicator in path_indicators:
            if indicator in query.lower():
                parts = query.lower().split(indicator, 1)
                filename = parts[0].strip()
                dir_spec = parts[1].strip()

                # Check for standard location aliases
                if dir_spec in ("desktop", "the desktop"):
                    search_dir = Path.home() / "Desktop"
                elif dir_spec in ("documents", "my documents", "the documents"):
                    search_dir = Path.home() / "Documents"
                elif dir_spec in ("downloads", "my downloads", "the downloads"):
                    search_dir = Path.home() / "Downloads"
                else:
                    # Handle raw absolute or relative paths
                    try:
                        potential_path = Path(dir_spec)
                        if potential_path.is_absolute():
                            search_dir = potential_path
                        else:
                            search_dir = self.app.base_dir / potential_path
                    except Exception:
                        search_dir = self.app.base_dir
                break

        # Check if the target search directory actually exists
        if not search_dir.exists():
            return f"The folder '{search_dir}' doesn't seem to exist. 😢"

        found_paths = []
        start_time = time.time()
        dir_count = 0

        # Run directory traversal
        try:
            for root, dirs, files in os.walk(search_dir):
                # Safety Limit 1: Do not lock up GUI mainloop for more than 3 seconds
                if time.time() - start_time > 3.0:
                    break

                # Safety Limit 2: Do not scan more than 500 directories to prevent memory/performance issues
                dir_count += 1
                if dir_count > 500:
                    break

                # Prune hidden, cache, and system directories
                dirs[:] = [
                    d for d in dirs 
                    if not d.startswith(".") 
                    and d not in ("__pycache__", "node_modules", ".venv", "dist", "build", "$RECYCLE.BIN", "System Volume Information")
                ]

                for f in files:
                    if filename.lower() in f.lower():
                        full_path = Path(root) / f
                        found_paths.append(full_path)
                        if len(found_paths) >= 3:
                            break
                if len(found_paths) >= 3:
                    break
        except Exception as e:
            print(f"[SearchCommand] Error walking directory: {e}")
            return "I ran into a problem scanning your directories! 🥺"

        if not found_paths:
            return f"I couldn't find any file matching '{filename}' inside '{search_dir.name}'. 😢"

        # Format output paths cleanly
        formatted_results = []
        for path in found_paths:
            try:
                if path.is_relative_to(self.app.base_dir):
                    formatted_results.append(str(path.relative_to(self.app.base_dir)))
                elif path.is_relative_to(Path.home()):
                    rel_home = path.relative_to(Path.home())
                    formatted_results.append(f"~/{rel_home}")
                else:
                    formatted_results.append(str(path))
            except Exception:
                formatted_results.append(str(path))

        response = f"Found it! 🔍 ({search_dir.name})\n" + "\n".join(formatted_results[:3])
        if len(found_paths) > 3:
            response += "\n...and more!"
            
        return response
