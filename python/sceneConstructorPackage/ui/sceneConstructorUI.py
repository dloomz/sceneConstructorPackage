import sys
from PySide6 import QtCore, QtGui, QtWidgets
from ..utils.fileUtils import open_in_native_explorer

# Path: sceneConstructorPackage/python/sceneConstructorPackage/ui/sceneConstructorUI.py

class sceneConstructor(QtWidgets.QWidget):
    """
    The main View (GUI) for the Scene Constructor.
    Emits signals on user interaction.
    Provides public slots to update its display.
    """
    
    #signals emitted by view
    publishActorsClicked = QtCore.Signal()
    publishShotsClicked = QtCore.Signal()
    
    #emits list of selected actor data
    transferClicked = QtCore.Signal(list) 
    
    #emits new scene name
    sceneSelected = QtCore.Signal(str) 
    
    #emits new shot name
    shotSelected = QtCore.Signal(str) 
    
    #context menu signals
    openPathRequested = QtCore.Signal(str)
    deletePresetActorRequested = QtCore.Signal(QtWidgets.QTreeWidgetItem)
    deleteShotActorRequested = QtCore.Signal(QtWidgets.QTreeWidgetItem)
    editItemRequested = QtCore.Signal(QtWidgets.QTreeWidgetItem, int)
    
    def __init__(self, parent=None):
        super(sceneConstructor, self).__init__(parent)
        self.setWindowTitle('Scene Constructor')
        self.resize(1000, 600)

        # Note: no DataManager, no state variables
        self.actor_types = ['camera', 'character', 'prop', 'set']

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        """Constructs all UI widgets."""
        
        #STYLING
        self.setStyleSheet("""
            QWidget {
                background-color: #333;
                color: #DDD;
                font-size: 14px;
            }
            QTreeWidget {
                background-color: #2b2b2b;
                border: 1px solid #555;
            }
            QHeaderView::section {
                background-color: #444;
                padding: 4px;
                border: 1px solid #555;
            }
            QPushButton {
                background-color: #5a5a5a;
                border: 1px solid #777;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #6a6a6a;
            }
            QLabel {
                font-weight: bold;
            }
        """)

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

        for types in self.actor_types:
            typeGroup = QtWidgets.QTreeWidgetItem([types])
            self.preset_table.addTopLevelItem(typeGroup)

        self.actorButton = QtWidgets.QPushButton('Publish Actors')

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

        for types in self.actor_types:
            typeGroup = QtWidgets.QTreeWidgetItem([types])
            self.shot_table.addTopLevelItem(typeGroup)

        sceneSel_layout = QtWidgets.QHBoxLayout()
        sceneSel_label = QtWidgets.QLabel('Select Scene:')
        self.construct_scene_dropdown = QtWidgets.QComboBox()
        sceneSel_layout.addWidget(sceneSel_label)
        sceneSel_layout.addWidget(self.construct_scene_dropdown)

        shotSel_layout = QtWidgets.QHBoxLayout()
        shotSel_label = QtWidgets.QLabel('Select Shot:')
        self.construct_shot_dropdown = QtWidgets.QComboBox()
        shotSel_layout.addWidget(shotSel_label)
        shotSel_layout.addWidget(self.construct_shot_dropdown)

        self.shotButton = QtWidgets.QPushButton('Publish Shots')

        shot_layout.addWidget(shot_label)
        shot_layout.addLayout(sceneSel_layout)
        shot_layout.addLayout(shotSel_layout)
        shot_layout.addWidget(self.shot_table)
        shot_layout.addWidget(self.shotButton)

        # ---- Transfer button ----
        transfer_layout = QtWidgets.QVBoxLayout()
        self.transferButton = QtWidgets.QPushButton('->')
        transfer_layout.addWidget(self.transferButton)

        # ---- Main layout assembly ----
        main_layout.addLayout(preset_layout)
        main_layout.addLayout(transfer_layout)
        main_layout.addLayout(shot_layout)
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 0.25)
        main_layout.setStretch(2, 1)
        
    def _connect_signals(self):
        """Connects widget signals to this class's signals."""
        
        #button clicks
        self.actorButton.clicked.connect(self.publishActorsClicked.emit)
        self.shotButton.clicked.connect(self.publishShotsClicked.emit)
        self.transferButton.clicked.connect(self._on_transfer_clicked)
        
        #dropdown changes
        self.construct_scene_dropdown.currentTextChanged.connect(self.sceneSelected.emit)
        self.construct_shot_dropdown.currentTextChanged.connect(self.shotSelected.emit)
        
        #context menus
        self.preset_table.customContextMenuRequested.connect(self._on_open_context_menu_presets)
        self.shot_table.customContextMenuRequested.connect(self._on_open_context_menu_shots)

    #called by controller to update view

    @QtCore.Slot(list)
    def update_actor_tree(self, actor_data: list):
        """Populates the actor preset tree."""
        self._populate_tree_widget(actor_data, self.preset_table)
        
    @QtCore.Slot(dict, str)
    def update_shot_tree(self, shot_data_cache: dict, current_shot_name: str):
        """Populates the shot constructor tree."""
        shot_key = current_shot_name.casefold()
        shot_items = shot_data_cache.get(shot_key, [])
        self._populate_tree_widget(shot_items, self.shot_table)
        
    @QtCore.Slot(list)
    def update_scene_dropdown(self, scenes: list):
        """Populates the scene dropdown."""
        self.construct_scene_dropdown.blockSignals(True)
        self.construct_scene_dropdown.clear()
        self.construct_scene_dropdown.addItems(scenes)
        self.construct_scene_dropdown.blockSignals(False)

    @QtCore.Slot(list)
    def update_shot_dropdown(self, shots: list):
        """Populates the shot dropdown."""
        self.construct_shot_dropdown.blockSignals(True)
        self.construct_shot_dropdown.clear()
        self.construct_shot_dropdown.addItems(shots)
        self.construct_shot_dropdown.blockSignals(False)
        
    @QtCore.Slot(str)
    def set_scene_dropdown(self, scene_name: str):
        """Sets the current scene in the dropdown."""
        self.construct_scene_dropdown.blockSignals(True)
        self.construct_scene_dropdown.setCurrentText(scene_name)
        self.construct_scene_dropdown.blockSignals(False)
        
    @QtCore.Slot(str)
    def set_shot_dropdown(self, shot_name: str):
        """Sets the current shot in the dropdown."""
        self.construct_shot_dropdown.blockSignals(True)
        self.construct_shot_dropdown.setCurrentText(shot_name)
        self.construct_shot_dropdown.blockSignals(False)
        
    @QtCore.Slot(QtWidgets.QTreeWidgetItem, int)
    def start_item_edit(self, item: QtWidgets.QTreeWidgetItem, column: int):
        """Puts a tree widget item into edit mode."""
        if item:
            item.treeWidget().editItem(item, column)

    @QtCore.Slot(str)
    def open_path_in_explorer(self, path: str):
        """Uses the utility function to open a path."""
        open_in_native_explorer(path)

    #helpers
    
    def _populate_tree_widget(self, data, tree_widget):
        """Helper to populate a QTreeWidget from Actor data."""
        
        #clear all items, including categories
        tree_widget.clear() 
        
        #add categories
        category_items = {}
        for type_name in self.actor_types:
            typeGroup = QtWidgets.QTreeWidgetItem([type_name])
            tree_widget.addTopLevelItem(typeGroup)
            category_items[type_name] = typeGroup
            
        for item in data:
            item_type = item.get('type')
            parent_item = category_items.get(item_type)

            if not parent_item: 
                continue
            
            name = item.get('name', 'Unknown')
            child = QtWidgets.QTreeWidgetItem([name])
            child.setFlags(child.flags() | QtCore.Qt.ItemIsEditable)
            parent_item.addChild(child)
            
            #store data on the item for later retrieval
            child.setData(0, QtCore.Qt.UserRole, item) 

            #add child attributes (path, shot, etc.)
            for key, val in item.items():
                if key in ('type', 'name'):
                    continue
                
                attr_child = QtWidgets.QTreeWidgetItem([key, str(val)])
                attr_child.setFlags(attr_child.flags() | QtCore.Qt.ItemIsEditable)
                child.addChild(attr_child)

    def _on_transfer_clicked(self):
        """Gathers data from selected actors and emits signal."""
        selected_items_data = []
        selectedActors = self.preset_table.selectedItems()

        for item in selectedActors:
            #get the data we stored on the item
            item_data = item.data(0, QtCore.Qt.UserRole)
            
            #main actor item
            if item_data: 
                selected_items_data.append(item_data)
                
            elif item.parent() and item.parent().data(0, QtCore.Qt.UserRole):
                #this is a child (like 'path'), get the parent's data
                parent_data = item.parent().data(0, QtCore.Qt.UserRole)
                if parent_data not in selected_items_data:
                    selected_items_data.append(parent_data)

        if selected_items_data:
            self.transferClicked.emit(selected_items_data)

    def get_all_data_from_tree(self, tree_widget: QtWidgets.QTreeWidget) -> list:
        """Helper to convert a tree widget back into a list of actor dicts."""
        output_data = []
        for i in range(tree_widget.topLevelItemCount()):
            type_item = tree_widget.topLevelItem(i)
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
        return output_data

    #context menu handlers
    
    def _on_open_context_menu_presets(self, position):
        item = self.preset_table.itemAt(position)
        if not item: return

        menu = QtWidgets.QMenu(self.preset_table)
        
        #only add "Edit" if it's an editable item (not a category)
        if item.parent() is not None:
            edit_action = menu.addAction("Edit")
            edit_action.triggered.connect(lambda: self._on_edit_item(item))

        # only add "Open" if it's a 'path' item
        if item.text(0).lower() == "path" and item.parent() is not None:
            open_action = menu.addAction("Open")
            open_action.triggered.connect(
                lambda: self.openPathRequested.emit(item.text(1))
            )
        
        #only add "Delete" if it's an actor (not a category or attribute)
        if item.parent() is not None and item.parent().parent() is not None:
             delete_action = menu.addAction("Delete")
             delete_action.triggered.connect(
                 lambda: self.deletePresetActorRequested.emit(item)
             )

        if menu.actions():
            menu.exec_(self.preset_table.viewport().mapToGlobal(position))

    def _on_open_context_menu_shots(self, position):
        item = self.shot_table.itemAt(position)
        if not item: return
        
        menu = QtWidgets.QMenu(self.shot_table)

        #"Open" for 'path' items
        if item.text(0).lower() == "path" and item.parent() is not None:
            open_action = menu.addAction("Open")
            open_action.triggered.connect(
                lambda: self.openPathRequested.emit(item.text(1))
            )

        #"Delete" for actor items
        if item.parent() is not None and item.parent().parent() is not None:
             delete_action = menu.addAction("Delete")
             delete_action.triggered.connect(
                 lambda: self.deleteShotActorRequested.emit(item)
             )

        if menu.actions():
            menu.exec_(self.shot_table.viewport().mapToGlobal(position))
            
    def _on_edit_item(self, item):
        """Internal helper to figure out which column to edit."""
        label = item.text(0).lower()
        #if it's an attribute (like 'path' or 'shot'), edit column 1 (value)
        if label in ("path", "shot") and item.columnCount() > 1:
            self.editItemRequested.emit(item, 1)
        #otherwise, edit column 0 (name)
        else:
            self.editItemRequested.emit(item, 0)