import os
from pathlib import Path

# --- CORE CONFIGURATION ---

# Path: sceneConstructorPackage/config.py

# Resolve the project root dynamically, or use an environment variable
# SCENE_CONSTRUCTOR_ROOT should be set in the .module file or startup script
PROJECT_ROOT = Path(os.environ.get('SCENE_CONSTRUCTOR_ROOT', Path(__file__).parent.parent.parent.absolute()))

# --- DERIVED PATHS ---

# Root for JSON files (e.g., Jsons/)
JSON_PATH_ROOT = PROJECT_ROOT / 'Jsons'

# Root for all published scene/shot data (e.g., 25_footage/scene)
# This path should ideally be set as an environment variable (e.g., SCENE_DATA_ROOT)
SCENE_ROOT = Path(os.environ.get('SCENE_DATA_ROOT', 'D:/temp/25_footage/scene')) 

# Root for authors used in the publisher UI
AUTHORS_ROOT = Path(os.environ.get('AUTHORS_ROOT', 'D:/temp/authors'))

# --- SPECIFIC FILE PATHS ---
ACTORS_JSON = JSON_PATH_ROOT / 'actors.json'

# Create necessary directories if they don't exist
JSON_PATH_ROOT.mkdir(exist_ok=True)
AUTHORS_ROOT.mkdir(exist_ok=True)