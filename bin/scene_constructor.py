#!/usr/bin/env python

import sys
import os
from pathlib import Path

# Resolve the path to the 'python' directory containing sceneConstructorPackage
script_dir = Path(__file__).resolve().parent 
package_path = str(script_dir.parent / 'python') 

# Add the 'python' directory to sys.path if it's not already there
if package_path not in sys.path:
    sys.path.append(package_path)
# --------------------------------------------------------------------------

from PySide6 import QtWidgets, QtCore

# Import the new MVC Controller
from sceneConstructorPackage.ui.scene_constructor_controller import SceneConstructorController

def run_ui():
    print('Launching Scene Constructor UI (MVC)')

    QtWidgets.QApplication.setHighDpiScaleFactorRoundingPolicy(
        QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app_created = False
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
        app_created = True 

    # Launch the controller, which creates the model and view
    controller = SceneConstructorController()
    controller.run() # This will show the window

    # This keeps the window open.
    if app_created:
        sys.exit(app.exec())

if __name__ == '__main__':
    run_ui()