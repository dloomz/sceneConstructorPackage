#!/usr/bin/env python

import sys

# Path: sceneConstructorPackage/bin/scene_constructor.py

# framestore import, REPLACE with QT IMPORT
from PySide6 import QtWidgets 
# dots represent folder struct, calling package ui python file
from sceneConstructorPackage.ui.sceneConstructorUI import sceneConstructor

def run_ui():
    print('Launching Scene Constructor UI')
    # Use QApplication if not running inside a host application
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
        
    window = sceneConstructor()
    window.show()

    if not QtWidgets.QApplication.instance().parent():
        sys.exit(app.exec())

if __name__ == "__main__":
    run_ui()