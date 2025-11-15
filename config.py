# --- World / Rendering ---
WORLD_WIDTH = 1280
WORLD_HEIGHT = 720
FPS = 60

# Palette (neo-ocean)
BG_COLOR = (8, 11, 18)            # base background
BG_VIGNETTE_ALPHA = 80            # 0..255
GRID_COLOR = (18, 24, 34)
FOOD_COLOR = (255, 214, 98)
FOOD_GLOW = (255, 240, 160)
ORG_COLOR = (106, 200, 255)
ORG_GLOW = (120, 230, 255)
MASTER_COLOR = (145, 255, 160)
FOV_COLOR = (110, 255, 150)
TARGET_COLOR = (255, 236, 128)

FOOD_RADIUS = 3  # draw size

# --- Population / Food / Genesis ---
START_ORGS = 25          # used if START_ADAM_EVE = False
START_FOOD = 80
MAX_FOOD = 220           # hard cap
FOOD_RESPAWN = True
TARGET_POP = 60          # soft carrying capacity for dynamic respawn

# Adam & Eve mode: start with 2 organisms (M/F) and let everything evolve from them
START_ADAM_EVE = True

# --- Physics (2D inertial) ---
BASE_THRUST = 55.0          # px/s^2 baseline thrust (scaled by trait_thrust_eff)
MAX_TURN_TORQUE = 3.0       # rad/s^2 cap on angular acceleration
LIN_DRAG = 1.4              # s^-1 linear drag
ANG_DRAG = 6.0              # s^-1 angular drag
MAX_SPEED = 240.0           # px/s clamp

# --- Perception defaults (each org mutates around these) ---
SENSOR_RANGE_DEFAULT = 160.0
SENSOR_FOV_DEG_DEFAULT = 120
SENSOR_RAYS = 5             # sample rays in FOV to build left/right signals

# --- Energy economy ---
START_ENERGY = 2.0
METABOLISM_BASE = 0.045
METABOLISM_SPEED_COEF = 0.00035
METABOLISM_BRAIN_COEF = 0.002
FOOD_ENERGY = 1.8
EAT_RADIUS = 6.0

# --- Reproduction / Sexual vs Asexual ---
REPRODUCTION_THRESHOLD = 5.5       # energy threshold for being "fertile"
PARENT_KEEP = 0.62                 # fraction of parent's energy kept after reproducing
CHILD_TAKE = 0.38                  # fraction given to child (per parent in sexual mode)

# Toggle sexual (True) vs asexual (False) reproduction
SEXUAL_REPRODUCTION = True

# Distance within which two compatible organisms can mate
MATING_RADIUS = 22.0

# Chance that an organism will choose to try to mate instead of forage
MATING_DRIVE_STRENGTH = 0.5  # 0..1 (higher = more eager to seek mates)

# --- Mutation / Traits ---
MUTATION_RATE = 0.08
MUTATION_SCALE = 0.25

# Heritable trait bounds (clamped after mutation)
FOV_MIN, FOV_MAX = 40.0, 180.0          # degrees
RANGE_MIN, RANGE_MAX = 70.0, 320.0      # px
THRUST_MIN, THRUST_MAX = 0.5, 2.0       # multiplier
META_MIN, META_MAX = 0.6, 1.6           # multiplier

# --- Brain / Learning / Development ---
# Neural controller size
BRAIN_INPUT_SIZE = 6        # [left, right, energy, speed, age, bias]
BRAIN_HIDDEN = 16           # can safely increase (32, 64…) with RTX 3080
BRAIN_OUTPUT_SIZE = 2       # [turn, thrust]

# Reward-modulated plasticity on recurrent weights
BRAIN_PLASTICITY_RATE = 0.001   # base strength of learning updates
BRAIN_PLASTICITY_DECAY = 1e-4   # weight decay per step to keep things bounded

# Developmental schedule: younger brains learn faster
DEV_LEARNING_AGE_HALF = 200.0   # age (s) where learning rate ~½ of max
DEV_LEARNING_MIN = 0.2          # minimum fraction of base plasticity later in life

# --- Sleep / Dreaming ---
SLEEP_PRESSURE_RATE = 0.02      # how fast sleep pressure accumulates while awake
SLEEP_RECOVERY_RATE = 0.15      # how fast pressure drops while sleeping
SLEEP_MIN_PRESSURE = 0.4        # threshold to start trying to fall asleep (0..1)
SLEEP_NIGHT_WEIGHT = 0.6        # weight of night in sleep drive (0..1)
SLEEP_METABOLISM_FACTOR = 0.4   # metabolism multiplier during sleep

DREAM_STEPS_PER_SEC = 8         # how many replay steps per second of sleep
MEMORY_BUFFER_SIZE = 128        # per-organism experience buffer size

# --- Environment / Weather ---
# Day/night and seasonal cycles (sim seconds)
DAY_LENGTH = 240.0              # length of a day
YEAR_LENGTH = 2400.0            # length of a year

# Temperature profile (Earth-ish, simplified)
BASE_TEMPERATURE_EQUATOR = 30.0     # baseline temp at equator (°C)
BASE_TEMPERATURE_POLE = 0.0         # baseline temp at poles (°C)
SEASONAL_VARIATION_EQUATOR = 5.0    # amplitude of seasonal variation at equator
SEASONAL_VARIATION_POLE = 20.0      # amplitude at poles

# Precipitation profile
BASE_PRECIPITATION = 0.5            # mean precipitation level (0..1)
PRECIP_VARIATION = 0.3              # seasonal amplitude
PRECIP_NOISE = 0.1                  # random noise magnitude per update

# Food regrowth modulation
BASE_REGROWTH = 0.10                # base probability per second
GROWTH_NOISE = 0.02                 # randomness added to growth factor
OPTIMAL_GROWTH_TEMP = 25.0          # °C for best growth
TEMP_TOLERANCE = 15.0               # |temp - optimal| below which growth is good

# --- Terrain / Homes / Nature & Nurture ---
# Tiles are currently just "PLAINS", but we plan for later terrain types:
# e.g. "FOREST", "WATER", "MOUNTAIN" with different movement/resource modifiers.

# Home building
CAN_BUILD_HOMES = True
HOME_BUILD_ENERGY_COST = 1.5        # energy cost to construct a home
HOME_RADIUS = 18.0                  # radius considered "at home"
HOME_CAPACITY = 4                   # how many dependents a home supports comfortably

# Parental care / nurture
CHILD_DEPENDENCY_AGE = 80.0         # age (s) during which children benefit from parents
PARENT_FEED_SHARE = 0.25            # fraction of parent's surplus energy that can be donated
PARENT_GUARD_RADIUS = 40.0          # how far parent will patrol around home/child
ORPHAN_PENALTY = 0.4                # multiplier on survival when no caregivers

# Cultural / tech evolution hooks (placeholders for future features)
TECH_DISCOVERY_BASE_RATE = 1e-4     # baseline chance of "discovering" a new behavior/tool
TECH_SPREAD_RADIUS = 120.0          # distance over which cultural traits can spread
MAX_TECH_TIERS = 5                  # how deep "tech tree" can go (for future extensions)

# --- Lifespan ---
MAX_AGE = 600.0  # seconds; mild senescence penalty after

# --- UI / Debug ---
STATUS_PRINT_INTERVAL = 1.0
DRAW_FOV = True

# --- Pretty ---
DRAW_GRID = True
GRID_SPACING = 64
MASTER_TRAIL_POINTS = 80
MASTER_TRAIL_ALPHA = 80
