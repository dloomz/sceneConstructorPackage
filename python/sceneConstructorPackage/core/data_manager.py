import json
import os
from pathlib import Path
from .. import config

class DataManager:
    """
    Handles all file I/O operations.
    - Scans ASSET_PUBLISH_ROOT for Actors.
    - Scans SCENE_ROOT for Scenes and Shots.
    """

    def __init__(self):
        pass 


    def load_actors(self) -> list:
        """
        Loads all global Actors by scanning the ASSET_PUBLISH_ROOT.
        Scans for .../Assets/[Asset_Name]/[Department]/PUBLISH/[version]/
        and finds the *_meta.json file.
        """
        print("[INFO] Scanning for published assets...")
        found_assets = []
        
        root = config.ASSET_PUBLISH_ROOT 
        
        if not root.exists():
            print(f"[WARN] Asset publish root does not exist: {root}")
            return []

        try:
            for asset_dir in root.iterdir():
                if not asset_dir.is_dir(): continue
                asset_name = asset_dir.name

                for dept_dir in asset_dir.iterdir():
                    if not dept_dir.is_dir() or dept_dir.name in ("WORK", "REF"):
                        continue
                    department = dept_dir.name 

                    publish_dir = dept_dir / "PUBLISH"
                    if not publish_dir.exists(): 
                        continue

                    versions = [d.name for d in publish_dir.iterdir() if d.is_dir() and d.name.startswith('v')]
                    if not versions: 
                        continue

                    latest_version_str = sorted(versions)[-1]
                    latest_version_dir = publish_dir / latest_version_str

                    meta_files = list(latest_version_dir.glob("*_meta.json"))
                    if not meta_files:
                        print(f"[WARN] Skipping {asset_name}/{department}: No _meta.json found in {latest_version_dir}")
                        continue
                    
                    meta_path = meta_files[0] 
                    
                    try:
                        with open(meta_path, 'r') as f:
                            meta_data = json.load(f)
                    except Exception as e:
                        print(f"[ERROR] Could not read {meta_path}: {e}")
                        continue
                    
                    meta_data['name'] = asset_name
                    
                    loadable_path_str = meta_data.get('path')
                    if not loadable_path_str or not Path(loadable_path_str).exists():
                        print(f"[WARN] Skipping {asset_name}/{department}: 'path' in meta.json is missing or invalid.")
                        continue
                        
                    found_assets.append(meta_data)
                
        except Exception as e:
            print(f"[ERROR] Failed during asset scan: {e}")
            
        print(f"[INFO] Found {len(found_assets)} published asset departments.")
        return sorted(found_assets, key=lambda x: (x.get('name', ''), x.get('department', '')))

    def get_all_versions_for_asset(self, asset_name: str, department: str) -> list[str]:
        """
        Scans the publish directory for an asset/department and returns
        a sorted list of all found version strings (e.g., ['v001', 'v002']).
        """
        publish_dir = (
            config.ASSET_PUBLISH_ROOT / 
            asset_name / 
            department / 
            "PUBLISH"
        )
        
        if not publish_dir.exists():
            print(f"[WARN] No PUBLISH directory found at: {publish_dir}")
            return []
            
        try:
            versions = [
                d.name for d in publish_dir.iterdir() 
                if d.is_dir() and d.name.startswith('v')
            ]
            versions.sort()
            return versions
        except Exception as e:
            print(f"[ERROR] Could not list versions for {asset_name}/{department}: {e}")
            return []

    def get_asset_version_details(self, asset_name: str, department: str, version_str: str) -> dict | None:
        """
        Finds the meta.json for a specific asset version and returns its data.
        Returns None if the version or metadata doesn't exist.
        """
        
        version_dir = (
            config.ASSET_PUBLISH_ROOT / 
            asset_name / 
            department / 
            "PUBLISH" / 
            version_str
        )
        
        if not version_dir.exists():
            print(f"[WARN] Version not found: {version_dir}")
            return None
            
        meta_files = list(version_dir.glob("*_meta.json"))
        if not meta_files:
            print(f"[WARN] No _meta.json found in {version_dir}")
            return None
            
        meta_path = meta_files[0]
        
        try:
            with open(meta_path, 'r') as f:
                meta_data = json.load(f)
            
            meta_data['name'] = asset_name

            loadable_path_str = meta_data.get('path')
            if not loadable_path_str or not Path(loadable_path_str).exists():
                print(f"[WARN] Invalid path in {meta_path}: {loadable_path_str}")
                return None
                
            return meta_data
        except Exception as e:
            print(f"[ERROR] Could not read {meta_path}: {e}")
            return None

    
    def get_scenes(self):
        if not config.SCENE_ROOT.exists():
            return []
        return sorted([d.name for d in config.SCENE_ROOT.iterdir() if d.is_dir()])

    def get_shots_in_scene(self, scene_name: str):
        scene_path = config.SCENE_ROOT / scene_name
        if not scene_path.exists():
            return []
        return sorted([d.name for d in scene_path.iterdir() if d.is_dir()])

    def load_shot_data(self, scene_name: str, shot_name: str) -> tuple[str, dict]:
        shot_dir = config.SCENE_ROOT / scene_name / shot_name / 'SceneConstructor'
        
        if not shot_dir.exists():
            shot_dir.mkdir(parents=True, exist_ok=True) 

        json_file_path = ""
        for f in shot_dir.iterdir():
            if f.suffix.lower() == '.json':
                json_file_path = f
                break
        
        if json_file_path and json_file_path.exists():
            try:
                with open(json_file_path, 'r') as json_file:
                    data = json.load(json_file)
                    return str(json_file_path), data
            except Exception as e:
                print(f"[ERROR] Failed to load shot JSON {json_file_path}: {e}")
                return str(json_file_path), {}
        
        default_path = shot_dir / f"{shot_name.lower()}_scene_data.json"
        return str(default_path), {}

    def save_shot_data(self, shot_json_path: str, shot_data: dict):
        try:
            Path(shot_json_path).parent.mkdir(parents=True, exist_ok=True)
            with open(shot_json_path, "w") as f:
                json.dump(shot_data, f, indent=4)
            print(f"[OK] Shots saved to {shot_json_path}")
        except Exception as e:
            print(f"[ERROR] Could not save Shots JSON: {e}")