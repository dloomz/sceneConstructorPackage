#!/usr/bin/env python

import sys
# Use standard PySide6 imports
from PySide6 import QtWidgets, QtCore, QtGui
# Note: You may need to run 'pip install PySide6' if you don't have it.

# Import the main UI class
# This assumes the PYTHONPATH setup in step 1 is complete.
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