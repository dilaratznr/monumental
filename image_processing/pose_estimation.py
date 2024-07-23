import json
import os
import cv2

def load_images_and_camera_params(paths):
    # Load the color image
    color_image = cv2.imread(paths['color_image_path'])
    
    # Load the depth image
    depth_image = cv2.imread(paths['depth_image_path'], cv2.IMREAD_UNCHANGED)
    
    # Kamera parametreleri dosyasını kontrol edin ve yükleyin
    if not os.path.exists(paths['camera_params_path']):
        print(f"DEBUG: Camera parameters file not found at: {paths['camera_params_path']}")
        raise FileNotFoundError(f"Camera parameters file not found: {paths['camera_params_path']}")
    
    # Kamera parametreleri dosyasının yolunu yazdır
    print(f"DEBUG: Loading camera parameters from: {paths['camera_params_path']}")
    
    # Load the camera parameters
    try:
        with open(paths['camera_params_path'], 'r') as f:
            camera_params = json.load(f)
    except Exception as e:
        print(f"DEBUG: Error loading camera parameters: {str(e)}")
        raise e
    
    return color_image, depth_image, camera_params

def calculate_3d_pose(color_image, depth_image, camera_params):
    # Burada pose hesaplama işlemlerini gerçekleştirin
    # Örneğin:
    pose = [0, 0, 0, 0, 0, 0]  # Sadece örnek amaçlı, burada gerçek hesaplamalar yapılmalı
    return pose
