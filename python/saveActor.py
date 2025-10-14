import os
import json
import tempfile
from datetime import datetime

from PySide6 import QtWidgets, QtCore, QtGui
import maya.cmds as cmds

# close existing window if re-run
try:
    for widget in QtWidgets.QApplication.allWidgets():
        if widget.objectName() == "ActorPublishWindow":
            widget.close()
            widget.deleteLater()
except:
    pass


class ShotLoaderUI(QtWidgets.QMainWindow):
    def __init__(self, json_path, shot_path, scene_path, parent=None):
        super(ShotLoaderUI, self).__init__(parent)

        self.setObjectName("ActorPublishWindow")

        self.json_path = json_path
        self.shot_path = shot_path
        self.scene_path = scene_path
        self.authors_json_path = r'C:\Users\Dolapo\Desktop\python\static\05_sandbox'

        self.setWindowTitle("Actor Publish")
        self.setMinimumWidth(800)
        self.setMinimumHeight(400)

        # will store temp snapshot path
        self.snapshot_path = None

        # make ui
        self.build_ui()

        # set up: find next version
        self.auto_set_version()
        # take snapshot
        self.refresh_snapshot()
        # display selected geo
        self.refresh_selection()

        # run showing new selection every time it changes
        cmds.scriptJob(event=["SelectionChanged", self.refresh_selection], protected=True)

    def build_ui(self):
        # central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QHBoxLayout()
        central_widget.setLayout(main_layout)

        # === CREATE TAB WIDGET FOR LEFT COLUMN ===
        self.tab_widget = QtWidgets.QTabWidget()

        # ------------------
        # TAB 1: UPDATE EXISTING (blank for now)
        # ------------------
        update_tab = QtWidgets.QWidget()
        update_layout = QtWidgets.QVBoxLayout(update_tab)

        # placeholder content so it's obvious where to add widgets later
        placeholder_label = QtWidgets.QLabel("Update Existing Actor\n\n(Add widgets here later)")
        placeholder_label.setAlignment(QtCore.Qt.AlignCenter)
        placeholder_label.setStyleSheet(
            "color: #888; font-style: italic; border: 1px dashed #666; padding: 20px;"
        )

        update_layout.addStretch()
        update_layout.addWidget(placeholder_label)
        update_layout.addStretch()

        self.tab_widget.addTab(update_tab, "Update Existing")

        # ------------------
        # TAB 2: NEW ACTOR (your current left column)
        # ------------------
        new_tab = QtWidgets.QWidget()
        new_layout = QtWidgets.QVBoxLayout(new_tab)

        # author and version row
        author_row = QtWidgets.QHBoxLayout()
        author_label = QtWidgets.QLabel("Author:")

        try:
            authors = os.listdir(self.authors_json_path)
            self.author_dropdown = QtWidgets.QComboBox()

            if isinstance(authors, list):
                self.author_dropdown.addItems(authors)
            elif isinstance(authors, dict):
                self.author_dropdown.addItems(authors.keys())
            else:
                self.author_dropdown.addItem("Unknown")
        except Exception as e:
            print("Error loading:", e)
            self.author_dropdown = QtWidgets.QComboBox()
            self.author_dropdown.addItem("Unknown")

        version_label = QtWidgets.QLabel("Version:")
        self.version_spinbox = QtWidgets.QSpinBox()
        self.version_spinbox.setMinimum(1)
        self.version_spinbox.setMaximum(999)
        self.version_spinbox.setValue(1) # updated by auto_set_version()

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
        # scan asset_path and set spinbox to next available version
        if not os.path.exists(self.scene_path):
            os.makedirs(self.scene_path, exist_ok=True)
            self.version_spinbox.setValue(1)
            return

        max_version = 0
        for name in os.listdir(self.scene_path):
            if name.lower().startswith("v") and len(name) >= 4:
                try:
                    num = int(name[1:4])
                    max_version = max(max_version, num)
                except ValueError:
                    pass

        self.version_spinbox.setValue(max_version + 1)

    def capture_snapshot(self):
        # viewport snapshot of the current maya scene
        temp_dir = tempfile.gettempdir()
        self.snapshot_path = os.path.join(temp_dir, "maya_snapshot.png")

        # delete old file if exists
        if os.path.exists(self.snapshot_path):
            try:
                os.remove(self.snapshot_path)
            except:
                pass

        # create a snapshot using playblast (silent, no viewer)
        cmds.playblast(
            completeFilename=self.snapshot_path,
            forceOverwrite=True,
            format='image',
            compression='png',
            widthHeight=(800, 600),
            showOrnaments=False,
            viewer=False,
            frame=cmds.currentTime(query=True)
        )

    def display_snapshot(self):
        # loads the snapshot
        if self.snapshot_path and os.path.exists(self.snapshot_path):
            pixmap = QtGui.QPixmap(self.snapshot_path)
            self.snapshot_label.setPixmap(pixmap.scaled(
                400, 300,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            ))
        else:
            self.snapshot_label.setText("Snapshot failed")

    def refresh_snapshot(self):
        # captures and updates snapshot preview
        self.capture_snapshot()
        self.display_snapshot()

    def refresh_selection(self):
        # update UI to show current selection
        selected = cmds.ls(selection=True) or []
        if selected:
            self.selection_label.setText("Selected: " + ", ".join(selected))
        else:
            self.selection_label.setText("Selected: None")

    def publish_action(self):
        # create a version folder, save snapshot, export USD, and write metadata JSON
        author = self.author_dropdown.currentText()
        note = self.note_box.toPlainText().strip()
        version_num = self.version_spinbox.value()
        version_str = f"v{version_num:03d}"

        # create version folder
        output_dir = os.path.join(self.scene_path, version_str)
        os.makedirs(output_dir, exist_ok=True)

        # save snapshot to folder
        snapshot_dest = os.path.join(output_dir, f"{version_str}_snapshot.png")
        if self.snapshot_path and os.path.exists(self.snapshot_path):
            cmds.sysFile(self.snapshot_path, copy=snapshot_dest)

        # export USD of selected objects
        selected = cmds.ls(selection=True) or []
        if selected:
            usd_path = os.path.join(output_dir, f"{version_str}_geo.usd")
            cmds.file(
                usd_path,
                force=True,
                options=";", # default export options
                type="USD Export",
                exportSelected=True
            )

        # write metadata JSON
        now = datetime.now()
        meta = {
            "author": author,
            "date-published": now.strftime("%y-%m-%d"),
            "time-published": now.strftime("%H:%M"),
            "version": f"{version_num:03d}",
            "note": note
        }
        json_path = os.path.join(output_dir, f"{version_str}_meta.json")
        with open(json_path, 'w') as f:
            json.dump(meta, f, indent=4)

        QtWidgets.QMessageBox.information(self, "Publish Complete", f"Published to {output_dir}")

        # after publishing, bump to next version automatically
        self.version_spinbox.setValue(version_num + 1)


# paths:
json_path = r'C:\Users\Dolapo\Desktop\python\static\00_pipeline\sceneConstructorPackage\Jsons\actors.json'
shot_path = r'C:\Users\Dolapo\Desktop\python\static\00_pipeline\shotMaster'
actor_path = r'C:\Users\Dolapo\Desktop\python\static\30_assets'

win = ShotLoaderUI(json_path, shot_path, scene_path)
win.show()