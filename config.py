"""
Configuration file for ForceQuest
Contains all constants, color schemes, and default values
"""

# Application Settings
APP_TITLE = "⚙️ P6Quest — Physics Adventure Mode"
APP_GEOMETRY = "1400x1000"
QUIZ_TITLE = "💡 P6Quest Quiz Time!"
QUIZ_GEOMETRY = "800x600"

# Colors
COLORS = {
    'bg_dark': '#1e1e2f',
    'bg_panel': '#252540',
    'primary': '#00e6e6',
    'success': '#98c379',
    'error': '#ff6b6b',
    'warning': '#ffaa00',
    'info': '#61afef',
    'text_light': '#bbb',
    'text_white': 'white',
    'text_dark': 'black',
}

# Compatibility aliases expected by app.py
WINDOW = {'width': 1400, 'height': 900}

# Colors expected by the newer UI modules
COLORS.update({
    'bg_primary': COLORS.get('bg_dark'),
    'bg_secondary': COLORS.get('bg_panel'),
    'accent_cyan': COLORS.get('primary'),
    'accent_green': COLORS.get('success'),
    'accent_red': COLORS.get('error'),
    'accent_yellow': COLORS.get('warning'),
    'accent_blue': COLORS.get('info'),
    'text_gray': COLORS.get('text_light')
})

# Basic font presets used by the UI
FONTS = {
    'title': ("Consolas", 24, "bold"),
    'subtitle': ("Segoe UI", 11, "italic"),
    'timer': ("Consolas", 11, "bold"),
    'feedback': ("Consolas", 11, "bold"),
    'solution': ("Consolas", 10),
    'button': ("Segoe UI", 10),
    'label': ("Segoe UI", 10),
    'instruction': ("Segoe UI", 10),
    'normal': ("Segoe UI", 10),
    'header': ("Consolas", 18, "bold")
}

# Physics Constants
GRAVITY = 9.81  # m/s²

# Surface Friction Coefficients
SURFACE_FRICTION = {
    "Ice": 0.1,
    "Tile": 0.3,
    "Wood": 0.5,
    "Concrete": 0.7,
    "Sand": 0.9
}

# Shape Friction Factors
SHAPE_FRICTION_FACTOR = {
    "Box": 1.0,
    "Cylinder": 0.15,
    "Sphere": 0.05
}

# Force Angle Mapping
FORCE_ANGLE_MAP = {
    "Horizontal": 0,
    "Upward": 30,
    "Downward": -30
}

# Surface Background Colors and Labels
SURFACE_COLORS = {
    "Ice": ("#b3e5fc", "❄️ ICE"),
    "Tile": ("#f0f0f0", "🏠 TILE"),
    "Wood": ("#deb887", "🪵 WOOD"),
    "Concrete": ("#a9a9a9", "🏗️ CONCRETE"),
    "Sand": ("#e69f00", "🏖️ SAND"),
}

# Object Colors
OBJECT_COLORS = {
    'Pushing Object': '#ff6f61',
    'Lifting Object': '#f4a261',
    'Inclined Plane': '#d95f02',
}

# Animation Settings
DEFAULT_ANIMATION_SPEED = 1.0
MIN_ANIMATION_SPEED = 0.5
MAX_ANIMATION_SPEED = 3.0
ANIMATION_DELAY = 0.02

# Canvas Settings
CANVAS = {
    'width': 800,
    'height': 450,
    'ground_y': 400,
    'ground_height': 50
}

# Scenarios
SCENARIOS = ["Pushing Object", "Lifting Object", "Inclined Plane"]

# Surface Materials
SURFACE_MATERIALS = ["Ice", "Tile", "Wood", "Concrete", "Sand"]

# Object Shapes
OBJECT_SHAPES = ["Box", "Cylinder", "Sphere"]

# Force Angles
FORCE_ANGLES = ["Horizontal", "Upward", "Downward"]

# Push Modes
PUSH_MODES = ["Constant Force", "Sudden Push", "Increasing Force"]
ANIMATION_DELAY = 0.02  # seconds

# Canvas Settings
CANVAS_WIDTH = 700
CANVAS_HEIGHT = 450
GROUND_Y = 400
CANVAS = {
    'width': CANVAS_WIDTH,
    'height': CANVAS_HEIGHT,
    'ground_y': GROUND_Y,
    'ground_height': 50,
    'bg': 'white',
    'highlight': '#00e6e6'
}
CANVAS_HIGHLIGHT = '#00e6e6'

# Scenarios
SCENARIOS = ["Pushing Object", "Lifting Object", "Inclined Plane"]
SURFACES = ["Ice", "Tile", "Wood", "Concrete", "Sand"]
SHAPES = ["Box", "Cylinder", "Sphere"]
FORCE_ANGLES = ["Horizontal", "Upward", "Downward"]
PUSH_MODES = ["Constant Force", "Sudden Push", "Increasing Force"]

# Backwards-compatible aliases expected by older modules
SURFACE_MATERIALS = SURFACES
OBJECT_SHAPES = SHAPES