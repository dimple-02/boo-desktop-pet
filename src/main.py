import sys
from pathlib import Path

# Enforce inclusion of the 'src' directory in python search path
# to ensure modular imports run robustly from any execution context.
src_dir = Path(__file__).resolve().parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from core.app import BooApp

def main():
    try:
        app = BooApp()
        app.run()
    except Exception as e:
        print(f"[Bootstrapping Error] Failed to run Boo: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()