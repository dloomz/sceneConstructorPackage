import os
import json
import tempfile
from datetime import datetime
from PySide6 import QtWidgets, QtCore, QtGui
import maya.cmds as cmds

from sceneConstructorPackage.core.data_manager import DataManager
from .. import config

# close existing window if re-run
try:
    for widget in QtWidgets.QApplication.allWidgets():
        if widget.objectName() == "ActorPublishWindow":
            widget.close()
            widget.deleteLater()
except:
    pass

class ActorPublisherUI(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(ActorPublisherUI, self).__init__(parent)

        self.setObjectName("ActorPublishWindow")
        self.data_manager = DataManager()
        
        self.asset_publish_root = config.ASSET_PUBLISH_ROOT 
        self.authors_root = config.AUTHORS_ROOT

        self.setWindowTitle("Actor Publish")
        self.setMinimumWidth(800)
        self.setMinimumHeight(400)

        self.snapshot_path = None
        self.build_ui()
        self.auto_set_version()
        self.refresh_snapshot()
        self.refresh_selection()
        self.refresh_update_tree()
        cmds.scriptJob(event=["SelectionChanged", self.refresh_selection], protected=True)

    def build_ui(self):

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QHBoxLayout()
        central_widget.setLayout(main_layout)
        self.tab_widget = QtWidgets.QTabWidget()
        
        # TAB 1: UPDATE EXISTING 
        update_tab = QtWidgets.QWidget()
        update_main_layout = QtWidgets.QHBoxLayout(update_tab)
        
        # --- Left side: Asset Tree ---
        update_left_layout = QtWidgets.QVBoxLayout()
        update_left_label = QtWidgets.QLabel("Select Asset Department to Update:")
        self.update_asset_tree = QtWidgets.QTreeWidget()
        self.update_asset_tree.setHeaderLabels(["Asset", "Info"])
        self.update_asset_tree.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.update_asset_tree.itemSelectionChanged.connect(self._on_update_asset_selected)
        
        update_left_layout.addWidget(update_left_label)
        update_left_layout.addWidget(self.update_asset_tree)
        
        # --- Right side: Publish Info ---
        update_right_layout = QtWidgets.QVBoxLayout()
        
        # Author and Version
        update_author_row = QtWidgets.QHBoxLayout()
        update_author_label = QtWidgets.QLabel("Author:")
        self.update_author_dropdown = QtWidgets.QComboBox()
        try:
            authors = [d.name for d in self.authors_root.iterdir() if d.is_dir()]
            self.update_author_dropdown.addItems(authors or ["Unknown"])
        except:
            self.update_author_dropdown.addItem("Unknown")

        update_version_label = QtWidgets.QLabel("New Version:")
        self.update_version_spinbox = QtWidgets.QSpinBox()
        self.update_version_spinbox.setMinimum(1)
        self.update_version_spinbox.setMaximum(999)
        self.update_version_spinbox.setValue(1) 

        update_author_row.addWidget(update_author_label)
        update_author_row.addWidget(self.update_author_dropdown, 1)
        update_author_row.addWidget(update_version_label)
        update_author_row.addWidget(self.update_version_spinbox)

        # Notes
        update_note_label = QtWidgets.QLabel("Update Notes (what changed?):")
        self.update_note_box = QtWidgets.QTextEdit()
        self.update_note_box.setFixedHeight(100)

        # Publish Button
        self.update_publish_button = QtWidgets.QPushButton("Publish New Version")
        self.update_publish_button.setEnabled(False)
        self.update_publish_button.clicked.connect(self.publish_action)
        self.update_publish_button.setFixedHeight(40)
        self.update_publish_button.setStyleSheet("background-color: #007acc; font-weight: bold;")
        
        update_right_layout.addLayout(update_author_row)
        update_right_layout.addWidget(update_note_label)
        update_right_layout.addWidget(self.update_note_box)
        update_right_layout.addStretch()
        update_right_layout.addWidget(self.update_publish_button)
        
        update_main_layout.addLayout(update_left_layout, 1)
        update_main_layout.addLayout(update_right_layout, 1)
        
        self.tab_widget.addTab(update_tab, "Update Existing")

        #TAB 2: NEW ACTOR
        new_tab = QtWidgets.QWidget()
        new_layout = QtWidgets.QVBoxLayout(new_tab)

        #actor Name, Type, and Department
        name_type_row = QtWidgets.QHBoxLayout()
        
        name_label = QtWidgets.QLabel("Actor Name:")
        self.actor_name_line = QtWidgets.QLineEdit()
        
        type_label = QtWidgets.QLabel("Logical Type:")
        self.actor_type_dropdown = QtWidgets.QComboBox()
        self.actor_type_dropdown.addItems(['character', 'prop', 'set', 'camera'])

        dept_label = QtWidgets.QLabel("Department:")
        self.dept_dropdown = QtWidgets.QComboBox()
        self.dept_dropdown.addItems(['GEO', 'RIG', 'GRM', 'TEX'])

        name_type_row.addWidget(name_label)
        name_type_row.addWidget(self.actor_name_line, 1)
        name_type_row.addWidget(type_label)
        name_type_row.addWidget(self.actor_type_dropdown)
        name_type_row.addWidget(dept_label)
        name_type_row.addWidget(self.dept_dropdown)

        # (Author and Version row)
        author_row = QtWidgets.QHBoxLayout()
        author_label = QtWidgets.QLabel("Author:")
        self.author_dropdown = QtWidgets.QComboBox()
        try:
            authors = [d.name for d in self.authors_root.iterdir() if d.is_dir()]
            self.author_dropdown.addItems(authors or ["Unknown"])
        except:
            self.author_dropdown.addItem("Unknown")

        version_label = QtWidgets.QLabel("Version:")
        self.version_spinbox = QtWidgets.QSpinBox()
        self.version_spinbox.setMinimum(1)
        self.version_spinbox.setMaximum(999)
        self.version_spinbox.setValue(1) 

        author_row.addWidget(author_label)
        author_row.addWidget(self.author_dropdown, 1)
        author_row.addWidget(version_label)
        author_row.addWidget(self.version_spinbox)

        # (Notes, selection, publish button...)
        note_label = QtWidgets.QLabel("Add notes:")
        self.note_box = QtWidgets.QTextEdit()
        self.note_box.setFixedHeight(80)

        self.selection_label = QtWidgets.QLabel("Selected: None")
        self.selection_label.setStyleSheet("color: #aaa; font-style: italic;")

        publish_button = QtWidgets.QPushButton("Publish")
        publish_button.clicked.connect(self.publish_action)

        new_layout.addLayout(name_type_row)
        new_layout.addLayout(author_row)
        new_layout.addWidget(note_label)
        new_layout.addWidget(self.note_box)
        new_layout.addWidget(self.selection_label)
        new_layout.addWidget(publish_button)
        new_layout.addStretch()

        self.tab_widget.addTab(new_tab, "New Actor")

        # === RIGHT COLUMN (snapshot) ===
        right_layout = QtWidgets.QVBoxLayout()
        self.snapshot_label = QtWidgets.QLabel("Snapshot Here")
        self.snapshot_label.setAlignment(QtCore.Qt.AlignCenter)
        self.snapshot_label.setStyleSheet("background-color: #444; color: white; padding: 10px;")
        right_layout.addWidget(self.snapshot_label)

        refresh_button = QtWidgets.QPushButton("Refresh Snapshot")
        refresh_button.clicked.connect(self.refresh_snapshot)
        right_layout.addWidget(refresh_button)
        right_layout.addStretch()

        main_layout.addWidget(self.tab_widget, 2)
        main_layout.addLayout(right_layout, 1)
        
        # --- Connect signals ---
        self.actor_name_line.textChanged.connect(self.auto_set_version)
        self.dept_dropdown.currentTextChanged.connect(self.auto_set_version)
    
    def refresh_update_tree(self):
        """Loads all actors from the data manager and populates the update tree."""
        
        print("Refreshing asset tree...")
        self.update_asset_tree.clear()
        
        try:
            #load  actors using the DataManager
            all_actors = self.data_manager.load_actors()
        except Exception as e:
            print(f"Failed to load actors: {e}")
            return

        category_items = {} #group by type
        asset_name_items = {} #group by asset name

        for actor_data in all_actors:
            actor_type = actor_data.get('type', 'unknown')
            asset_name = actor_data.get('name', 'Unknown')
            department = actor_data.get('department', 'unknown')

            #get/create type 
            parent_category = category_items.get(actor_type)
            if not parent_category:
                parent_category = QtWidgets.QTreeWidgetItem([actor_type.capitalize()])
                self.update_asset_tree.addTopLevelItem(parent_category)
                category_items[actor_type] = parent_category

            #get/create asset name
            asset_key = (actor_type, asset_name)
            parent_asset_item = asset_name_items.get(asset_key)
            if not parent_asset_item:
                parent_asset_item = QtWidgets.QTreeWidgetItem([asset_name])
                #store minimal data on the asset group
                parent_asset_item.setData(0, QtCore.Qt.UserRole, {"is_group": True, "name": asset_name})
                parent_category.addChild(parent_asset_item)
                asset_name_items[asset_key] = parent_asset_item
            
            #add department item 
            version_str = actor_data.get('version', 'N/A')
            dept_item_name = f"{department.upper()} ({version_str})"
            dept_item = QtWidgets.QTreeWidgetItem([dept_item_name])
            
            #store the full data dict on this item
            dept_item.setData(0, QtCore.Qt.UserRole, actor_data) 
            parent_asset_item.addChild(dept_item)

        self.update_asset_tree.expandAll()
        print(f"Found and added {len(all_actors)} asset departments.")

    def auto_set_version(self):
        #scans the specific actor/dept folder for the next version
        actor_name = self.actor_name_line.text().strip()
        department = self.dept_dropdown.currentText()
        
        if not actor_name:
            self.version_spinbox.setValue(1)
            return

        publish_dir = self.asset_publish_root / actor_name / department / "PUBLISH"
        
        if not publish_dir.exists():
            self.version_spinbox.setValue(1)
            return
            
        max_version = 0
        try:
            for version_dir in publish_dir.iterdir():
                if version_dir.is_dir() and version_dir.name.startswith('v'):
                    try:
                        num = int(version_dir.name[1:])
                        max_version = max(max_version, num)
                    except ValueError:
                        pass
        except Exception as e:
            print(f"Could not auto-set version: {e}")

        self.version_spinbox.setValue(max_version + 1)
        

    def capture_snapshot(self):

        # Output path (playblast requires path WITHOUT extension)
        temp_dir = tempfile.gettempdir()
        base_path = os.path.join(temp_dir, "sc_snapshot")
        final_png = base_path + ".png"

        # Find the currently focused modelEditor panel
        model_panel = cmds.getPanel(withFocus=True)
        if not model_panel or cmds.getPanel(typeOf=model_panel) != "modelPanel":
            # If focus isn't on a 3D view, fall back to the first model panel
            panels = cmds.getPanel(type="modelPanel")
            if not panels:
                print("[ERROR] No 3D view found.")
                self.snapshot_path = None
                return
            model_panel = panels[0]

        # Get the current camera from the panel
        try:
            camera = cmds.modelEditor(model_panel, q=True, camera=True)
        except:
            print("[ERROR] Could not detect camera.")
            self.snapshot_path = None
            return

        # Get panel size
        parent = cmds.modelPanel(model_panel, q=True, control=True)
        width = cmds.control(parent, q=True, width=True)
        height = cmds.control(parent, q=True, height=True)

        # Force refresh (avoids black playblast frames)
        cmds.refresh(force=True)

        try:
            cmds.playblast(
                frame=cmds.currentTime(q=True),
                format="image",
                filename=base_path,
                forceOverwrite=True,
                viewer=False,
                widthHeight=(width, height),
                percent=100,
                quality=100,
                compression="png",
                camera=camera  # <<< ensures snapshot is from current camera
            )

            self.snapshot_path = final_png
            print(f"Snapshot saved: {self.snapshot_path}")

        except Exception as e:
            print("[ERROR] Playblast failed:", e)
            self.snapshot_path = None


    def display_snapshot(self, image_path):
        
        if not image_path or not os.path.exists(image_path):
            self.snapshot_label.setText("Snapshot Failed")
            return

        pixmap = QtGui.QPixmap(image_path)
        pixmap = pixmap.scaled(
            self.snapshot_label.width(),
            self.snapshot_label.height(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )
        self.snapshot_label.setPixmap(pixmap)

    def refresh_snapshot(self):
        self.capture_snapshot()
        self.display_snapshot(self.snapshot_path)

    def refresh_selection(self, *args):
        selected = cmds.ls(selection=True, long=True) or []
        if not selected:
            self.selection_label.setText("Selected: None")
            self.selection_label.setStyleSheet("color: #aaa; font-style: italic;")
        else:
            short_name = selected[0].split('|')[-1]
            self.selection_label.setText(f"Selected: {short_name}")
            self.selection_label.setStyleSheet("color: #DDD; font-style: normal;")

    def publish_action(self):
        author = self.author_dropdown.currentText()
        note = self.note_box.toPlainText().strip()
        version_num = self.version_spinbox.value()
        version_str = f"v{version_num:03d}"
        
        actor_name = self.actor_name_line.text().strip()
        actor_logical_type = self.actor_type_dropdown.currentText()
        department = self.dept_dropdown.currentText()
        
        if not actor_name:
            QtWidgets.QMessageBox.warning(self, "Publish Error", "Please enter an Actor Name.")
            return

        #DEFINE DIRECTORY AND BASE NAME
        output_dir = self.asset_publish_root / actor_name / department / "PUBLISH" / version_str 
        output_dir.mkdir(parents=True, exist_ok=True)
        
        #Consistent Base Name ---
        base_name = f"{actor_name}_{department.lower()}_{version_str}"
        # e.g., "Bob_rig_v001"


        #SAVE SNAPSHOT
        snapshot_dest = output_dir / f"{base_name}_snapshot.png" 
        if self.snapshot_path and os.path.exists(self.snapshot_path):
            cmds.sysFile(self.snapshot_path, copy=str(snapshot_dest))

        # 3. EXPORT ASSET
        file_ext = "usd"
        file_type = "USD Export"
        if department == "RIG":
            file_ext = "ma"
            file_type = "mayaAscii"
            
        publish_path = output_dir / f"{base_name}.{file_ext}"
        
        selected = cmds.ls(selection=True) or []
        if selected:
            cmds.file(
                str(publish_path),
                force=True,
                options=";", 
                type=file_type,
                exportSelected=True
            )
        else:
            QtWidgets.QMessageBox.warning(self, "Publish Error", "Nothing selected to publish.")
            return

        # 4. WRITE METADATA
        now = datetime.now()
        meta = {
            "author": author,
            "type": actor_logical_type,
            "department": department,
            "date-published": now.strftime("%y-%m-%d"),
            "time-published": now.strftime("%H:%M"),
            "version": version_str,
            "note": note,
            "path": str(publish_path),     
            "snapshot": str(snapshot_dest) 
        }
        json_path = output_dir / f"{base_name}_meta.json"
        with open(json_path, 'w') as f:
            json.dump(meta, f, indent=4)
            
        QtWidgets.QMessageBox.information(self, "Publish Complete", f"Published to {output_dir}")
        self.version_spinbox.setValue(version_num + 1)
        
    def _on_update_asset_selected(self, *args):
        """Called when an asset is selected in the 'Update Existing' tree."""
        
        selected_items = self.update_asset_tree.selectedItems()
        if not selected_items:
            self.update_publish_button.setEnabled(False)
            return
        
        item = selected_items[0]
        #get the data we stored on the item
        actor_data = item.data(0, QtCore.Qt.UserRole)
        
        #check if it's a valid department item (not a group)
        if not actor_data or actor_data.get("is_group"):
            self.update_publish_button.setEnabled(False)
            return

        #valid asset, enable button
        self.update_publish_button.setEnabled(True)

        #auto-set the next version
        #get the current version string 
        current_version_str = actor_data.get('version', 'v000')
        try:
            #convert to integer
            current_version_num = int(current_version_str[1:])
            #set the spinbox to the *next* version
            self.update_version_spinbox.setValue(current_version_num + 1)
        except:
            #fallback if version string is formatted strangely
            self.update_version_spinbox.setValue(1)
        
        #auto-set author from last publish
        last_author = actor_data.get('author')
        if last_author:
            self.update_author_dropdown.setCurrentText(last_author)