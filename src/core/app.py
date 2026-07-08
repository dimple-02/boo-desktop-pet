import random
from pathlib import Path
from core.state_manager import StateManager
from ui.pet_window import PetWindow
from utils.image import load_and_scale_image
from managers.persistence import PersistenceManager

class BooApp:
    def __init__(self):
        # Initialize state manager and persistence
        self.state_manager = StateManager()
        self.persistence = PersistenceManager()

        # Load saved settings and window coordinates
        save_data = self.persistence.load_save_data()
        window_x = save_data.get("window_x")
        window_y = save_data.get("window_y")

        # Initialize window and pass callbacks
        self.window = PetWindow(
            on_drag_end=self._on_drag_end,
            on_double_click=self._on_double_click
        )

        # Restore saved coordinates if they exist
        if window_x is not None and window_y is not None:
            self.window.set_window_position(window_x, window_y)

        # Path resolution for base images
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.images_dir = self.base_dir / "assets" / "images" / "base"

        # Caching sprites
        self.sprites = {}
        self._load_sprites()

        # Animation states for floating
        self.float_offset = 0
        self.float_direction = 1

        # Bind initial view to initial sprite state
        self.update_sprite()

    def _load_sprites(self):
        """Loads and caches pet animation sprites using PIL utility."""
        sprite_size = (100, 100)
        
        # Load idle sprite
        idle_path = self.images_dir / "boo_idle.png"
        self.sprites["boo_idle.png"] = load_and_scale_image(idle_path, sprite_size)

        # Load blink sprite
        blink_path = self.images_dir / "boo_blink.png"
        self.sprites["boo_blink.png"] = load_and_scale_image(blink_path, sprite_size)

    def update_sprite(self):
        """Fetches the correct sprite from state manager and updates the view."""
        texture_name = self.state_manager.get_texture_name()
        photo = self.sprites.get(texture_name)
        if photo:
            self.window.set_image(photo)

    def start_blink_loop(self):
        """Coordinates Boo's eye-blinking sequence."""
        self.state_manager.set_animation("Blink")
        self.update_sprite()
        
        # Eyes stay closed for 180ms
        self.window.after(180, self._open_eyes)

    def _open_eyes(self):
        """Re-opens eyes and schedules the next random blink event."""
        self.state_manager.set_animation("Idle")
        self.update_sprite()
        
        # Next blink occurs randomly in 4 to 8 seconds
        next_blink = random.randint(4000, 8000)
        self.window.after(next_blink, self.start_blink_loop)

    def float_tick(self):
        """Coordinates the smooth float/drift movement loop."""
        # Simple vertical drift calculations
        self.float_offset += self.float_direction
        if self.float_offset >= 5:
            self.float_direction = -1
        elif self.float_offset <= -5:
            self.float_direction = 1

        # Translate relative Y offset onto the pet window label placement
        current_y = self.window.base_pet_y + self.float_offset
        self.window.set_pet_offset(self.window.base_pet_x, current_y)
        
        # Tick float update every 60ms
        self.window.after(60, self.float_tick)

    def _on_drag_end(self, x, y):
        """Callback triggered when drag-and-drop ends. Saves position to save.json."""
        self.persistence.save_save_data({
            "window_x": x,
            "window_y": y
        })

    def _on_double_click(self):
        """Callback triggered on double-click. Displays a random greeting speech bubble."""
        greetings = [
            "Hiiiiii!! ✨",
            "Boo is happy to see you! 💜",
            "Try dragging me around! 😉",
            "Blink... float... sleep... yawn...",
            "What a wonderful day! 🌸"
        ]
        text = random.choice(greetings)
        self.window.say(text)

    def run(self):
        """Starts background loops and launches the GUI event loop."""
        # Schedule initial loops
        self.window.after(3000, self.start_blink_loop)
        self.window.after(60, self.float_tick)
        
        # Run main loop
        self.window.start_loop()
