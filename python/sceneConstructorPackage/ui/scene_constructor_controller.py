# Path: python/sceneConstructorPackage/ui/scene_constructor_controller.py

import json
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui
from sceneConstructorPackage.ui.sceneConstructorUI import sceneConstructor
from sceneConstructorPackage.ui.scene_constructor_model import SceneConstructorModel

class SceneConstructorController:
    """
    The Controller linking the View (sceneConstructor) 
    and the Model (SceneConstructorModel).
    """
    def __init__(self):
        self.model = SceneConstructorModel()
        self.view = sceneConstructor()

        self._connect_signals()

    def run(self):
        """Show the view and load initial data."""
        self.view.show()
        # Trigger initial data load
        self.model.load_actors()
        self.model.load_scenes() 

    def _connect_signals(self):
        """Connect signals from View to Controller slots, and Model to View slots."""
        
        # --- View -> Controller ---
        self.view.publishShotsClicked.connect(self.on_save_shots)
        self.view.sceneSelected.connect(self.model.set_current_scene)
        self.view.shotSelected.connect(self.model.set_current_shot)
        
        self.view.transferClicked.connect(self.on_transfer_actors)
        self.view.openPathRequested.connect(self.view.open_path_in_explorer)
        self.view.editItemRequested.connect(self.view.start_item_edit)
        
        self.view.deleteShotAssetRequested.connect(self.on_delete_shot_asset)
        self.view.actorSelected.connect(self.on_actor_selected)
        
        self.view.shotVersionChanged.connect(self.on_shot_version_changed)

        # --- NEW CONNECTION ---
        self.view.chooseVersionRequested.connect(self.on_choose_version)

        # --- Model -> View ---
        self.model.actorsReloaded.connect(self.view.update_actor_tree)
        self.model.scenesReloaded.connect(self.on_scenes_reloaded)
        self.model.shotsReloaded.connect(self.on_shots_reloaded)
        self.model.shotDataLoaded.connect(self.on_shot_data_loaded)
        
        self.model.versionUpdateFailed.connect(self.view.show_error_message)

        
    # --- Controller Slots (Handling View Signals) ---

    def on_save_shots(self):
        """Get data from shot tree and tell model to save."""
        shot_data = self.view.get_all_data_from_tree(self.view.shot_table)
        self.model.save_shot_data(shot_data)

    def on_transfer_actors(self, assets_to_transfer: list):
        """Adds selected assets to the current shot data and updates the view."""
        shot_key = self.model.current_shot_name.casefold()
        current_shot_items = self.model.current_shot_data_cache.get(shot_key, [])
        
        existing_ids = set()
        for item in current_shot_items:
            existing_ids.add( (item.get('name'), item.get('department')) )

        for asset_data in assets_to_transfer:
            asset_id = (asset_data.get('name'), asset_data.get('department'))
            if asset_id not in existing_ids:
                current_shot_items.append(asset_data.copy()) # Add a copy
        
        self.model.current_shot_data_cache[shot_key] = current_shot_items
        self.view.update_shot_tree(self.model.current_shot_data_cache, self.model.current_shot_name)

    def on_delete_shot_asset(self, item: QtWidgets.QTreeWidgetItem):
        """Removes an asset (a department item) from the shot tree."""
        (item.parent() or self.view.shot_table.invisibleRootItem()).removeChild(item)
        self.on_save_shots() # Persist the change

    @QtCore.Slot(dict)
    def on_actor_selected(self, actor_data: dict):
        """Called when an actor is selected in the View. Loads and displays metadata."""
        
        if not actor_data or actor_data.get("is_group"):
            self.view.update_snapshot(QtGui.QPixmap()) # Send null pixmap
            self.view.update_actor_notes("")
            return

        snapshot_path = actor_data.get('snapshot')

        notes_list = []
        publish_note = actor_data.get('note')
        if publish_note:
            notes_list.append(f"Publish Note:\n{publish_note}")
        
        other_metadata = []
        excluded_keys = ['type', 'name', 'department', 'snapshot', 'path', 'version', 'note', 'is_group']
        
        for key, val in actor_data.items():
            if key not in excluded_keys:
                pretty_key = key.replace('_', ' ').capitalize()
                other_metadata.append(f"{pretty_key}: {val}")
        
        if other_metadata:
            notes_list.append("Additional Metadata:\n" + "\n".join(other_metadata))

        if not notes_list:
            note_text = "No notes available."
        else:
            note_text = "\n\n".join(notes_list)

        # 1. Load Snapshot
        pixmap = QtGui.QPixmap()
        if snapshot_path and Path(snapshot_path).exists():
            pixmap.load(snapshot_path)
        self.view.update_snapshot(pixmap)

        # 2. Load Notes
        self.view.update_actor_notes(note_text)

    @QtCore.Slot(QtWidgets.QTreeWidgetItem, str)
    def on_shot_version_changed(self, version_item, new_version_str):
        """
        Called when the user edits a version in the shot list.
        Tells the Model to validate it and updates the View.
        """
        dept_item = version_item.parent()
        if not dept_item: return
        
        actor_data = dept_item.data(0, QtCore.Qt.UserRole)
        if not actor_data: return
            
        asset_name = actor_data.get('name')
        department = actor_data.get('department')
        old_version = actor_data.get('version')
        
        if new_version_str == old_version:
            return

        # 1. Ask the Model to find this new version
        new_data = self.model.get_new_version_data(
            asset_name, department, new_version_str
        )
        
        # 2. Update the View based on the result
        if new_data:
            # SUCCESS
            self.view.update_shot_item_version(version_item, new_data)
            self.on_save_shots() # Auto-save the change
        else:
            # FAILED
            self.view.revert_shot_item_version(version_item, old_version)

    # --- NEW SLOT ---
    @QtCore.Slot(QtWidgets.QTreeWidgetItem)
    def on_choose_version(self, version_item: QtWidgets.QTreeWidgetItem):
        """
        Called when "Choose Version" is clicked in either tree.
        Fetches all versions and shows a selection dialog.
        """
        dept_item = version_item.parent()
        if not dept_item:
            return
            
        actor_data = dept_item.data(0, QtCore.Qt.UserRole)
        if not actor_data or actor_data.get("is_group"):
            return
            
        asset_name = actor_data.get('name')
        department = actor_data.get('department')
        
        if not asset_name or not department:
            return
            
        #get all available versions from the Model
        all_versions = self.model.get_all_versions(asset_name, department)
        if not all_versions:
            self.view.show_error_message(f"No other versions found for {asset_name} {department}.")
            return
            
        all_versions.sort(reverse=True) # Show newest first
        
        current_version = version_item.text(1)
        
        #show the dialog
        new_version_str, ok = QtWidgets.QInputDialog.getItem(
            self.view,
            "Choose Version",
            f"Select version for {asset_name} {department}:",
            all_versions,
            0, # Default to the first item (newest)
            False # List is not editable
        )
        
        #handle the result
        if not ok or new_version_str == current_version:
            return #user cancelled or didn't change the version
            
        #decide which tree to update
        tree_widget = version_item.treeWidget()
        
        if tree_widget == self.view.shot_table:
            # Right-side tree: Use the existing logic to update and save
            self.on_shot_version_changed(version_item, new_version_str)
            
        elif tree_widget == self.view.preset_table:
            # Left-side tree: Just update the view, don't save
            new_data = self.model.get_new_version_data(asset_name, department, new_version_str)
            if new_data:
                self.view.update_asset_item_version(version_item, new_data)
            else:
                # This should be rare since we got the version from the list
                self.view.show_error_message(f"Could not load data for {new_version_str}")

    # --- Controller Slots (Handling Model Signals) ---
    
    def on_scenes_reloaded(self, scenes: list):
        self.view.update_scene_dropdown(scenes)
        if scenes:
            self.view.set_scene_dropdown(scenes[0])
            
    def on_shots_reloaded(self, shots: list):
        self.view.update_shot_dropdown(shots)
        if shots:
            self.view.set_shot_dropdown(shots[0])
        else:
            self.view.update_shot_tree({}, "")

    def on_shot_data_loaded(self, json_path: str, shot_data: dict):
        self.view.update_shot_tree(shot_data, self.model.current_shot_name)