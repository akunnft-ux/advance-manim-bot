import os

HISTORY_FILE = "data/history.json"
MODE_FILE = "data/mode.json"
MAX_HISTORY_ITEMS = 180

# Render timeout per complexity tier (seconds)
RENDER_TIMEOUT = {"simple": 300, "medium": 600, "complex": 900}

# Scene complexity tier config
DEFAULT_COMPLEXITY = "medium"

TOPICS = {
    "kalkulus": "Kalkulus",
    "aljabar-linear": "Aljabar Linear",
    "geometri-3d": "Geometri 3D",
    "probstat": "Probabilitas & Statistika",
}

TOPIC_DESCRIPTIONS = {
    "kalkulus": "limit, turunan, integral, deret tak hingga, visualisasi fungsi",
    "aljabar-linear": "matriks, vektor, transformasi linear, eigenvalue, ruang dimensi",
    "geometri-3d": "bangun ruang, surface plot, transformasi 3D, visualisasi multivariabel",
    "probstat": "distribusi probabilitas, teorema Bayes, regresi, visualisasi data",
}

CTA_POOL = [
    "Follow untuk konten matematika visual setiap hari!",
    "Jangan lupa follow biar makin paham kalkulus!",
    "Follow akun ini buat visualisasi matematika yang engaging!",
    "Klik follow biar gak ketinggalan video matematika terbaru!",
]

HASHTAG_POOL = [
    "#Matematika", "#Kalkulus", "#BelajarMatematika",
    "#VisualisasiMatematika", "#MathAnimation", "#3Blue1Brown",
    "#MathIsFun", "#MathVisualization", "#Mathematics",
]

SCENE_ELEMENT_MAP = {
    "title": "text",
    "subtitle": "text",
    "equation": "latex",
    "label": "text",
    "axes": "axes",
    "function_graph": "function",
    "surface": "surface_3d",
    "sphere": "sphere_3d",
    "torus": "torus_3d",
    "dot_cloud": "dot_cloud",
    "vector": "vector",
    "matrix": "matrix",
    "number_line": "number_line",
    "grid": "grid",
}

ALLOWED_ANIMATIONS = {
    "write", "fade_in", "fade_out", "transform", "create",
    "lagged_start", "grow_from_center", "move_along_path",
    "draw_border_then_fill", "indicate", "flash",
}

ALLOWED_SCENE_TYPES = {"intro", "visualization", "conclusion", "transition"}

ALLOWED_CHARACTER_EXPRESSIONS = {"default", "explain", "happy"}

ALLOWED_CHARACTER_POSITIONS = {"bottom_left", "bottom_right"}


def get_env(key: str) -> str:
    val = os.environ.get(key)
    if not val:
        raise ValueError(f"{key} not set")
    return val
