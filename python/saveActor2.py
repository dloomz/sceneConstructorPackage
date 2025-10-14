import maya.cmds as cmds
import os
import json
import time

class ShotLoaderUI(object):
    def __init__(self):

        self.json_path = r'C:\Users\Dolapo\Desktop\python\static\00_pipeline\sceneConstructorPackage\Jsons\actors.json'
        #str(base_dir / "actors.json")
        self.shot_path = r'C:\Users\Dolapo\Desktop\python\static\00_pipeline\sceneConstructorPackage\Jsons\shots.json'
        #str(base_dir / "shots.json")
        self.scene_path = r'C:\Users\Dolapo\Desktop\python\static\25_footage\scene'
        #str(base_dir / "testFilm" / "25_footage" / "scene")
        
        self.window = "shotLoader"
        # self.scene_dropdown = None
        # self.shot_dropdown = None
        
        self.build_ui()
        self.load_scenes()

    def build_ui(self):
        #delete existing window if it exists
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window)

        #create a new window
        cmds.window(self.window, title="Shot Loader", widthHeight=(300, 100))

        #create the main row layout to hold two columns and a button
        main_layout = cmds.rowLayout(
            numberOfColumns=3,
            adjustableColumn=1,
            columnAttach3=('both', 'both', 'both')
        )

        #scene selection column
        cmds.columnLayout(adjustableColumn=True)
        cmds.text(label='Scene')
        self.scene_dropdown = cmds.optionMenu(changeCommand=self.scene_changed)
        cmds.setParent(main_layout)  # back to row layout

        #shot selection column
        cmds.columnLayout(adjustableColumn=True)
        cmds.text(label='Shot')
        self.shot_dropdown = cmds.optionMenu()
        cmds.setParent(main_layout)

        #load button column
        cmds.columnLayout(adjustableColumn=True)
        cmds.text(label='')
        cmds.button(label='Load Shot', command=self.import_actors)
        cmds.setParent('..')

        cmds.showWindow(self.window)

    def load_scenes(self):
        scene_files = os.listdir(self.scene_path)
        scene_files.sort()

        # clear existing items
        items = cmds.optionMenu(self.scene_dropdown, q=True, itemListLong=True)
        if items:
            for item in items:
                cmds.deleteUI(item)

        # add only folders to menu
        for scene in scene_files:
            if os.path.isdir(os.path.join(self.scene_path, scene)):
                cmds.menuItem(label=scene, parent=self.scene_dropdown)

        #load in shots upon start
        self.load_shots_in_scenes(cmds.optionMenu(self.scene_dropdown, q=True, value=True))

    def scene_changed(self, *args):
        # triggered when user picks a scene
        current_scene = cmds.optionMenu(self.scene_dropdown, q=True, value=True)
        print("Scene changed to:", current_scene)

        self.load_shots_in_scenes(current_scene)


    def load_shots_in_scenes(self, current_scene):

        # clear existing items
        items = cmds.optionMenu(self.shot_dropdown, q=True, itemListLong=True)
        if items:
            for item in items:
                cmds.deleteUI(item)
        
        shot_file_path = os.path.join(self.scene_path, current_scene)
        shotList = os.listdir(shot_file_path)

        shotList.sort()

        for s in shotList:
            if os.path.isdir(shot_file_path) == True:
                cmds.menuItem(label=s, parent=self.shot_dropdown)
            
        # self.show_shot_items(self.shot_dropdown.currentText())
        # self.shot_dropdown.currentTextChanged.connect(self.show_shot_items)

    def import_actors(self, *args):

        current_selected_scene = cmds.optionMenu(self.scene_dropdown, q=True, value=True)

        current_selected_shot = cmds.optionMenu(self.shot_dropdown, q=True, value=True)

        shot_dir = os.path.join(self.scene_path,current_selected_scene,current_selected_shot, 'SceneConstructor')

        print(shot_dir)

        pipeline_files = os.listdir(shot_dir)

        for file in pipeline_files:
            if os.path.isfile(os.path.join(shot_dir,file)) == True:
                if file.lower().endswith('.json'):
                    self.shot_json_path = os.path.join(shot_dir,file)
                    with open(self.shot_json_path) as f:
                        self.shot_data = json.load(f)

                    shot_items = self.shot_data[current_selected_shot.casefold()]  

                    for s in shot_items:
                        print(s["path"])

    def get_snapshot(self):
        '''grabbed from github, repurposed'''
        #get snapshot once actor has been published
        # set screenshot dimensions
        width = 960
        height = 540

        # get active viewport panel
        panel = cmds.getPanel(withFocus=True)

        # throw error if active panel is not a viewport
        if "modelPanel" not in cmds.getPanel(typeOf=panel):
            cmds.confirmDialog(title='Error!', message='Please select a viewport panel first.', button=['Ok'], defaultButton='Ok', dismissString='No')	
            raise RuntimeError('Error: Please select a viewport panel, then try again.')

        # get current frame number
        curFrame = int(cmds.currentTime(query=True))

        # get name of current file
        scName = cmds.file(query=True, sn=True, shn=True)

        # get full path of current file
        scPath = cmds.file(query=True, sn=True)

        # set new path where previews will be saved to
        path = scPath + "-prv/"

        # get name of current camera
        cam = cmds.modelEditor(panel, query=True, camera=True)

        # get current timestamp
        ots = int(time.time())
        #readable time
        ts = time.ctime(ots)
        '''sep so time and date sep to input into json'''

        # construct full path
        fullPath = "{}{}-{}-f{}-{}.jpg".format(path, scName, cam, curFrame, ts)

        # Create path if it doesn't exist
        if not os.path.exists(path):
            os.makedirs(path)

        # run playblast for current viewport
        cmds.playblast(fr=curFrame, v=False, fmt="image", c="jpg", orn=False, cf=fullPath, wh=[width,height], p=100)

        # log path to console for reference
        print('Snapshot saved as: ' + fullPath)

        # show popup message in viewport
        cmds.inViewMessage(amg='<span style="color:#82C99A;">Snapshot saved</span> for <hl>' + cam + '</hl> in <hl>' + scName + '<hl> at frame <hl>' + str(curFrame) + '</hl>', pos='topRight', fade=True, fst=3000)

    # def publish_actor(self, *args):


ShotLoaderUI()



