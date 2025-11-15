from PySide6 import QtCore
from sceneConstructorPackage.core.data_manager import DataManager

class SceneConstructorModel(QtCore.QObject):
    """
    Manages the application's data and state.
    Communicates data changes via signals.
    """
    
    #signals to notify the View when data has changed
    actorsReloaded = QtCore.Signal(list)
    scenesReloaded = QtCore.Signal(list)
    shotsReloaded = QtCore.Signal(list)
    shotDataLoaded = QtCore.Signal(str, dict) 
    shotDataSaved = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        
        #initialise 
        self.current_actors = []
        self.current_scenes = []
        self.current_shots = []
        
        self.current_scene_name = ""
        self.current_shot_name = ""
        self.current_shot_json_path = ""
        self.current_shot_data_cache = {} #caches loaded shot data

    #called by controller

    def load_actors(self):
        """Loads actors from DataManager and emits signal."""
        self.current_actors = self.data_manager.load_actors()
        self.actorsReloaded.emit(self.current_actors)

    def save_actors(self, actor_data: list):
        """Saves actors via DataManager."""
        self.data_manager.save_actors(actor_data)
        
        #reload to update
        self.load_actors() 

    def load_scenes(self):
        """Loads scene list from DataManager and emits signal."""
        self.current_scenes = self.data_manager.get_scenes()
        self.scenesReloaded.emit(self.current_scenes)
        
        #if scenes are loaded, automatically set the first one as active
        if self.current_scenes:
            self.set_current_scene(self.current_scenes[0])

    def load_shots_for_scene(self, scene_name: str):
        
        """Loads shot list for a specific scene and emits signal."""
        
        self.current_shots = self.data_manager.get_shots_in_scene(scene_name)
        self.shotsReloaded.emit(self.current_shots)
        
        #if shots are loaded, automatically set the first one as active
        if self.current_shots:
            self.set_current_shot(self.current_shots[0])
        else:
            #if no shots, clear the shot data
            self.set_current_shot("")

    def load_shot_data(self):
        
        """Loads data for the currently active scene and shot."""
        
        if not self.current_scene_name or not self.current_shot_name:
            self.current_shot_json_path = ""
            self.current_shot_data_cache = {}
            self.shotDataLoaded.emit("", {})
            return

        path, data = self.data_manager.load_shot_data(
            self.current_scene_name, 
            self.current_shot_name
        )
        
        self.current_shot_json_path = path
        self.current_shot_data_cache = data
        self.shotDataLoaded.emit(path, data)

    def save_shot_data(self, shot_tree_data: list):
        
        """Saves data for the currently active shot."""
        
        if not self.current_shot_json_path:
            print("[ERROR] Cannot save shot: Shot JSON path is not set.")
            return
            
        if not self.current_shot_name:
            print("[ERROR] Cannot save shot: No shot is selected.")
            return

        shot_key = self.current_shot_name.casefold()
        self.current_shot_data_cache[shot_key] = shot_tree_data
        
        self.data_manager.save_shot_data(
            self.current_shot_json_path, 
            self.current_shot_data_cache
        )
        self.shotDataSaved.emit()

    #set states

    def set_current_scene(self, scene_name: str):
        
        """Sets the active scene and triggers a shot load."""
        if scene_name != self.current_scene_name:
            self.current_scene_name = scene_name
            self.load_shots_for_scene(scene_name)

    def set_current_shot(self, shot_name: str):
        """Sets the active shot and triggers a shot data load."""
        #check path as well, in case shot name is same but scene changed
        new_path, _ = self.data_manager.load_shot_data(self.current_scene_name, shot_name)
        
        if new_path != self.current_shot_json_path:
            self.current_shot_name = shot_name
            self.load_shot_data()