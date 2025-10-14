# Path: sceneConstructorPackage/python/sceneConstructorPackage/ui/saveActorUI.py

# ... (imports)
from PySide6 import QtWidgets, QtCore, QtGui
import maya.cmds as cmds
# IMPORTANT: Updated imports to use new core modules
from ...core.data_manager import DataManager 
from .... import config
# ... (close existing window block)

class ShotLoaderUI(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(ShotLoaderUI, self).__init__(parent)

        self.setObjectName("ActorPublishWindow")
        self.data_manager = DataManager()
        
        # 🆕 Use config paths
        self.authors_json_path = str(config.AUTHORS_ROOT)
        # Note: scene_path here should be where final USD/meta.json goes (e.g., assets folder)
        self.scene_path = r'C:\Users\Dolapo\Desktop\python\static\30_assets' # Placeholder

        self.setWindowTitle("Actor Publish")
        # ... (other setup)
        
    def build_ui(self):
        # ... (Existing build_ui code)

        # ------------------
        # TAB 2: NEW ACTOR (Updated to include Name and Type)
        # ------------------
        new_tab = QtWidgets.QWidget()
        new_layout = QtWidgets.QVBoxLayout(new_tab)

        # 🆕 NEW ACTOR NAME AND TYPE ROW
        name_type_row = QtWidgets.QHBoxLayout()
        name_label = QtWidgets.QLabel("Actor Name:")
        self.actor_name_line = QtWidgets.QLineEdit()
        type_label = QtWidgets.QLabel("Actor Type:")
        self.actor_type_dropdown = QtWidgets.QComboBox()
        self.actor_type_dropdown.addItems(['character', 'prop', 'set', 'camera'])

        name_type_row.addWidget(name_label)
        name_type_row.addWidget(self.actor_name_line, 1)
        name_type_row.addWidget(type_label)
        name_type_row.addWidget(self.actor_type_dropdown)
        
        # ... (author and version row remains the same)

        # Add new row to layout
        new_layout.addLayout(name_type_row)
        new_layout.addLayout(author_row)
        # ... (rest of new_layout widgets)

        # ... (rest of build_ui)

    def publish_action(self):
        # ... (Existing variable definitions: author, note, version_num, version_str)
        
        # 🆕 Get Actor Name and Type
        actor_name = self.actor_name_line.text().strip()
        actor_type = self.actor_type_dropdown.currentText()
        
        if not actor_name:
            QtWidgets.QMessageBox.warning(self, "Publish Error", "Please enter an Actor Name.")
            return

        # create version folder
        output_dir = os.path.join(self.scene_path, actor_name, version_str) # Organized by Actor Name
        os.makedirs(output_dir, exist_ok=True)

        # ... (save snapshot and export USD logic remains the same)
        
        # --- WRITE METADATA JSON ---
        meta = {
            # ... (metadata fields)
            "path": output_dir # Path to the published version folder
        }
        json_path = os.path.join(output_dir, f"{version_str}_meta.json")
        with open(json_path, 'w') as f:
            json.dump(meta, f, indent=4)
            
        # --- 🆕 UPDATE GLOBAL ACTORS JSON ---
        # 1. Load current actors list
        all_actors = self.data_manager.load_actors()
        
        # 2. Create the entry for the new/updated actor
        new_actor_entry = {
            "type": actor_type,
            "name": actor_name,
            "path": os.path.join(output_dir, f"{version_str}_geo.usd"), # Point to the USD file
            # Add other attributes here if needed (e.g., "latest_version": version_str)
        }
        
        # 3. Find and replace old entry, or append
        updated = False
        for i, actor in enumerate(all_actors):
            if actor.get("name") == actor_name:
                all_actors[i] = new_actor_entry
                updated = True
                break
        
        if not updated:
            all_actors.append(new_actor_entry)
            
        # 4. Save back to global actors.json
        self.data_manager.save_actors(all_actors)

        # ... (Show message box and bump version)