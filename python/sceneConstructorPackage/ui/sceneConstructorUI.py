#!/usr/bin/env python

from plcore.ui.qt.compatibility import QtCore, QtGui, QtWidgets, wrapInstance
import json
import os
from pathlib import Path

#super function
class sceneConstructor(QtWidgets.QWidget):
    #setting main function in class, self is class terminology
    #parent = determines if window is child
    def __init__(self, parent=None):
        super(sceneConstructor, self).__init__(parent)
        self.setWindowTitle('Scene Constructor')
        self.resize(1000, 600)

        self.json_path = '/job/pipeline/dev/sandbox/sandbox_dokuboyejo/work/dokuboyejo/scripts/SceneConstructor/actors.json'

        self.shot_path = '/job/pipeline/dev/sandbox/sandbox_dokuboyejo/work/dokuboyejo/scripts/SceneConstructor/shots.json'

        self.scene_path = '/job/pipeline/dev/sandbox/sandbox_dokuboyejo/work/dokuboyejo/scripts/SceneConstructor/testFilm/25_footage/scene'

        self.position = QtCore.QPointF(0,0)

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12pt;
            }
            QLabel {
                color: #ff99cc;
                font-weight: bold;
                padding: 4px;
            }
            QTableWidget, QTreeWidget {
                background-color: #2d2d2d;
                border: 1px solid #444;
                selection-background-color: #ff99cc;
                selection-color: #ffffff;
            }
            QHeaderView::section {
                background-color: #3c3c3c;
                color: #ffffff;
                padding: 4px;
                border: 1px solid #444;
            }
            QPushButton {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px 12px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #ff99cc;
                border: 1px solid #ff99cc;
            }
        """)

        #LAYOUT
        main_layout = QtWidgets.QHBoxLayout(self)
        #setting variable at the end to save repetition

        #left column
        preset_layout = QtWidgets.QVBoxLayout()
        preset_label = QtWidgets.QLabel('Actors')

        self.preset_table = QtWidgets.QTreeWidget()
        self.preset_table.setHeaderLabels(['Preset', 'Value'])
        self.preset_table.header().setSectionResizeMode(0 , QtWidgets.QHeaderView.ResizeToContents)
        self.preset_table.header().setStretchLastSection(True)
        self.preset_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.preset_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.preset_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.preset_table.customContextMenuRequested.connect(lambda pos: self.open_context_menu_presets(self.preset_table, pos))

        #create type categories to sort actors with here
        self.actor_types = ['camera', 'character','prop', 'set']

        for types in self.actor_types:
            typeGroup = QtWidgets.QTreeWidgetItem([types])
            self.main_preset_parents = self.preset_table.addTopLevelItem(typeGroup)

        self.actorButton = QtWidgets.QPushButton('Publish Actors')
        self.actorButton.clicked.connect(self.save_presets_to_json)

        #context-menu (right click)
        # self.preset_table.installEventFilter(self)

        #putting left side all together
        preset_layout.addWidget(preset_label)
        preset_layout.addWidget(self.preset_table)
        preset_layout.addWidget(self.actorButton)

        #right column
        shot_layout = QtWidgets.QVBoxLayout()
        shot_label = QtWidgets.QLabel('Construct')

        self.shot_table = QtWidgets.QTreeWidget()
        self.shot_table.setHeaderLabels(['Preset', 'Value'])
        self.shot_table.header().setSectionResizeMode(0 , QtWidgets.QHeaderView.ResizeToContents)
        self.shot_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.shot_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.shot_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.shot_table.customContextMenuRequested.connect(lambda pos: self.open_context_menu_shots(self.shot_table, pos))

        for types in self.actor_types:
            typeGroup = QtWidgets.QTreeWidgetItem([types])
            self.main_shot_parents = self.shot_table.addTopLevelItem(typeGroup)

        sceneSel_layout = QtWidgets.QHBoxLayout()
        sceneSel_label = QtWidgets.QLabel('Select Scene:')
        self.scene_dropdown = QtWidgets.QComboBox()
        sceneSel_layout.addWidget(sceneSel_label)
        sceneSel_layout.addWidget(self.scene_dropdown)

        shotSel_layout = QtWidgets.QHBoxLayout()
        shotSel_label = QtWidgets.QLabel('Select Shot:')
        self.shot_dropdown = QtWidgets.QComboBox()
        shotSel_layout.addWidget(shotSel_label)
        shotSel_layout.addWidget(self.shot_dropdown)
        # self.shot_dropdown.addItems(['shot1','shot2','shot3'])

        self.shotButton = QtWidgets.QPushButton('Publish Shots')
        self.shotButton.clicked.connect(self.save_shots)

        shot_layout.addWidget(shot_label)
        # shot_layout.addWidget(self.shot_dropdown)
        shot_layout.addLayout(sceneSel_layout)
        shot_layout.addLayout(shotSel_layout)
        shot_layout.addWidget(self.shot_table)
        shot_layout.addWidget(self.shotButton)

        #middle transfer button
        transfer_layout = QtWidgets.QVBoxLayout()
        self.transferButton = QtWidgets.QPushButton('->')
        transfer_layout.addWidget(self.transferButton)

        self.transferButton.clicked.connect(self.add_actor_to_shot)

        #main window with both columns
        main_layout.addLayout(preset_layout)
        main_layout.addLayout(transfer_layout)
        main_layout.addLayout(shot_layout)
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 0.25)
        main_layout.setStretch(2, 1)

        self.load_presets_from_json(self.json_path)
        # self.load_shots(self.shot_path)
        self.load_scenes(self.scene_path)

    def load_presets_from_json(self, json_path):
    # load JSON file
        with open(json_path) as f:
            data = json.load(f)

        for item in data:

            if item['type'] in self.actor_types:
                # find the top-level item that matches the type name
                parent_item = None
                for i in range(self.preset_table.topLevelItemCount()):
                    self.preset_top_item = self.preset_table.topLevelItem(i)
                    if self.preset_top_item.text(0) == item['type']:
                        parent_item = self.preset_top_item
                        break

                if not parent_item:
                    # if not found, can skip or create it
                    continue

                #create the name child
                name = item['name']
                child = QtWidgets.QTreeWidgetItem([name])
                child.setFlags(child.flags() | QtCore.Qt.ItemIsEditable)
                parent_item.addChild(child)

                # path child
                path = item['path']
                path_child = QtWidgets.QTreeWidgetItem(["path", path])
                path_child.setFlags(path_child.flags() | QtCore.Qt.ItemIsEditable)
                child.addChild(path_child)

                # shot child (cameras only)
                if item['type'] == "camera" and "shot" in item:
                    shot_item = QtWidgets.QTreeWidgetItem(["shot", item["shot"]])
                    shot_item.setFlags(shot_item.flags() | QtCore.Qt.ItemIsEditable)
                    child.addChild(shot_item)

    def open_context_menu_presets(self, widget, position):
        #self.preset_table = QtWidgets.QTreeWidget()
        #widget = self.preset_table
        #item = QtWidgets.QTreeWidget.itemAt(position)
        item = widget.itemAt(position)
        index = widget.indexAt(position)
        if not item:
            return

        menu = QtWidgets.QMenu(widget)

        edit_action = menu.addAction("Edit")

        if item.text(0) == "path":
            open_action = menu.addAction("Open")

        delete_action = menu.addAction("Delete")

        action = menu.exec_(widget.viewport().mapToGlobal(position))

        edit_action.triggered.connect(self.edit_actor_triggered(action, edit_action, item, widget))

        if item.text(0) == "path":
            open_action.triggered.connect(self.open_actor_triggered(action, open_action, item))

        delete_action.triggered.connect(self.delete_actor_triggered(action, delete_action, item, index))       

    def edit_actor_triggered(self, action, edit_action, item, widget):
        if action == edit_action:
            label = item.text(0).lower()

            if label in ("path", "shot", "type") and item.columnCount() > 1:
                # Only edit value (column 1)
                widget.editItem(item, 1)
            else:
                # Edit label (Name or Type) in column 0
                widget.editItem(item, 0)
    
    def open_actor_triggered(self, action, open_action, item):

      if action == open_action:
            label = item.text(0).lower()
            filePath = item.text(1)

            command = f"caja {filePath}"

            if label in ("path") and item.columnCount() > 1:
                os.system(command)
                print(filePath)
            else:
                pass

    def delete_actor_triggered(self, action, delete_action, item, index):
        if action == delete_action:

            #while loop to get top most level that does not have a parent
            if item is not None:
                top_level_item = item
                while top_level_item.parent():
                    top_level_item = top_level_item.parent()

            #delete's the child of top
            top_level_item.takeChild(index.row())
            
    def save_presets_to_json(self):

        #sets output as an empty list
        output_data = []

        #going through each top level item
        for i in range(self.preset_table.topLevelItemCount()):
            type_item = self.preset_table.topLevelItem(i)
            #save out the actor type ie: camera, prop
            preset_type = type_item.text(0)

            #for children of each type, so the actual actors
            for j in range(type_item.childCount()):
                #store the name of the actor
                name_item = type_item.child(j)
                #get it as a string
                name = name_item.text(0)
                #save out dictionary with actor type and actor name
                entry = {"type": preset_type, "name": name}

                '''made iterable so it also saves shots'''
                #gets  children of actor so actor deets such as path
                for k in range(name_item.childCount()):
                    attr_item = name_item.child(k)
                    key = attr_item.text(0)
                    val = attr_item.text(1)

                    #removed hard-coding 
                    entry[key] = val

                    # if key == "path":l
                    #     entry["Path"] = val

                #add the created dictionaries to the list/data
                output_data.append(entry)

        try:
            #dump it into the json
            with open(self.json_path, "w") as f:
                json.dump(output_data, f, indent=4)
            print(f"[OK] Presets saved to {self.json_path}")
        except Exception as e:
            print(f"[ERROR] Could not save JSON: {e}")

    def add_actor_to_shot(self):
        selectedActors = self.preset_table.selectedItems()

        for actor in selectedActors:
            # skip if top-level item
            if actor.parent() is None:
                continue

            # copy actor and children func
            def clone_actor(actor):
                #copy text from all columns
                new_actor = QtWidgets.QTreeWidgetItem([actor.text(i) for i in range(actor.columnCount())])
                #for each child in selected copy those too
                for c in range(actor.childCount()):
                    new_actor.addChild(clone_actor(actor.child(c)))
                #output copied actor to add to shot_table
                return new_actor

            #actorCopy = new_actor
            actorCopy = clone_actor(actor)

            # find top-level item in shot_table matching the parent name
            parent_item = None

            #get top level
            for i in range(self.shot_table.topLevelItemCount()):
                top_item = self.shot_table.topLevelItem(i)
                #if the types are the same, that's the actor's parent
                if top_item.text(0) == actor.parent().text(0):
                    parent_item = top_item
                    break

            #if a parent item exists add the copy
            if parent_item:
                parent_item.addChild(actorCopy)     

    def load_scenes(self, scene_path):
        #get list of everthing in scene path
        scene_files = os.listdir(self.scene_path)

        #sort so scenes show in order
        scene_files.sort()

        #check if it's a folder and only then add to dropdown
        for scene in scene_files:
            if os.path.isdir(os.path.join(self.scene_path, scene)) == True:
                self.scene_dropdown.addItem(str(scene))

        self.currentScene = self.scene_dropdown.currentText()
        self.load_shots_in_scenes(self.currentScene)

        self.scene_dropdown.currentTextChanged.connect(self.load_shots_in_scenes)

    def load_shots_in_scenes(self, scene):

        self.shot_dropdown.clear()
        
        shot_file_path = os.path.join(self.scene_path, scene)
        shotList = os.listdir(shot_file_path)

        shotList.sort()

        for s in shotList:
            if os.path.isdir(shot_file_path) == True:
                self.shot_dropdown.addItem(str(s))
            
        self.show_shot_items(self.shot_dropdown.currentText())

        self.shot_dropdown.currentTextChanged.connect(self.show_shot_items)
        
    def show_shot_items(self, text):

        #text is current shot

        shot_dir = os.path.join(self.scene_path,self.currentScene,text,'SceneConstructor')

        print(shot_dir)
        pipeline_files = os.listdir(shot_dir)

        #clear current tree b4 adding except headers
        for i in range(self.shot_table.topLevelItemCount()):
            self.shot_table.topLevelItem(i).takeChildren()

        for file in pipeline_files:
            if os.path.isfile(os.path.join(shot_dir,file)) == True:
                if file.lower().endswith('.json'):
                    self.shot_json_path = os.path.join(shot_dir,file)
                    with open(self.shot_json_path) as f:
                        self.shot_data = json.load(f)

                    shot_items = self.shot_data[text.casefold()]  
                    print(shot_items)

                    for item in shot_items:

                        if item['type'] in self.actor_types:
                            # find the top-level item that matches the type name
                            parent_item = None
                            for i in range(self.shot_table.topLevelItemCount()):
                                self.shot_top_item = self.shot_table.topLevelItem(i)
                                if self.shot_top_item.text(0) == item['type']:
                                    parent_item = self.shot_top_item
                                    break

                            if not parent_item:
                                # if not found, can skip or create it
                                continue

                            #create the name child
                            name = item['name']
                            child = QtWidgets.QTreeWidgetItem([name])
                            child.setFlags(child.flags() | QtCore.Qt.ItemIsEditable)
                            parent_item.addChild(child)

                            # path child
                            path = item['path']
                            path_child = QtWidgets.QTreeWidgetItem(["path", path])
                            path_child.setFlags(path_child.flags() | QtCore.Qt.ItemIsEditable)
                            child.addChild(path_child)

                            # shot child (cameras only)
                            if item['type'] == "camera" and "shot" in item:
                                shot_item = QtWidgets.QTreeWidgetItem(["shot", item["shot"]])
                                shot_item.setFlags(shot_item.flags() | QtCore.Qt.ItemIsEditable)
                                child.addChild(shot_item)

    def save_shots(self):

        #sets output as an empty list
        output_data = []

        #going through each top level item
        for i in range(self.shot_table.topLevelItemCount()):
            type_item = self.shot_table.topLevelItem(i)
            #save out the actor type ie: camera, prop
            preset_type = type_item.text(0)

            #for children of each type, so the actual actors
            for j in range(type_item.childCount()):
                #store the name of the actor
                name_item = type_item.child(j)
                #get it as a string
                name = name_item.text(0)
                #save out dictionary with actor type and actor name
                entry = {"type": preset_type, "name": name}

                '''made iterable so it also saves shots'''
                #gets  children of actor so actor deets such as path
                for k in range(name_item.childCount()):
                    attr_item = name_item.child(k)
                    key = attr_item.text(0)
                    val = attr_item.text(1)

                    #removed hard-coding 
                    entry[key] = val

                    # if key == "path":
                    #     entry["Path"] = val

                #add the created dictionaries to the list/data
                output_data.append(entry)

        currentShot = self.shot_dropdown.currentText()

        if currentShot.casefold() in self.shot_data:
            self.shot_data[currentShot.casefold()] = output_data

        try:
            #dump it into the json
            with open(self.shot_json_path, "w") as f:
                json.dump(self.shot_data, f, indent=4)
            print(f"[OK] Presets saved to {self.shot_json_path}")
        except Exception as e:
            print(f"[ERROR] Could not save JSON: {e}")  

    def open_context_menu_shots(self, widget, position):
        #self.preset_table = QtWidgets.QTreeWidget()
        #widget = self.preset_table
        #item = QtWidgets.QTreeWidget.itemAt(position)
        item = widget.itemAt(position)
        index = widget.indexAt(position)
        if not item:
            return

        menu = QtWidgets.QMenu(widget)

        if item.text(0) == "path":
            open_action = menu.addAction("Open")

        delete_action = menu.addAction("Delete")

        action = menu.exec_(widget.viewport().mapToGlobal(position))

        if item.text(0) == "path":
            open_action.triggered.connect(self.open_actor_triggered(action, open_action, item))

        delete_action.triggered.connect(self.delete_actor_triggered(action, delete_action, item, index))          
