# Boo Application Configuration Constants

# Window dimensions
WIDTH = 160
HEIGHT = 200
FPS = 60

# Pet label positioning offsets within the transparent root window
PET_X = 30
PET_Y = 90

# Image scaling size
IMAGE_SIZE = (100, 100)

# Timing intervals (in milliseconds)
FLOAT_INTERVAL_MS = 60
BLINK_CLOSE_DURATION_MS = 180
BLINK_INTERVAL_MIN_MS = 4000
BLINK_INTERVAL_MAX_MS = 8000

# Dialogue timing (in seconds / milliseconds)
SPONTANEOUS_CHECK_INTERVAL_MS = 30000     # Tick check runs every 30 seconds
COOLDOWN_IDLE_SPEECH_SEC = 15 * 60         # Speech cooldown is 15 minutes
SPEECH_BUBBLE_DURATION_MS = 4000          # Bubble hides after 4 seconds

# Hidden Progression Mechanics thresholds
TRUST_MAX = 100
AFFECTION_MAX = 100

# Neglect parameters
NEGLECT_THRESHOLD_SEC = 48 * 60 * 60       # Neglect triggers after 48 hours (2 days)
SLOW_RECOVERY_DURATION_SEC = 30 * 60       # Slow recovery dampening lasts for 30 minutes
DAMPING_FACTOR = 0.5                      # 50% stat dampening during recovery
