"""
TerraDesk – Global Constants
Single source of truth for all tuneable values.
"""

# ── Window ───────────────────────────────────────────────────────────────────
WINDOW_WIDTH  = 1600
WINDOW_HEIGHT = 900
FPS_TARGET    = 60

TOOLBAR_HEIGHT = 46
SIDEBAR_WIDTH  = 240
PANEL_PADDING  = 10

# ── Grid ─────────────────────────────────────────────────────────────────────
GRID_COLS = 60
GRID_ROWS = 60

# Isometric tile dimensions (base, before zoom)
TILE_W      = 64   # full tile pixel width  (2 × half-width)
TILE_H      = 32   # full tile pixel height (2 × half-height)
TILE_HALF_W = 32
TILE_HALF_H = 16

# ── Camera ───────────────────────────────────────────────────────────────────
CAMERA_PAN_SPEED  = 300.0   # px/s
CAMERA_ZOOM_MIN   = 0.3
CAMERA_ZOOM_MAX   = 3.0
CAMERA_ZOOM_STEP  = 0.12

# ── Simulation ────────────────────────────────────────────────────────────────
TICKS_PER_MINUTE   = 10        # sim ticks per in-game minute at speed 1
SIM_SPEEDS         = [0, 1, 2, 4, 8]
SIM_SPEED_LABELS   = ["||", "1x", "2x", "4x", "8x"]
AUTOSAVE_INTERVAL  = 180.0     # real seconds

# ── Time ─────────────────────────────────────────────────────────────────────
HOURS_PER_DAY   = 24
DAYS_PER_SEASON = 7
SEASONS_PER_YEAR = 4

# ── Economy ──────────────────────────────────────────────────────────────────
STARTING_MONEY      = 5000.0
TAX_RATE_DEFAULT    = 0.10     # 10 %
CITIZEN_SALARY      = 50.0     # per game-day
FOOD_PRICE          = 5.0
WOOD_PRICE          = 8.0
STONE_PRICE         = 10.0

BUILDING_COSTS = {
    "house":       {"money": 200},
    "farm":        {"money": 300},
    "market":      {"money": 500},
    "school":      {"money": 800},
    "hospital":    {"money": 1200},
    "church":      {"money": 600},
    "tavern":      {"money": 400},
    "well":        {"money": 100},
    "mill":        {"money": 350},
    "blacksmith":  {"money": 300},
    "warehouse":   {"money": 450},
    "road":        {"money": 20},
    "tree":        {"money": 10},
    "bridge":      {"money": 250},
}

# ── Citizen AI ───────────────────────────────────────────────────────────────
AI_THINK_INTERVAL   = 120     # ticks between AI decisions
NEED_HUNGER_DECAY   = 0.0004
NEED_ENERGY_DECAY   = 0.0003
NEED_SOCIAL_DECAY   = 0.0002
NEED_HAPPINESS_DECAY = 0.0001

# ── Desktop ───────────────────────────────────────────────────────────────────
DESKTOP_WALLPAPER_MODE  = False
DESKTOP_ALWAYS_ON_TOP   = False
DESKTOP_CLICK_THROUGH   = False

# ── Colours (R, G, B) ────────────────────────────────────────────────────────
# UI chrome
C_UI_PANEL      = (22,  24,  32)
C_UI_BORDER     = (60,  65,  85)
C_UI_BUTTON     = (35,  38,  52)
C_UI_BUTTON_HOV = (50,  54,  72)
C_UI_BUTTON_ACT = (45,  80, 120)
C_UI_HOVER      = (40,  44,  58)
C_UI_SELECTED   = (30,  70, 110)
C_UI_TEXT       = (220, 225, 235)
C_UI_TEXT_DIM   = (130, 138, 160)
C_UI_ACCENT     = (90,  170, 255)
C_UI_ACCENT2    = (160, 110, 255)
C_UI_SUCCESS    = (80,  200, 110)
C_UI_WARNING    = (240, 180,  50)
C_UI_DANGER     = (230,  70,  60)

# Terrain tile colours
C_GRASS_LIGHT   = (110, 180,  80)
C_GRASS_MID     = ( 90, 160,  65)
C_GRASS_DARK    = ( 70, 130,  50)
C_GRASS_TOP     = (140, 210, 100)
C_DIRT          = (170, 130,  80)
C_DIRT_DARK     = (130, 100,  60)
C_WATER_LIGHT   = ( 60, 140, 200)
C_WATER_MID     = ( 50, 120, 180)
C_WATER_DARK    = ( 40, 100, 160)
C_WATER_SHINE   = (120, 190, 240)
C_SAND          = (210, 190, 130)
C_SAND_DARK     = (180, 160, 100)
C_ROCK          = (120, 120, 130)
C_ROCK_DARK     = ( 90,  90, 100)
C_SNOW_LIGHT    = (230, 240, 255)
C_SNOW_DARK     = (200, 215, 240)
C_PATH_TOP      = (180, 155, 110)
C_PATH_SIDE     = (140, 118,  80)

# Building colours
C_WALL_LIGHT    = (210, 190, 155)
C_WALL_MID      = (180, 160, 125)
C_WALL_DARK     = (140, 120,  90)
C_ROOF_RED      = (180,  60,  50)
C_ROOF_RED_D    = (140,  45,  38)
C_ROOF_BROWN    = (120,  80,  45)
C_ROOF_BROWN_D  = ( 90,  58,  30)
C_ROOF_GREY     = (100, 100, 115)
C_ROOF_GREY_D   = ( 75,  75,  88)
C_ROOF_BLUE     = ( 60,  90, 160)
C_ROOF_BLUE_D   = ( 42,  65, 120)
C_WINDOW_GLOW   = (255, 230, 100)
C_WINDOW_DAY    = (160, 200, 240)
C_DOOR          = ( 90,  58,  30)
C_CHIMNEY       = ( 80,  80,  88)
C_CHIMNEY_DARK  = ( 55,  55,  62)

# Tree colours
C_TREE_TRUNK    = (100,  70,  40)
C_TREE_SPRING   = ( 80, 180,  70)
C_TREE_SUMMER   = ( 55, 155,  50)
C_TREE_AUTUMN   = (200, 110,  40)
C_TREE_WINTER   = (200, 220, 240)

# Farm colours
C_CROP_GREEN    = (120, 190,  70)
C_CROP_YELLOW   = (220, 190,  60)
C_FIELD_BROWN   = (160, 110,  55)

# Citizen colours
C_CITIZEN_SHIRT = [(200, 80, 60), (60, 120, 200), (60, 180, 100),
                   (220, 170, 50), (160, 90, 200), (200, 200, 200)]
C_CITIZEN_PANTS = [(60, 80, 120), (80, 60, 40), (40, 50, 70),
                   (100, 80, 60), (50, 50, 50)]
C_CITIZEN_HAIR_1 = (60, 40, 20)
C_CITIZEN_HAIR_2 = (200, 160, 80)
C_CITIZEN_HAIR_3 = (30, 30, 30)
C_CITIZEN_SKIN   = (220, 180, 140)
C_CITIZEN_SKIN_2 = (160, 110,  80)
C_CITIZEN_SKIN_3 = (100,  70,  45)

# Sky / lighting
C_SKY_DAY       = ( 90, 170, 240)
C_SKY_DAWN      = (220, 140,  80)
C_SKY_DUSK      = (180,  90,  60)
C_SKY_NIGHT     = ( 10,  15,  35)
C_SKY_MIDNIGHT  = (  5,   8,  22)