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

# Use standard PySide6 imports
from PySide6 import QtWidgets, QtCore, QtGui
# Note: You may need to run 'pip install PySide6' if you don't have it.

# Import the main UI class
from sceneConstructorPackage.ui.sceneConstructorUI import sceneConstructor

def run_ui():
    print('Launching Scene Constructor UI')

    QtWidgets.QApplication.setHighDpiScaleFactorRoundingPolicy(
        QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app_created = False
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
        app_created = True 

    # Launch the main window
    window = sceneConstructor()
    window.show()

    # This keeps the window open.
    if app_created:
        sys.exit(app.exec())

if __name__ == '__main__':
    run_ui()