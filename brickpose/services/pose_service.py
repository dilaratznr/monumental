import json
import cv2
import numpy as np

from core import settings

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

        # Perform actual pose estimation here
        # Placeholder for the algorithm to estimate pose (position and orientation)
        processed_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

        # Example processed image path for visualization
        processed_image_path = 'processed_image.png'
        cv2.imwrite(processed_image_path, processed_image)

        # Placeholder results for demonstration
        translation = [100, 50, 30]  # Example translation in millimeters
        rotation = [10, 5, 2]  # Example rotation in degrees (roll, pitch, yaw)

        result = {
            'color_image_path': color_image_path,
            'depth_image_path': depth_image_path,
            'processed_image_mean_intensity': np.mean(processed_image),
            'camera_params': camera_params,
            'processed_image_path': f"{settings.MEDIA_URL}{processed_image_path}",
            'translation': translation,
            'rotation': rotation
        }
        return result
