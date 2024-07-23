import os
import requests

# Base URL of your Django server
base_url = 'http://localhost:8000/api/process_image/'

# Folder paths
folders = [str(i) for i in range(11)]
base_path = 'place_quality_inputs'

for folder in folders:
    print(f"Testing folder: {folder}")
    
    # Dosya yollarını tam olarak belirtelim
    color_image_path = os.path.join(base_path, folder, 'color.png')
    depth_image_path = os.path.join(base_path, folder, 'depth.png')
    cam_json_path = os.path.join(base_path, folder, 'cam.json')

    # Bu dosyaların var olup olmadığını kontrol edelim
    print(f"DEBUG: Checking existence of files in folder {folder}:")
    print(f"  Color image: {color_image_path} - Exists: {os.path.exists(color_image_path)}")
    print(f"  Depth image: {depth_image_path} - Exists: {os.path.exists(depth_image_path)}")
    print(f"  Camera params: {cam_json_path} - Exists: {os.path.exists(cam_json_path)}")

    with open(color_image_path, 'rb') as color_file, open(depth_image_path, 'rb') as depth_file, open(cam_json_path, 'r') as cam_file:
        response = requests.post(base_url, files={
            'color_image': color_file,
            'depth_image': depth_file,
            'camera_params': cam_file
        })

    print(f"Folder {folder}:")
    try:
        print(response.json())
    except requests.exceptions.JSONDecodeError:
        print("Response is not in JSON format")
        print(f"Response content: {response.content}")
    print(response.status_code)
    print()
