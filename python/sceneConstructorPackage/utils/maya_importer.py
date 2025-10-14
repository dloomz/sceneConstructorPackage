import maya.cmds as cmds
import os
import json

# Path: sceneConstructorPackage/python/sceneConstructorPackage/utils/maya_importer.py

# IMPORTANT: Updated imports to use new core modules
from ...core.data_manager import DataManager 

class ShotLoaderUI(object):
    def __init__(self):
        # 🆕 Initialize DataManager
        self.data_manager = DataManager()
        self.window = "shotLoader"
        
        self.build_ui()
        self.load_scenes()

    # ... (build_ui, load_scenes, scene_changed, load_shots_in_scenes remain the same, 
    # but use self.data_manager.get_scenes() and self.data_manager.get_shots_in_scene() 
    # instead of os.listdir on hardcoded paths)

    def import_actors(self, *args):
        """
        Loads the shot JSON and imports all assets into the current Maya scene.
        """
        current_selected_scene = cmds.optionMenu(self.scene_dropdown, q=True, value=True)
        current_selected_shot = cmds.optionMenu(self.shot_dropdown, q=True, value=True)

        if not current_selected_scene or not current_selected_shot:
            print("[ERROR] Please select a Scene and a Shot.")
            return

        # 🆕 Use DataManager to load the shot data
        shot_json_path, shot_data_dict = self.data_manager.load_shot_data(
            current_selected_scene, current_selected_shot
        )

        if not shot_data_dict:
            print(f"[ERROR] Could not load data for shot: {current_selected_shot}")
            return

        # Extract the list of items for the current shot
        shot_items = shot_data_dict.get(current_selected_shot.casefold(), [])

        for item in shot_items:
            path_to_import = item.get("path")
            actor_name = item.get("name", "UnknownActor")
            actor_type = item.get("type", "asset")

            if not path_to_import:
                print(f"[WARN] Actor {actor_name} is missing a path. Skipping.")
                continue

            # 1. Determine Maya File Type and Namespace
            file_type = "file" # Default for Maya files (.ma, .mb)
            if path_to_import.lower().endswith(('.usd', '.usda', '.usdc')):
                file_type = "USD Import"
            elif path_to_import.lower().endswith(('.fbx')):
                # Note: FBX/Alembic may need more specific plugin-based import commands
                print(f"[WARN] FBX/Alembic import logic is a placeholder for {path_to_import}")
                # You would typically use cmds.AbcImport or fbx.importFbx here

            # Create a unique namespace to prevent object name conflicts
            namespace = f"{current_selected_shot}_{actor_name}"
            
            # 2. Execute the Maya import command
            try:
                cmds.file(
                    path_to_import,
                    i=True, # import mode
                    type=file_type,
                    ignoreVersion=True,
                    mergeNamespacesOnClash=False,
                    namespace=namespace,
                    options="v=0;p=17;f=0" # Common options for Maya files
                )
                print(f"[SUCCESS] Imported {actor_name} into namespace {namespace}")
            except Exception as e:
                print(f"[ERROR] Failed to import {actor_name} from {path_to_import}: {e}")