# Path: python/sceneConstructorPackage/ui/sceneConstructorUI.py

import sys
from PySide6 import QtCore, QtGui, QtWidgets
from ..utils.fileUtils import open_in_native_explorer

class sceneConstructor(QtWidgets.QWidget):
    """
    The main View (GUI) for the Scene Constructor.
    Emits signals on user interaction.
    Provides public slots to update its display.
    """
    
    #signals emitted by view
    publishShotsClicked = QtCore.Signal()
    transferClicked = QtCore.Signal(list) 
    
    sceneSelected = QtCore.Signal(str) 
    shotSelected = QtCore.Signal(str) 
    
    actorSelected = QtCore.Signal(dict)
    
    #context menu signal
    openPathRequested = QtCore.Signal(str)
    deleteShotAssetRequested = QtCore.Signal(QtWidgets.QTreeWidgetItem)
    editItemRequested = QtCore.Signal(QtWidgets.QTreeWidgetItem, int)
    
    #signal to controller when shot changed
    shotVersionChanged = QtCore.Signal(QtWidgets.QTreeWidgetItem, str)

    def __init__(self, parent=None):
        super(sceneConstructor, self).__init__(parent)
        self.setWindowTitle('Scene Constructor')
        self.resize(1000, 750) 

        self.actor_types = ['camera', 'character', 'prop', 'set']

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        """Constructs all UI widgets."""
        
        # --- Styling ---
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
            QTextEdit {
                background-color: #2b2b2b;
                border: 1px solid #555;
            }
            QGroupBox {
                font-weight: bold;
            }
        """)

        # ========== Layout ==========
        main_layout = QtWidgets.QHBoxLayout(self)

        # ---- Left column (Assets) ----
        preset_layout = QtWidgets.QVBoxLayout()
        preset_label = QtWidgets.QLabel('Assets')

        self.preset_table = QtWidgets.QTreeWidget()
        self.preset_table.setHeaderLabels(['Asset', 'Info'])
        self.preset_table.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.preset_table.header().setStretchLastSection(True)
        self.preset_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.preset_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.preset_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        for types in self.actor_types:
            typeGroup = QtWidgets.QTreeWidgetItem([types])
            self.preset_table.addTopLevelItem(typeGroup)

        preset_layout.addWidget(preset_label)
        preset_layout.addWidget(self.preset_table, 2) 

        # --- Actor Metadata Panel ---
        self.metadata_group = QtWidgets.QGroupBox("Asset Metadata")
        metadata_layout = QtWidgets.QVBoxLayout()
        self.metadata_group.setLayout(metadata_layout)

        self.snapshot_label = QtWidgets.QLabel("Select an asset department (GEO, RIG...)")
        self.snapshot_label.setAlignment(QtCore.Qt.AlignCenter)
        self.snapshot_label.setMinimumHeight(200)
        self.snapshot_label.setStyleSheet("background-color: #2b2b2b; border: 1px solid #555;")
        
        self.notes_label = QtWidgets.QLabel("Publish Notes:")
        self.notes_display = QtWidgets.QTextEdit()
        self.notes_display.setReadOnly(True)
        self.notes_display.setFixedHeight(100)

        metadata_layout.addWidget(self.snapshot_label)
        metadata_layout.addWidget(self.notes_label)
        metadata_layout.addWidget(self.notes_display)
        
        preset_layout.addWidget(self.metadata_group, 1)

        # ---- Right column (Shots) ----
        shot_layout = QtWidgets.QVBoxLayout()
        shot_label = QtWidgets.QLabel('Construct')

        self.shot_table = QtWidgets.QTreeWidget()
        self.shot_table.setHeaderLabels(['Asset', 'Value'])
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
        
        #button
        self.shotButton.clicked.connect(self.publishShotsClicked.emit)
        self.transferButton.clicked.connect(self._on_transfer_clicked)
        
        #dropdown
        self.construct_scene_dropdown.currentTextChanged.connect(self.sceneSelected.emit)
        self.construct_shot_dropdown.currentTextChanged.connect(self.shotSelected.emit)
        
        #context
        self.preset_table.customContextMenuRequested.connect(self._on_open_context_menu_presets)
        self.shot_table.customContextMenuRequested.connect(self._on_open_context_menu_shots)

        #actor select
        self.preset_table.itemSelectionChanged.connect(self._on_actor_selection_changed)

        #shot item changed (for version)
        self.shot_table.itemChanged.connect(self._on_shot_item_changed)

    #public slots

    @QtCore.Slot(list)
    def update_actor_tree(self, actor_data: list):
        """Populates the asset preset tree."""
        self._populate_tree_widget(actor_data, self.preset_table)
        
    @QtCore.Slot(dict, str)
    def update_shot_tree(self, shot_data_cache: dict, current_shot_name: str):
        """Populates the shot constructor tree."""
        shot_key = current_shot_name.casefold()
        shot_items = shot_data_cache.get(shot_key, [])
        self._populate_tree_widget(shot_items, self.shot_table)
        
    @QtCore.Slot(list)
    def update_scene_dropdown(self, scenes: list):
        self.construct_scene_dropdown.blockSignals(True)
        self.construct_scene_dropdown.clear()
        self.construct_scene_dropdown.addItems(scenes)
        self.construct_scene_dropdown.blockSignals(False)

    @QtCore.Slot(list)
    def update_shot_dropdown(self, shots: list):
        self.construct_shot_dropdown.blockSignals(True)
        self.construct_shot_dropdown.clear()
        self.construct_shot_dropdown.addItems(shots)
        self.construct_shot_dropdown.blockSignals(False)
        
    @QtCore.Slot(str)
    def set_scene_dropdown(self, scene_name: str):
        self.construct_scene_dropdown.blockSignals(True)
        self.construct_scene_dropdown.setCurrentText(scene_name)
        self.construct_scene_dropdown.blockSignals(False)
        
    @QtCore.Slot(str)
    def set_shot_dropdown(self, shot_name: str):
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

    @QtCore.Slot(QtGui.QPixmap)
    def update_snapshot(self, pixmap: QtGui.QPixmap):
        """Displays the loaded snapshot pixmap."""
        if pixmap.isNull():
            self.snapshot_label.setText("No Snapshot Found")
            self.snapshot_label.setPixmap(QtGui.QPixmap()) # Clear it
        else:
            self.snapshot_label.setPixmap(pixmap.scaled(
                self.snapshot_label.width(), 
                self.snapshot_label.height(), 
                QtCore.Qt.KeepAspectRatio, 
                QtCore.Qt.SmoothTransformation
            ))

    @QtCore.Slot(str)
    def update_actor_notes(self, note_text: str):
        """Displays the loaded actor notes."""
        self.notes_display.setText(note_text or "No notes found.")
        
    @QtCore.Slot(str)
    def show_error_message(self, message: str):
        """Shows a warning message box."""
        QtWidgets.QMessageBox.warning(self, "Error", message)

    @QtCore.Slot(QtWidgets.QTreeWidgetItem, dict)
    def update_shot_item_version(self, item: QtWidgets.QTreeWidgetItem, new_data: dict):
        """
        Updates a shot item in the tree with new version data from the Controller.
        'item' is the 'version' attribute item.
        """
        dept_item = item.parent()
        if not dept_item:
            return
            
        new_version = new_data.get('version')
        new_path = new_data.get('path')
        department = new_data.get('department')

        self.shot_table.blockSignals(True)
        
        #update data stored on dept item
        dept_item.setData(0, QtCore.Qt.UserRole, new_data)
        
        #update dept item display text
        dept_item.setText(0, f"{department} ({new_version})")
        
        #update version item text
        item.setText(1, new_version)
        
        #find and update path item
        for i in range(dept_item.childCount()):
            child = dept_item.child(i)
            if child.text(0) == 'path':
                child.setText(1, new_path)
                break
        
        self.shot_table.blockSignals(False)

    @QtCore.Slot(QtWidgets.QTreeWidgetItem, str)
    def revert_shot_item_version(self, item: QtWidgets.QTreeWidgetItem, old_version: str):
        """Reverts the text of a version item if the new version was invalid."""
        self.shot_table.blockSignals(True)
        item.setText(1, old_version)
        self.shot_table.blockSignals(False)

    #internal helpers
    
    def _populate_tree_widget(self, data, tree_widget):
        tree_widget.clear()
        
        category_items = {}
        for type_name in self.actor_types:
            typeGroup = QtWidgets.QTreeWidgetItem([type_name])
            tree_widget.addTopLevelItem(typeGroup)
            category_items[type_name] = typeGroup

        asset_name_items = {} 

        for item_data in data:
            item_type = item_data.get('type')
            asset_name = item_data.get('name')
            department = item_data.get('department', 'unknown')

            parent_category = category_items.get(item_type)
            if not parent_category: 
                continue

            asset_key = (item_type, asset_name)
            parent_asset_item = asset_name_items.get(asset_key)

            if not parent_asset_item:
                parent_asset_item = QtWidgets.QTreeWidgetItem([asset_name])
                parent_asset_item.setData(0, QtCore.Qt.UserRole, {"is_group": True, "name": asset_name})
                parent_asset_item.setFlags(parent_asset_item.flags() & ~QtCore.Qt.ItemIsEditable)
                parent_category.addChild(parent_asset_item)
                asset_name_items[asset_key] = parent_asset_item

            dept_item_name = f"{department} ({item_data.get('version', 'N/A')})"
            dept_item = QtWidgets.QTreeWidgetItem([dept_item_name])
            dept_item.setData(0, QtCore.Qt.UserRole, item_data) 
            dept_item.setFlags(dept_item.flags() & ~QtCore.Qt.ItemIsEditable)
            parent_asset_item.addChild(dept_item)

            for key, val in item_data.items():
                if key in ('type', 'name', 'department', 'note', 'snapshot'):
                    continue
                
                attr_child = QtWidgets.QTreeWidgetItem([key, str(val)])
                
                if tree_widget == self.shot_table and key == 'version':
                    attr_child.setFlags(attr_child.flags() | QtCore.Qt.ItemIsEditable)
                else:
                    attr_child.setFlags(attr_child.flags() & ~QtCore.Qt.ItemIsEditable)
                
                dept_item.addChild(attr_child)


    def _on_transfer_clicked(self):
        """Gathers data from selected actors and emits signal."""
        selected_items_data = []
        selectedActors = self.preset_table.selectedItems()

        for item in selectedActors:
            item_data = self._get_data_from_item(item)
            
            #only transfer if it's a loadable department, not a group
            if item_data and not item_data.get("is_group"):
                if item_data not in selected_items_data:
                    selected_items_data.append(item_data)

        if selected_items_data:
            self.transferClicked.emit(selected_items_data)

    def get_all_data_from_tree(self, tree_widget: QtWidgets.QTreeWidget) -> list:
        """Helper to convert a tree widget back into a list of asset dicts."""
        output_data = []
        
        for i in range(tree_widget.topLevelItemCount()): # character, prop
            type_item = tree_widget.topLevelItem(i)
            
            for j in range(type_item.childCount()): # Bob, Apple
                asset_item = type_item.child(j)
                
                for k in range(asset_item.childCount()): # RIG, GEO
                    dept_item = asset_item.child(k)
                    
                    #full, correct data is stored on the department item
                    item_data = dept_item.data(0, QtCore.Qt.UserRole)
                    if item_data and not item_data.get("is_group"):
                        output_data.append(item_data)
                        
        return output_data

    def _get_data_from_item(self, item: QtWidgets.QTreeWidgetItem) -> dict | None:
        """Helper to get the asset data from a selected item or its parent."""
        if not item:
            return None
        
        actor_data = item.data(0, QtCore.Qt.UserRole)
        if actor_data:
            return actor_data
        
        if item.parent():
            actor_data = item.parent().data(0, QtCore.Qt.UserRole)
            if actor_data:
                return actor_data
        if item.parent() and item.parent().parent():
            actor_data = item.parent().parent().data(0, QtCore.Qt.UserRole)
            if actor_data:
                return actor_data
                
        return None

    def _on_actor_selection_changed(self):
        """Emits the data of the selected asset department."""
        selected_items = self.preset_table.selectedItems()
        if not selected_items:
            self.actorSelected.emit({}) 
            return
        
        item = selected_items[0]
        actor_data = self._get_data_from_item(item)
        
        if not actor_data or actor_data.get("is_group"):
            self.actorSelected.emit({})
        else:
            self.actorSelected.emit(actor_data)

    # --- Context Menu Handlers ---
    
    def _on_open_context_menu_presets(self, position):
        item = self.preset_table.itemAt(position)
        if not item: return

        menu = QtWidgets.QMenu(self.preset_table)
        actor_data = self._get_data_from_item(item)
        if not actor_data: return

        #"Open" for 'path' items
        if item.text(0).lower() == "path" and item.parent() is not None:
            self.openPathRequested.emit(item.text(1))

        #"Open Publish Directory" for department items
        if not actor_data.get("is_group") and "path" in actor_data:
             open_asset_action = menu.addAction("Open Publish Directory")
             file_path = Path(actor_data["path"])
             open_asset_action.triggered.connect(lambda: self.openPathRequested.emit(str(file_path.parent)))

        if menu.actions():
            menu.exec_(self.preset_table.viewport().mapToGlobal(position))

    def _on_open_context_menu_shots(self, position):
        item = self.shot_table.itemAt(position)
        if not item: return
        
        menu = QtWidgets.QMenu(self.shot_table)
        actor_data = self._get_data_from_item(item)
        if not actor_data: return

        #"Edit Version" for 'version' items
        if item.text(0).lower() == "version" and item.parent() is not None:
            menu.addAction("Edit Version").triggered.connect(
                lambda: self.editItemRequested.emit(item, 1) # Edit column 1
            )

        #"Open" for 'path' items
        if item.text(0).lower() == "path" and item.parent() is not None:
            menu.addAction("Open File Location").triggered.connect(
                lambda: self.openPathRequested.emit(item.text(1))
            )

        #"Delete" for department items
        if actor_data and not actor_data.get("is_group") and item.parent().parent() is not None:
             menu.addAction("Delete Asset").triggered.connect(
                 lambda: self.deleteShotAssetRequested.emit(item)
             )

        if menu.actions():
            menu.exec_(self.shot_table.viewport().mapToGlobal(position))
            
    def _on_shot_item_changed(self, item, column):
        """
        Emits a signal when an item in the shot tree is edited.
        """
        #only care if a 'version' attribute's text (col 1) was changed
        if item.text(0) == 'version' and column == 1:
            self.shotVersionChanged.emit(item, item.text(1))