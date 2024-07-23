import os
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, 'media', 'place_quality_inputs')

for i in range(11):
    folder_path = os.path.join(MEDIA_DIR, str(i))
    print(f"\nTesting folder: {i}")
    
    color_image_path = os.path.join(folder_path, 'color.png')
    depth_image_path = os.path.join(folder_path, 'depth.png')
    cam_json_path = os.path.join(folder_path, 'cam.json')

    print(f"DEBUG: Checking existence of files in folder {i}:")
    print(f"  Color image: {color_image_path} - Exists: {os.path.exists(color_image_path)}")
    print(f"  Depth image: {depth_image_path} - Exists: {os.path.exists(depth_image_path)}")
    print(f"  Camera params: {cam_json_path} - Exists: {os.path.exists(cam_json_path)}")

    if not os.path.exists(color_image_path) or not os.path.exists(depth_image_path) or not os.path.exists(cam_json_path):
        continue

    with open(color_image_path, 'rb') as color_file, open(depth_image_path, 'rb') as depth_file, open(cam_json_path, 'r') as cam_file:
        files = {
            'color_image': color_file,
            'depth_image': depth_file,
            'camera_params': cam_file
        }
        response = requests.post('http://localhost:8000/api/process_image/', files=files)
        print(f"Folder {i}:")
        print(response.json())
        print(response.status_code)
