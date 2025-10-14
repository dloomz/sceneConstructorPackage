import sys
import os
import json
from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets
from shiboken6 import wrapInstance

# Path: sceneConstructorPackage/python/sceneConstructorPackage/ui/sceneConstructorUI.py
from ...core.data_manager import DataManager 
from ..utils.fileUtils import open_in_native_explorer # 🆕 Renamed import

# -------- Scene Constructor UI --------
class sceneConstructor(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(sceneConstructor, self).__init__(parent)
        self.setWindowTitle('Scene Constructor')
        self.resize(1000, 600)

        # 🆕 Initialize DataManager and path variables
        self.data_manager = DataManager()
        self.shot_data = {} # Cache for current shot's data
        self.shot_json_path = "" # Path to the current shot's JSON file

        self.position = QtCore.QPointF(0, 0)

        # --- Styling (omitted for brevity, remains the same) ---
        self.setStyleSheet("""...""")

        # ========== Layout ==========
        main_layout = QtWidgets.QHBoxLayout(self)

        # ---- Left column (Actors) ----
        preset_layout = QtWidgets.QVBoxLayout()
        preset_label = QtWidgets.QLabel('Actors')

        self.preset_table = QtWidgets.QTreeWidget()
        self.preset_table.setHeaderLabels(['Preset', 'Value'])
        self.preset_table.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.preset_table.header().setStretchLastSection(True)
        self.preset_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.preset_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.preset_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.preset_table.customContextMenuRequested.connect(
            lambda pos: self.open_context_menu_presets(self.preset_table, pos)
        )

        self.actor_types = ['camera', 'character', 'prop', 'set']
        for types in self.actor_types:
            typeGroup = QtWidgets.QTreeWidgetItem([types])
            self.preset_table.addTopLevelItem(typeGroup)

        self.actorButton = QtWidgets.QPushButton('Publish Actors')
        self.actorButton.clicked.connect(self.save_presets_to_json)

        preset_layout.addWidget(preset_label)
        preset_layout.addWidget(self.preset_table)
        preset_layout.addWidget(self.actorButton)

        # ---- Right column (Shots) ----
        shot_layout = QtWidgets.QVBoxLayout()
        shot_label = QtWidgets.QLabel('Construct')

        self.shot_table = QtWidgets.QTreeWidget()
        self.shot_table.setHeaderLabels(['Preset', 'Value'])
        self.shot_table.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.shot_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.shot_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.shot_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.shot_table.customContextMenuRequested.connect(
            lambda pos: self.open_context_menu_shots(self.shot_table, pos)
        )

        for types in self.actor_types:
            typeGroup = QtWidgets.QTreeWidgetItem([types])
            self.shot_table.addTopLevelItem(typeGroup)

        sceneSel_layout = QtWidgets.QHBoxLayout()
        sceneSel_label = QtWidgets.QLabel('Select Scene:')
        self.construct_scene_dropdown = QtWidgets.QComboBox() # 🆕 Renamed
        sceneSel_layout.addWidget(sceneSel_label)
        sceneSel_layout.addWidget(self.construct_scene_dropdown)

        shotSel_layout = QtWidgets.QHBoxLayout()
        shotSel_label = QtWidgets.QLabel('Select Shot:')
        self.construct_shot_dropdown = QtWidgets.QComboBox() # 🆕 Renamed
        shotSel_layout.addWidget(shotSel_label)
        shotSel_layout.addWidget(self.construct_shot_dropdown)

        self.shotButton = QtWidgets.QPushButton('Publish Shots')
        self.shotButton.clicked.connect(self.save_shots)

        shot_layout.addWidget(shot_label)
        shot_layout.addLayout(sceneSel_layout)
        shot_layout.addLayout(shotSel_layout)
        shot_layout.addWidget(self.shot_table)
        shot_layout.addWidget(self.shotButton)

        # ---- Transfer button ----
        transfer_layout = QtWidgets.QVBoxLayout()
        self.transferButton = QtWidgets.QPushButton('->')
        transfer_layout.addWidget(self.transferButton)
        self.transferButton.clicked.connect(self.add_actor_to_shot)

        # ---- Main layout assembly ----
        main_layout.addLayout(preset_layout)
        main_layout.addLayout(transfer_layout)
        main_layout.addLayout(shot_layout)
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 0.25)
        main_layout.setStretch(2, 1)

        # ---- Load data ----
        self.load_presets()
        self.load_scenes()
        
        # Connect to the new dropdown names
        self.construct_scene_dropdown.currentTextChanged.connect(self.load_shots_in_scenes)
        self.construct_shot_dropdown.currentTextChanged.connect(self.show_shot_items)

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

    def open_context_menu_presets(self, widget, position):
        item = widget.itemAt(position)
        index = widget.indexAt(position)
        if not item: return
        menu = QtWidgets.QMenu(widget)
        edit_action = menu.addAction("Edit")
        if item.text(0) == "path": open_action = menu.addAction("Open")
        delete_action = menu.addAction("Delete")
        action = menu.exec_(widget.viewport().mapToGlobal(position))
        edit_action.triggered.connect(lambda: self.edit_actor_triggered(action, edit_action, item, widget))
        if item.text(0) == "path": open_action.triggered.connect(lambda: self.open_actor_triggered(action, open_action, item))
        delete_action.triggered.connect(lambda: self.delete_actor_triggered(action, delete_action, item, index))

    def edit_actor_triggered(self, action, edit_action, item, widget):
        if action == edit_action:
            label = item.text(0).lower()
            if label in ("path", "shot", "type") and item.columnCount() > 1:
                widget.editItem(item, 1)
            else:
                widget.editItem(item, 0)
            
            # Note: A signal listener on item changed would be better, 
            # but for simplicity, we rely on publish/delete buttons for permanent saves.

    def open_actor_triggered(self, action, open_action, item):
        if action == open_action:
            filePath = item.text(1)
            if item.text(0).lower() == "path":
                open_in_native_explorer(filePath) # 🆕 Renamed function
                
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
        
        self.data_manager.save_actors(output_data)

    def add_actor_to_shot(self):
        selectedActors = self.preset_table.selectedItems()

        for actor in selectedActors:
            if actor.parent() is None: continue

            def clone_actor(actor):
                new_actor = QtWidgets.QTreeWidgetItem([actor.text(i) for i in range(actor.columnCount())])
                for c in range(actor.childCount()):
                    new_actor.addChild(clone_actor(actor.child(c)))
                return new_actor

            actorCopy = clone_actor(actor)
            parent_item = None

            for i in range(self.shot_table.topLevelItemCount()):
                top_item = self.shot_table.topLevelItem(i)
                if top_item.text(0) == actor.parent().text(0):
                    parent_item = top_item
                    break

            if parent_item:
                parent_item.addChild(actorCopy)     

    def load_scenes(self):
        """Populates the Scene dropdown using DataManager."""
        self.construct_scene_dropdown.clear() # 🆕 Use new name
        scene_files = self.data_manager.get_scenes()
        self.construct_scene_dropdown.addItems(scene_files) # 🆕 Use new name
        self.currentScene = self.construct_scene_dropdown.currentText() # 🆕 Use new name
        self.load_shots_in_scenes(self.currentScene)

    def load_shots_in_scenes(self, scene):
        """Populates the Shot dropdown using DataManager."""
        self.construct_shot_dropdown.clear() # 🆕 Use new name
        shotList = self.data_manager.get_shots_in_scene(scene)
        self.construct_shot_dropdown.addItems(shotList) # 🆕 Use new name
        # Manually trigger to load items for the first shot
        self.show_shot_items(self.construct_shot_dropdown.currentText()) 
        
    def show_shot_items(self, shot_name):
        """Loads a shot's data and populates the shot_table."""
        self.currentScene = self.construct_scene_dropdown.currentText() # 🆕 Use new name
        if not self.currentScene or not shot_name:
            for i in range(self.shot_table.topLevelItemCount()):
                self.shot_table.topLevelItem(i).takeChildren()
            return
            
        # 🆕 Use DataManager to load data
        self.shot_json_path, self.shot_data = self.data_manager.load_shot_data(self.currentScene, shot_name)
        
        for i in range(self.shot_table.topLevelItemCount()):
            self.shot_table.topLevelItem(i).takeChildren()

        shot_items = self.shot_data.get(shot_name.casefold(), [])
        self._populate_tree_widget(shot_items, self.shot_table)

    def save_shots(self):
        """Converts shot_table to data structure and saves via DataManager."""
        output_data = []
        for i in range(self.shot_table.topLevelItemCount()):
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

        currentShot = self.construct_shot_dropdown.currentText() # 🆕 Use new name

        if not self.shot_json_path:
             # Default path generation if it was previously empty
             self.shot_json_path, _ = self.data_manager.load_shot_data(self.currentScene, currentShot)
             if not self.shot_json_path:
                 print("[ERROR] Cannot save shot: Shot JSON path could not be generated.")
                 return

        # Ensure the shot name is in the data dictionary for saving
        self.shot_data[currentShot.casefold()] = output_data

        self.data_manager.save_shot_data(self.shot_json_path, self.shot_data)

    def open_context_menu_shots(self, widget, position):
        item = widget.itemAt(position)
        index = widget.indexAt(position)
        if not item: return

        menu = QtWidgets.QMenu(widget)
        if item.text(0) == "path": open_action = menu.addAction("Open")
        delete_action = menu.addAction("Delete")
        action = menu.exec_(widget.viewport().mapToGlobal(position))

        if item.text(0) == "path":
            open_action.triggered.connect(lambda: self.open_actor_triggered(action, open_action, item))
        delete_action.triggered.connect(lambda: self.delete_actor_triggered(action, delete_action, item, index))