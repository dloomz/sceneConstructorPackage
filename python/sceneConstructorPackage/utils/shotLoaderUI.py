import maya.cmds as cmds
import os
import json

# Path: sceneConstructorPackage/python/sceneConstructorPackage/utils/shotLoaderUI.py
from ...core.data_manager import DataManager 

class ShotLoaderUI(object):
    def __init__(self):
        # ❌ Hardcoded paths removed
        self.data_manager = DataManager()
        self.window = "shotLoader"
        
        self.build_ui()
        self.load_scenes()

    def build_ui(self):
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window)

        cmds.window(self.window, title="Shot Loader", widthHeight=(300, 100))

        main_layout = cmds.rowLayout(
            numberOfColumns=3,
            adjustableColumn=1,
            columnAttach3=('both', 'both', 'both')
        )

        # scene selection column
        cmds.columnLayout(adjustableColumn=True)
        cmds.text(label='Scene')
        # We reuse the dropdown names from the original file for the cmds API
        self.scene_dropdown = cmds.optionMenu(changeCommand=self.scene_changed) 
        cmds.setParent(main_layout)  

        # shot selection column
        cmds.columnLayout(adjustableColumn=True)
        cmds.text(label='Shot')
        self.shot_dropdown = cmds.optionMenu()
        cmds.setParent(main_layout)

        # load button column
        cmds.columnLayout(adjustableColumn=True)
        cmds.text(label='')
        cmds.button(label='Load Shot', command=self.import_actors)
        cmds.setParent('..')

        cmds.showWindow(self.window)

    def load_scenes(self):
        # 🆕 Use DataManager
        scene_files = self.data_manager.get_scenes()
        scene_files.sort()

        items = cmds.optionMenu(self.scene_dropdown, q=True, itemListLong=True)
        if items:
            for item in items:
                cmds.deleteUI(item)

        for scene in scene_files:
            cmds.menuItem(label=scene, parent=self.scene_dropdown)

        current_scene = cmds.optionMenu(self.scene_dropdown, q=True, value=True)
        self.load_shots_in_scenes(current_scene)

    def scene_changed(self, current_scene, *args):
        print("Scene changed to:", current_scene)
        self.load_shots_in_scenes(current_scene)

    def load_shots_in_scenes(self, current_scene):
        # 🆕 Use DataManager
        shotList = self.data_manager.get_shots_in_scene(current_scene)
        shotList.sort()

        items = cmds.optionMenu(self.shot_dropdown, q=True, itemListLong=True)
        if items:
            for item in items:
                cmds.deleteUI(item)
        
        for s in shotList:
            cmds.menuItem(label=s, parent=self.shot_dropdown)

    def import_actors(self, *args):
        """
        Loads the shot JSON and imports all assets into the current Maya scene.
        """
        current_selected_scene = cmds.optionMenu(self.scene_dropdown, q=True, value=True)
        current_selected_shot = cmds.optionMenu(self.shot_dropdown, q=True, value=True)

        if not current_selected_scene or not current_selected_shot:
            cmds.warning("Please select a Scene and a Shot.")
            return

        # 🆕 Use DataManager to load the shot data
        _, shot_data_dict = self.data_manager.load_shot_data(
            current_selected_scene, current_selected_shot
        )

        if not shot_data_dict:
            cmds.warning(f"Could not load data for shot: {current_selected_shot}")
            return

        shot_items = shot_data_dict.get(current_selected_shot.casefold(), [])

        for item in shot_items:
            path_to_import = item.get("path")
            actor_name = item.get("name", "UnknownActor")
            actor_type = item.get("type", "asset")

            if not path_to_import:
                print(f"[WARN] Actor {actor_name} is missing a path. Skipping.")
                continue

            # 1. Determine Maya File Type and Namespace
            file_type = "file" 
            if path_to_import.lower().endswith(('.usd', '.usda', '.usdc')):
                file_type = "USD Import"
            # Add other format detection here (e.g., .fbx, .obj)

            namespace = f"{current_selected_shot}_{actor_name}"
            
            # 2. Execute the Maya import command
            try:
                cmds.file(
                    path_to_import,
                    i=True, 
                    type=file_type,
                    ignoreVersion=True,
                    mergeNamespacesOnClash=False,
                    namespace=namespace,
                    options="v=0;p=17;f=0" 
                )
                print(f"[SUCCESS] Imported {actor_name} into namespace {namespace}")
            except Exception as e:
                print(f"[ERROR] Failed to import {actor_name} from {path_to_import}: {e}")