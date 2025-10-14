# Path: sceneConstructorPackage/python/sceneConstructorPackage/ui/sceneConstructorUI.py

# ... (imports: QtCore, QtGui, QtWidgets, json, os, Path)
# IMPORTANT: Updated imports to use new core modules
from ...core.data_manager import DataManager 
from ..utils.file_utils import open_file_explorer

class sceneConstructor(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(sceneConstructor, self).__init__(parent)
        self.setWindowTitle('Scene Constructor')
        self.resize(1000, 600)

        # 🆕 Initialize DataManager
        self.data_manager = DataManager()
        self.shot_data = {} # Cache for current shot's data
        self.shot_json_path = "" # Path to the current shot's JSON file

        # ... (Styling and LAYOUT remains the same)

        # ... (Setup UI components like preset_table, shot_table, dropdowns)
        
        # --- Load data (updated to use DataManager) ----
        self.load_presets()
        self.load_scenes()
        # self.currentScene is set in load_scenes
        self.scene_dropdown.currentTextChanged.connect(self.load_shots_in_scenes)
        self.shot_dropdown.currentTextChanged.connect(self.show_shot_items)

    def load_presets(self):
        """Loads data from DataManager and populates the preset_table."""
        data = self.data_manager.load_actors()
        self._populate_tree_widget(data, self.preset_table)

    def _populate_tree_widget(self, data, tree_widget):
        """Helper to populate a QTreeWidget from Actor data."""
        # Clear existing actors, but keep top-level type items
        for i in range(tree_widget.topLevelItemCount()):
            tree_widget.topLevelItem(i).takeChildren()
            
        for item in data:
            if item['type'] in self.actor_types:
                parent_item = None
                for i in range(tree_widget.topLevelItemCount()):
                    top = tree_widget.topLevelItem(i)
                    if top.text(0) == item['type']:
                        parent_item = top
                        break
                if not parent_item: continue
                
                # ... (code to create name, path, and shot children remains the same)
                name = item['name']
                child = QtWidgets.QTreeWidgetItem([name])
                child.setFlags(child.flags() | QtCore.Qt.ItemIsEditable)
                parent_item.addChild(child)

                path = item['path']
                path_child = QtWidgets.QTreeWidgetItem(["path", path])
                path_child.setFlags(path_child.flags() | QtCore.Qt.ItemIsEditable)
                child.addChild(path_child)

                if item['type'] == "camera" and "shot" in item:
                    shot_item = QtWidgets.QTreeWidgetItem(["shot", item["shot"]])
                    shot_item.setFlags(shot_item.flags() | QtCore.Qt.ItemIsEditable)
                    child.addChild(shot_item)


    def load_scenes(self):
        """Populates the Scene dropdown using DataManager."""
        self.scene_dropdown.clear()
        scene_files = self.data_manager.get_scenes()
        self.scene_dropdown.addItems(scene_files)
        self.currentScene = self.scene_dropdown.currentText()
        self.load_shots_in_scenes(self.currentScene)

    def load_shots_in_scenes(self, scene):
        """Populates the Shot dropdown using DataManager."""
        self.shot_dropdown.clear()
        shotList = self.data_manager.get_shots_in_scene(scene)
        self.shot_dropdown.addItems(shotList)
        # Manually trigger to load items for the first shot
        self.show_shot_items(self.shot_dropdown.currentText()) 

    def show_shot_items(self, shot_name):
        """Loads a shot's data and populates the shot_table."""
        self.currentScene = self.scene_dropdown.currentText()
        if not self.currentScene or not shot_name:
            # Clear all shot children if no selection
            for i in range(self.shot_table.topLevelItemCount()):
                self.shot_table.topLevelItem(i).takeChildren()
            return
            
        # 🆕 Use DataManager to load data
        self.shot_json_path, self.shot_data = self.data_manager.load_shot_data(self.currentScene, shot_name)
        
        # Clear current tree before adding
        for i in range(self.shot_table.topLevelItemCount()):
            self.shot_table.topLevelItem(i).takeChildren()

        shot_items = self.shot_data.get(shot_name.casefold(), [])
        self._populate_tree_widget(shot_items, self.shot_table)
        
    def save_presets_to_json(self):
        """Converts preset_table to data structure and saves via DataManager."""
        output_data = []
        for i in range(self.preset_table.topLevelItemCount()):
            type_item = self.preset_table.topLevelItem(i)
            preset_type = type_item.text(0)
            
            for j in range(type_item.childCount()):
                name_item = type_item.child(j)
                name = name_item.text(0)
                entry = {"type": preset_type, "name": name}

                for k in range(name_item.childCount()):
                    attr_item = name_item.child(k)
                    key = attr_item.text(0)
                    val = attr_item.text(1)
                    entry[key] = val
                
                output_data.append(entry)
        
        # 🆕 Save using DataManager
        self.data_manager.save_actors(output_data)

    def save_shots(self):
        """Converts shot_table to data structure and saves via DataManager."""
        output_data = []
        for i in range(self.shot_table.topLevelItemCount()):
            # ... (Logic to traverse tree and build output_data is the same)
            # ...
            type_item = self.shot_table.topLevelItem(i)
            preset_type = type_item.text(0)
            
            for j in range(type_item.childCount()):
                name_item = type_item.child(j)
                name = name_item.text(0)
                entry = {"type": preset_type, "name": name}

                for k in range(name_item.childCount()):
                    attr_item = name_item.child(k)
                    key = attr_item.text(0)
                    val = attr_item.text(1)
                    entry[key] = val
                
                output_data.append(entry)

        currentShot = self.shot_dropdown.currentText()

        if not self.shot_json_path:
             print("[ERROR] Cannot save shot: Shot JSON path is not defined.")
             return

        # Update the shot_data dictionary for the current shot
        self.shot_data[currentShot.casefold()] = output_data

        # 🆕 Save using DataManager
        self.data_manager.save_shot_data(self.shot_json_path, self.shot_data)

    # ... (open_context_menu_presets and open_context_menu_shots remain similar)

    def open_actor_triggered(self, action, open_action, item):
        """Uses file_utils to open the file path."""
        if action == open_action:
            filePath = item.text(1)
            if item.text(0).lower() == "path":
                open_file_explorer(filePath)

    # 🆕 Crucial update: Call save_presets_to_json after deletion
    def delete_actor_triggered(self, action, delete_action, item, index):
        if action == delete_action:
            if item is not None:
                top_level_item = item
                while top_level_item.parent():
                    top_level_item = top_level_item.parent()

            top_level_item.takeChild(index.row())
            
            # --- PERSIST CHANGE ---
            if item.treeWidget() == self.preset_table:
                self.save_presets_to_json() 
            elif item.treeWidget() == self.shot_table:
                self.save_shots()