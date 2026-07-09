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
from managers.memory import MemoryManager
from assistant.assistant import Assistant
from animations.float import FloatAnimation
from animations.blink import BlinkAnimation
from animations.follow import FollowAnimation

class BooApp:
    def __init__(self):
        # Initialize state manager and persistence
        self.state_manager = StateManager()
        self.persistence = PersistenceManager()

        # Initialize managers
        self.stats_manager = StatsManager(self.persistence)
        self.memory_manager = MemoryManager(self.persistence)
        self.dialogue_manager = DialogueManager()
        self.assistant = Assistant(self)

        # Instantiate animations
        self.float_anim = FloatAnimation(PET_Y)
        self.blink_anim = BlinkAnimation(BLINK_INTERVAL_MIN_MS, BLINK_INTERVAL_MAX_MS)
        self.follow_anim = FollowAnimation(speed=0.08)

        # Core state flags
        self.is_following_cursor = False

        # Load saved settings and window coordinates
        save_data = self.persistence.load_save_data()
        window_x = save_data.get("window_x")
        window_y = save_data.get("window_y")

        # Initialize window and pass callbacks
        self.window = PetWindow(
            width=WIDTH,
            height=HEIGHT,
            on_drag_end=self._on_drag_end,
            on_double_click=self._on_double_click,
            on_submit=self._on_submit,
            on_toggle_input=self._on_toggle_input
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
        # Skip float Y-offset calculations if currently chasing the cursor
        if not self.is_following_cursor:
            current_y = self.float_anim.tick()
            self.window.set_pet_offset(PET_X, current_y)
        
        # Tick float update every FLOAT_INTERVAL_MS
        self.window.after(FLOAT_INTERVAL_MS, self.float_tick)

    def start_follow_cursor(self):
        """Switches app activity state to enable smooth cursor chasing."""
        if not self.is_following_cursor:
            self.is_following_cursor = True
            # Center pet Y offset inside window during active movement
            self.window.set_pet_offset(PET_X, PET_Y)
            self.follow_cursor_tick()

    def stop_follow_cursor(self):
        """Disables cursor chasing and returns Boo to static placement."""
        self.is_following_cursor = False
        self.update_sprite()

    def follow_cursor_tick(self):
        """Loop updating Boo window coordinates towards mouse cursor (60 FPS LERP)."""
        if not self.is_following_cursor:
            return

        # Query pointer position and window coordinates
        mx = self.window.root.winfo_pointerx()
        my = self.window.root.winfo_pointery()
        wx, wy = self.window.get_window_position()

        # Calculate step destination coordinates
        new_wx, new_wy = self.follow_anim.calculate_next_position(wx, wy, mx, my)
        self.window.set_window_position(new_wx, new_wy)

        # Run tick at 16ms (approx 60 updates per second)
        self.window.after(16, self.follow_cursor_tick)

    def idle_dialogue_tick(self):
        """Periodically checks if Boo should speak spontaneously in the background."""
        # Skip idle random comments if actively chasing the cursor
        if self.is_following_cursor:
            self.window.after(SPONTANEOUS_CHECK_INTERVAL_MS, self.idle_dialogue_tick)
            return

        status = self.stats_manager.get_relationship_status()
        if status == "Lonely":
            self.state_manager.set_mood("Lonely")
        else:
            self.state_manager.set_mood("Neutral")

        text = self.dialogue_manager.get_dialogue(relationship_status=status, force=False)
        if text:
            # Standard random dialogue does not show chat input
            self.window.say(text, show_input=False)
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
        """Callback triggered on double-click. Petting adds affection, increments petted stats, and forces standard dialogue."""
        self.stats_manager.record_pat()
        self.memory_manager.record_pet()

        status = self.stats_manager.get_relationship_status()
        text = self.dialogue_manager.get_dialogue(relationship_status=status, force=True)
        # Double click dialogue fades normally without showing the input field
        self.window.say(text, duration_ms=4000, show_input=False)
        self.update_sprite()

    def _on_toggle_input(self):
        """Callback when user triggers Shift+T shortcut. Opens input chat bubble."""
        self.window.show_chat_input()

    def _on_submit(self, text):
        """Callback triggered when the user types and submits a chat entry to Boo."""
        # Process query through the Assistant coordinator
        response = self.assistant.process_input(text)
        
        # Display Boo's response immediately.
        # We pass duration_ms=0 and show_input=True to keep the chat loop open for further inputs.
        self.window.say(response, duration_ms=0, show_input=True)
        self.update_sprite()

    def run(self):
        """Starts background loops and launches the GUI event loop."""
        # Schedule initial loops
        self.window.after(3000, self.start_blink_loop)
        self.window.after(60, self.float_tick)
        self.window.after(10000, self.idle_dialogue_tick)
        
        # Run main loop
        self.window.start_loop()
