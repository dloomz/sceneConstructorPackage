import json
import os
from pathlib import Path
from .. import config

# Path: sceneConstructorPackage/core/data_manager.py

class DataManager:
    """
    Handles all file I/O operations for Actors, Scenes, and Shots.
    Decouples UI classes from file system logic.
    """

    def __init__(self):
        self.actors_path = config.ACTORS_JSON

    # --- ACTOR PRESET METHODS ---

    def load_actors(self) -> list:
        """Loads all global Actors from actors.json."""
        try:
            with open(self.actors_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[WARN] Actors file missing or invalid: {e}. Returning empty list.")
            return []
        except Exception as e:
            print(f"[ERROR] Could not load Actors JSON: {e}")
            return []

    def save_actors(self, data: list):
        """Saves the list of Actors to actors.json."""
        try:
            with open(self.actors_path, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"[OK] Actors saved to {self.actors_path}")
        except Exception as e:
            print(f"[ERROR] Could not save Actors JSON: {e}")

    # --- SCENE/SHOT MANAGEMENT METHODS ---
        
    def get_scenes(self):
        """Returns a list of all scene folders in the SCENE_ROOT."""
        if not config.SCENE_ROOT.exists():
            return []
        # Filter for directories and return names
        return sorted([d.name for d in config.SCENE_ROOT.iterdir() if d.is_dir()])

    def get_shots_in_scene(self, scene_name: str):
        """Returns a list of all shot folders within a given scene."""
        scene_path = config.SCENE_ROOT / scene_name
        if not scene_path.exists():
            return []
        return sorted([d.name for d in scene_path.iterdir() if d.is_dir()])

    def load_shot_data(self, scene_name: str, shot_name: str) -> tuple[str, dict]:
        """
        Finds the SceneConstructor JSON file for a shot and loads its content.
        Returns the path (str) and the data (dict).
        """
        # Looks for the JSON file inside the 'SceneConstructor' sub-folder for the shot
        shot_dir = config.SCENE_ROOT / scene_name / shot_name / 'SceneConstructor'
        
        if not shot_dir.exists():
            return "", {}

        # Scan for the JSON file (assuming one per shot)
        for f in shot_dir.iterdir():
            if f.suffix.lower() == '.json':
                try:
                    with open(f, 'r') as json_file:
                        data = json.load(json_file)
                        # We return the whole shot dictionary (e.g., {'shot_001': [...]})
                        return str(f), data
                except Exception as e:
                    print(f"[ERROR] Failed to load shot JSON {f}: {e}")
                    return "", {}
        return "", {}

    def save_shot_data(self, shot_json_path: str, shot_data: dict):
        """Saves the shot data dictionary to the specified JSON path."""
        try:
            with open(shot_json_path, "w") as f:
                json.dump(shot_data, f, indent=4)
            print(f"[OK] Shots saved to {shot_json_path}")
        except Exception as e:
            print(f"[ERROR] Could not save Shots JSON: {e}")