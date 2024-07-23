import json
import os

def load_camera_params(camera_params_path):
    if not os.path.exists(camera_params_path):
        print(f"DEBUG: Camera parameters file not found at: {camera_params_path}")
        raise FileNotFoundError(f"Camera parameters file not found: {camera_params_path}")

    print(f"DEBUG: Loading camera parameters from: {camera_params_path}")
    
    try:
        with open(camera_params_path, 'r') as f:
            camera_params = json.load(f)
        print(f"DEBUG: Loaded camera parameters: {camera_params}")
        return camera_params
    except Exception as e:
        print(f"DEBUG: Error loading camera parameters: {str(e)}")
        raise e

# Test script
folders = [str(i) for i in range(11)]
base_path = 'place_quality_inputs'

for folder in folders:
    cam_json_path = os.path.join(base_path, folder, 'cam.json')
    print(f"Testing folder: {folder}")
    try:
        load_camera_params(cam_json_path)
    except Exception as e:
        print(f"Error: {str(e)}")
    print()
