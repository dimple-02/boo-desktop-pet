import random
from pathlib import Path
from core.config import (
    WIDTH, HEIGHT, PET_X, PET_Y, IMAGE_SIZE,
    FLOAT_INTERVAL_MS, BLINK_CLOSE_DURATION_MS,
    BLINK_INTERVAL_MIN_MS, BLINK_INTERVAL_MAX_MS,
    SPONTANEOUS_CHECK_INTERVAL_MS
)
from core.state_manager import StateManager
from ui.pet_window import PetWindow
from utils.image import load_and_scale_image
from managers.persistence import PersistenceManager
from managers.dialogue import DialogueManager
from managers.stats import StatsManager
from animations.float import FloatAnimation
from animations.blink import BlinkAnimation

class BooApp:
    def __init__(self):
        # Initialize state manager, persistence, and dialogue/stats managers
        self.state_manager = StateManager()
        self.persistence = PersistenceManager()
        self.stats_manager = StatsManager(self.persistence)
        self.dialogue_manager = DialogueManager()

        # Instantiate modular animations
        self.float_anim = FloatAnimation(PET_Y)
        self.blink_anim = BlinkAnimation(BLINK_INTERVAL_MIN_MS, BLINK_INTERVAL_MAX_MS)

        # Load saved settings and window coordinates
        save_data = self.persistence.load_save_data()
        window_x = save_data.get("window_x")
        window_y = save_data.get("window_y")

        # Initialize window and pass callbacks
        self.window = PetWindow(
            width=WIDTH,
            height=HEIGHT,
            on_drag_end=self._on_drag_end,
            on_double_click=self._on_double_click
        )

        # Restore saved coordinates if they exist
        if window_x is not None and window_y is not None:
            self.window.set_window_position(window_x, window_y)

        # Path resolution for images
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.images_dir = self.base_dir / "assets" / "images"

        # Caching sprites
        self.sprites = {}
        self._load_sprites()

        # Bind initial view to initial sprite state
        self.update_sprite()

    def _load_sprites(self):
        """Loads and caches pet animation sprites using PIL utility."""
        # Load idle sprite
        idle_path = self.images_dir / "idle.png"
        self.sprites["idle.png"] = load_and_scale_image(idle_path, IMAGE_SIZE)

        # Load blink sprite
        blink_path = self.images_dir / "blink.png"
        self.sprites["blink.png"] = load_and_scale_image(blink_path, IMAGE_SIZE)

        # Load sad sprite
        sad_path = self.images_dir / "boo_sad.png"
        self.sprites["boo_sad.png"] = load_and_scale_image(sad_path, IMAGE_SIZE)

    def update_sprite(self):
        """Fetches the correct sprite from state manager and updates the view."""
        texture_name = self.state_manager.get_texture_name()
        
        # Map state texture names to simplified image names
        is_blinking = "blink" in texture_name
        
        # Check relationship mood status
        status = self.stats_manager.get_relationship_status()
        if status == "Lonely" and not is_blinking:
            simplified_name = "boo_sad.png"
        else:
            simplified_name = "blink.png" if is_blinking else "idle.png"
            
        photo = self.sprites.get(simplified_name)
        if photo:
            self.window.set_image(photo)

    def start_blink_loop(self):
        """Coordinates Boo's eye-blinking sequence."""
        self.state_manager.set_animation("Blink")
        self.update_sprite()
        
        # Eyes stay closed for BLINK_CLOSE_DURATION_MS
        self.window.after(BLINK_CLOSE_DURATION_MS, self._open_eyes)

    def _open_eyes(self):
        """Re-opens eyes and schedules the next random blink event."""
        self.state_manager.set_animation("Idle")
        self.update_sprite()
        
        # Determine next blink timing from decoupled blink controller
        next_blink = self.blink_anim.get_next_interval()
        self.window.after(next_blink, self.start_blink_loop)

    def float_tick(self):
        """Coordinates the smooth float/drift movement loop."""
        # Retrieve float Y coordinates from decoupled float controller
        current_y = self.float_anim.tick()
        self.window.set_pet_offset(PET_X, current_y)
        
        # Tick float update every FLOAT_INTERVAL_MS
        self.window.after(FLOAT_INTERVAL_MS, self.float_tick)

    def idle_dialogue_tick(self):
        """Periodically checks if Boo should speak spontaneously in the background."""
        status = self.stats_manager.get_relationship_status()
        
        # Apply special neglect lonely mood override if active
        if status == "Lonely":
            self.state_manager.set_mood("Lonely")
        else:
            self.state_manager.set_mood("Neutral")

        text = self.dialogue_manager.get_dialogue(relationship_status=status, force=False)
        if text:
            self.window.say(text)
            # Make sure we redraw Boo sprite in case state transitions triggered mood updates
            self.update_sprite()
        
        # Run tick check
        self.window.after(SPONTANEOUS_CHECK_INTERVAL_MS, self.idle_dialogue_tick)

    def _on_drag_end(self, x, y):
        """Callback triggered when drag-and-drop ends. Saves position and updates stats."""
        # Save position coordinates
        self.persistence.save_save_data({
            "window_x": x,
            "window_y": y
        })
        
        # Add affection for gentle dragging
        self.stats_manager.record_drag()
        self.update_sprite()

    def _on_double_click(self):
        """Callback triggered on double-click. Petting adds affection and forces dialogue."""
        # Add affection for petting
        self.stats_manager.record_pat()

        status = self.stats_manager.get_relationship_status()
        text = self.dialogue_manager.get_dialogue(relationship_status=status, force=True)
        self.window.say(text)
        self.update_sprite()

    def run(self):
        """Starts background loops and launches the GUI event loop."""
        # Schedule initial loops
        self.window.after(3000, self.start_blink_loop)
        self.window.after(60, self.float_tick)
        self.window.after(10000, self.idle_dialogue_tick) # First spontaneous check at 10 seconds
        
        # Run main loop
        self.window.start_loop()
