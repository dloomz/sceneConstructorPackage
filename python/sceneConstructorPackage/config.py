import os
from pathlib import Path

# --- CORE CONFIGURATION ---

# Path: sceneConstructorPackage/config.py

# Resolve the project root dynamically, or use an environment variable
# SCENE_CONSTRUCTOR_ROOT should be set in the .module file or startup script
# For local testing, ensure 'D:/temp' structure exists.
#PROJECT_ROOT = Path(os.environ.get('SCENE_CONSTRUCTOR_ROOT', Path(__file__).parent.parent.absolute()))
PROJECT_ROOT = Path(os.environ.get('SCENE_CONSTRUCTOR_ROOT', r'C:\Users\Dolapo\Desktop\python\static\00_pipeline\sceneConstructorPackage'))

# --- DERIVED PATHS ---

# Root for JSON files (e.g., Jsons/)
JSON_PATH_ROOT = PROJECT_ROOT / 'Jsons'

# Root for all published scene/shot data (e.g., 25_footage/scene)
SCENE_ROOT = Path(os.environ.get('SCENE_DATA_ROOT', r'C:\Users\Dolapo\Desktop\python\static\25_footage\scene')) 

# Root for where the ActorPublisher will save final asset versions (e.g., 30_assets)
ASSET_PUBLISH_ROOT = Path(os.environ.get('ASSET_PUBLISH_ROOT', r'C:\Users\Dolapo\Desktop\python\static\30_assets'))

# Root for authors/users (used in the publisher UI)
AUTHORS_ROOT = Path(os.environ.get('AUTHORS_ROOT', r'C:\Users\Dolapo\Desktop\python\static\00_pipeline\userPrefs'))

# --- SPECIFIC FILE PATHS ---
ACTORS_JSON = JSON_PATH_ROOT / 'actors.json'

# Create necessary directories if they don't exist (helpful for first run)
JSON_PATH_ROOT.mkdir(exist_ok=True)
AUTHORS_ROOT.mkdir(exist_ok=True)
ASSET_PUBLISH_ROOT.mkdir(exist_ok=True)