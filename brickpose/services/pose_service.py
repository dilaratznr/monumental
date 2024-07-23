# brickpose/services/pose_service.py

import json
import cv2
import numpy as np

class PoseService:
    @staticmethod
    def process_image_files(color_image_path, depth_image_path, camera_params_path):
        try:
            with open(camera_params_path, 'r') as f:
                camera_params = json.load(f)
                
            print(f"DEBUG: Loaded camera parameters: {camera_params}")

            if isinstance(camera_params['dist_coeffs'], list):
                camera_params['dist_coeffs'] = np.array(camera_params['dist_coeffs'])

            result = PoseService.process_images(color_image_path, depth_image_path, camera_params)
            
            result['camera_params']['dist_coeffs'] = result['camera_params']['dist_coeffs'].tolist()
            
            return result
        except Exception as e:
            print(f"DEBUG: Error in process_image_files: {str(e)}")
            return {'error': str(e)}

    @staticmethod
    def process_images(color_image_path, depth_image_path, camera_params):
        color_image = cv2.imread(color_image_path)
        depth_image = cv2.imread(depth_image_path, cv2.IMREAD_UNCHANGED)

        # Burada gerçek görüntü işleme kodunu ekleyin
        # Örneğin, bazı basit işleme adımları:
        processed_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

        result = {
            'color_image_path': color_image_path,
            'depth_image_path': depth_image_path,
            'processed_image_mean_intensity': np.mean(processed_image),
            'camera_params': camera_params
        }
        return result
