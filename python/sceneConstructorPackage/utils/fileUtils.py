import subprocess
import platform

# Path: sceneConstructorPackage/python/sceneConstructorPackage/utils/fileUtils.py

def open_in_native_explorer(path: str):
    """Open a file or folder in the native file explorer."""
    system = platform.system()
    if system == "Windows":
        subprocess.run(["explorer", path])
    elif system == "Darwin":  # macOS
        subprocess.run(["open", path])
    else:  # Linux/Unix
        subprocess.run(["xdg-open", path])