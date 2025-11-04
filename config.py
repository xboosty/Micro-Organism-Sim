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

# --- Population / Food ---
START_ORGS = 25
START_FOOD = 80
MAX_FOOD = 220              # adjusted cap
FOOD_RESPAWN = True
TARGET_POP = 60             # soft carrying capacity for dynamic respawn

# --- Physics (2D inertial) ---
BASE_THRUST = 55.0          # px/s^2 baseline thrust (scaled by trait thrust_eff)
MAX_TURN_TORQUE = 3.0       # rad/s^2 cap on angular acceleration
LIN_DRAG = 1.4              # s^-1 linear drag
ANG_DRAG = 6.0              # s^-1 angular drag
MAX_SPEED = 240.0           # px/s clamp

# --- Perception default (each org mutates around these) ---
SENSOR_RANGE_DEFAULT = 160.0
SENSOR_FOV_DEG_DEFAULT = 120
SENSOR_RAYS = 5             # sample rays in FOV to build left/right signals

# --- Energy economy (tighter) ---
START_ENERGY = 2.0
METABOLISM_BASE = 0.045           # was 0.03
METABOLISM_SPEED_COEF = 0.00035   # was 0.00025
METABOLISM_BRAIN_COEF = 0.002
FOOD_ENERGY = 1.8                  # was 2.2
EAT_RADIUS = 6.0

# --- Reproduction / Mutation ---
REPRODUCTION_THRESHOLD = 5.5       # was 4.5
PARENT_KEEP = 0.62                 # was 0.58
CHILD_TAKE = 0.38                  # was 0.42
MUTATION_RATE = 0.08
MUTATION_SCALE = 0.25

# Heritable trait bounds (clamped after mutation)
FOV_MIN, FOV_MAX = 40, 180               # degrees
RANGE_MIN, RANGE_MAX = 70.0, 320.0       # px
THRUST_MIN, THRUST_MAX = 0.5, 2.0        # multiplier
META_MIN, META_MAX = 0.6, 1.6            # multiplier

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
