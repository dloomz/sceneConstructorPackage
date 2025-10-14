import os
import json
import tempfile
from datetime import datetime

from PySide6 import QtWidgets, QtCore, QtGui
import maya.cmds as cmds

# Path: sceneConstructorPackage/python/sceneConstructorPackage/ui/actorPublisherUI.py
from sceneConstructorPackage.core.data_manager import DataManager
from sceneConstructorPackage import config
# close existing window if re-run
try:
    for widget in QtWidgets.QApplication.allWidgets():
        if widget.objectName() == "ActorPublishWindow":
            widget.close()
            widget.deleteLater()
except:
    pass

class ActorPublisherUI(QtWidgets.QMainWindow): # 🆕 Renamed class
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
        cmds.scriptJob(event=["SelectionChanged", self.refresh_selection], protected=True)

    def build_ui(self):
        # ... (Layout setup remains the same)
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QHBoxLayout()
        central_widget.setLayout(main_layout)
        self.tab_widget = QtWidgets.QTabWidget()
        
        # TAB 1: UPDATE EXISTING (omitted for brevity)
        update_tab = QtWidgets.QWidget()
        self.tab_widget.addTab(update_tab, "Update Existing")

        # TAB 2: NEW ACTOR
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

        # author and version row
        author_row = QtWidgets.QHBoxLayout()
        author_label = QtWidgets.QLabel("Author:")
        # Load authors from config path
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

        # notes section
        note_label = QtWidgets.QLabel("Add notes:")
        self.note_box = QtWidgets.QTextEdit()
        self.note_box.setFixedHeight(80)

        # current selection
        self.selection_label = QtWidgets.QLabel("Selected: None")
        self.selection_label.setStyleSheet("color: #aaa; font-style: italic;")

        # publish button
        publish_button = QtWidgets.QPushButton("Publish")
        publish_button.clicked.connect(self.publish_action)

        # add widgets to NEW ACTOR tab layout
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

        # add both to main layout
        main_layout.addWidget(self.tab_widget, 2)
        main_layout.addLayout(right_layout, 1)

    def auto_set_version(self):
        # Scan Actor's path for max version (using a placeholder asset path for now)
        # Should be updated to scan self.asset_publish_root / self.actor_name_line.text()
        # For simplicity now, we only check the root publish directory.
        if not self.asset_publish_root.exists():
            self.asset_publish_root.mkdir(parents=True, exist_ok=True)
            self.version_spinbox.setValue(1)
            return

        # Simple root folder check (this is weak, real world needs to check inside actor folders)
        max_version = 0
        for actor_dir in self.asset_publish_root.iterdir():
            if actor_dir.is_dir():
                for name in actor_dir.iterdir():
                    if name.name.lower().startswith("v") and len(name.name) >= 4:
                        try:
                            num = int(name.name[1:4])
                            max_version = max(max_version, num)
                        except ValueError:
                            pass

        self.version_spinbox.setValue(max_version + 1)

    # ... (capture_snapshot, display_snapshot, refresh_snapshot, refresh_selection remain the same)

    def publish_action(self):
        author = self.author_dropdown.currentText()
        note = self.note_box.toPlainText().strip()
        version_num = self.version_spinbox.value()
        version_str = f"v{version_num:03d}"
        
        # 🆕 Get Actor Name and Type
        actor_name = self.actor_name_line.text().strip()
        actor_type = self.actor_type_dropdown.currentText()
        
        if not actor_name:
            QtWidgets.QMessageBox.warning(self, "Publish Error", "Please enter an Actor Name.")
            return

        # create version folder: ASSET_PUBLISH_ROOT/ActorName/v001/
        output_dir = self.asset_publish_root / actor_name / version_str 
        output_dir.mkdir(parents=True, exist_ok=True)

        # save snapshot to folder
        snapshot_dest = output_dir / f"{version_str}_snapshot.png"
        if self.snapshot_path and os.path.exists(self.snapshot_path):
            cmds.sysFile(self.snapshot_path, copy=str(snapshot_dest))

        # export USD of selected objects
        selected = cmds.ls(selection=True) or []
        usd_path = output_dir / f"{version_str}_geo.usd"
        if selected:
            cmds.file(
                str(usd_path),
                force=True,
                options=";", 
                type="USD Export",
                exportSelected=True
            )

        # write metadata JSON
        now = datetime.now()
        meta = {
            "author": author,
            "date-published": now.strftime("%y-%m-%d"),
            "time-published": now.strftime("%H:%M"),
            "version": version_str,
            "note": note,
            "path": str(output_dir) # Path to the published version folder
        }
        json_path = output_dir / f"{version_str}_meta.json"
        with open(json_path, 'w') as f:
            json.dump(meta, f, indent=4)
            
        # --- UPDATE GLOBAL ACTORS JSON ---
        all_actors = self.data_manager.load_actors()
        
        new_actor_entry = {
            "type": actor_type,
            "name": actor_name,
            "path": str(usd_path), # Point to the USD file for loading
        }
        
        # Find and replace old entry, or append
        updated = False
        for i, actor in enumerate(all_actors):
            if actor.get("name") == actor_name:
                all_actors[i] = new_actor_entry
                updated = True
                break
        
        if not updated:
            all_actors.append(new_actor_entry)
            
        self.data_manager.save_actors(all_actors)

        QtWidgets.QMessageBox.information(self, "Publish Complete", f"Published to {output_dir}")
        self.version_spinbox.setValue(version_num + 1)