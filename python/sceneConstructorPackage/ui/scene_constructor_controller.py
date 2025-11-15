from PySide6 import QtWidgets
from sceneConstructorPackage.ui.sceneConstructorUI import sceneConstructor
from sceneConstructorPackage.ui.scene_constructor_model import SceneConstructorModel

class SceneConstructorController:
    """
    The Controller linking the View (sceneConstructor) 
    and the Model (SceneConstructorModel).
    """
    def __init__(self):
        self.model = SceneConstructorModel()
        self.view = sceneConstructor()

        self._connect_signals()

    def run(self):
        """Show the view and load initial data."""
        self.view.show()
        # Trigger initial data load
        self.model.load_actors()
        self.model.load_scenes() 

    def _connect_signals(self):
        """Connect signals from View to Controller slots, and Model to View slots."""
        
        #view to controller 
        self.view.publishActorsClicked.connect(self.on_save_actors)
        self.view.publishShotsClicked.connect(self.on_save_shots)
        self.view.sceneSelected.connect(self.model.set_current_scene)
        self.view.shotSelected.connect(self.model.set_current_shot)
        
        self.view.transferClicked.connect(self.on_transfer_actors)
        self.view.openPathRequested.connect(self.view.open_path_in_explorer)
        self.view.editItemRequested.connect(self.view.start_item_edit)
        
        self.view.deletePresetActorRequested.connect(self.on_delete_preset_actor)
        self.view.deleteShotActorRequested.connect(self.on_delete_shot_actor)

        #model to view 
        self.model.actorsReloaded.connect(self.view.update_actor_tree)
        self.model.scenesReloaded.connect(self.on_scenes_reloaded)
        self.model.shotsReloaded.connect(self.on_shots_reloaded)
        self.model.shotDataLoaded.connect(self.on_shot_data_loaded)
        
    #controller slots

    def on_save_actors(self):
        """Get data from actor tree and tell model to save."""
        actor_data = self.view.get_all_data_from_tree(self.view.preset_table)
        self.model.save_actors(actor_data)

    def on_save_shots(self):
        """Get data from shot tree and tell model to save."""
        shot_data = self.view.get_all_data_from_tree(self.view.shot_table)
        self.model.save_shot_data(shot_data)

    def on_transfer_actors(self, actors_to_transfer: list):
        """Adds selected actors to the current shot data and updates the view."""
        #TODO: prevent duplicates better
        
        #get current shot data
        shot_key = self.model.current_shot_name.casefold()
        current_shot_items = self.model.current_shot_data_cache.get(shot_key, [])
        
        #add new items
        #simple duplicate check by name and type
        existing_names = {(item['name'], item['type']) for item in current_shot_items}
        for actor in actors_to_transfer:
            if (actor['name'], actor['type']) not in existing_names:
                current_shot_items.append(actor)
        
        #update the cache
        self.model.current_shot_data_cache[shot_key] = current_shot_items
        
        #update the view directly
        self.view.update_shot_tree(self.model.current_shot_data_cache, self.model.current_shot_name)

    def on_delete_preset_actor(self, item: QtWidgets.QTreeWidgetItem):
        """Removes an item from the preset tree and triggers a save."""
        (item.parent() or self.view.preset_table.invisibleRootItem()).removeChild(item)
        self.on_save_actors()

    def on_delete_shot_actor(self, item: QtWidgets.QTreeWidgetItem):
        """Removes an item from the shot tree and triggers a save."""
        (item.parent() or self.view.shot_table.invisibleRootItem()).removeChild(item)
        self.on_save_shots() 

    #slots that handle model signals
    
    def on_scenes_reloaded(self, scenes: list):
        
        """Handle new scene list from model."""
        self.view.update_scene_dropdown(scenes)
        if scenes:
            self.view.set_scene_dropdown(scenes[0])
            #model will automatically load shots for this scene
            
    def on_shots_reloaded(self, shots: list):
        
        """Handle new shot list from model."""
        self.view.update_shot_dropdown(shots)
        if shots:
            self.view.set_shot_dropdown(shots[0])
            #model will automatically load data for this shot
        else:
            #no shots, clear the view
            self.view.update_shot_tree({}, "")

    def on_shot_data_loaded(self, json_path: str, shot_data: dict):
        
        """Handle new shot data from model."""
        self.view.update_shot_tree(shot_data, self.model.current_shot_name)