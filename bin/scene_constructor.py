#!/usr/bin/env python

import sys
### NEW ###
import os
from pathlib import Path

### NEW ###
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
    
    # Check if a QApplication instance already exists (common in Maya/other hosts)
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
        
    # Launch the main window
    window = sceneConstructor()
    window.show()

    # Only start the event loop if we created the QApplication instance
    if app and app.startingUp():
        sys.exit(app.exec())

if __name__ == '__main__':
    run_ui()