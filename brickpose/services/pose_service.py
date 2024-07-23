# brickpose/services/pose_service.py

import json
import numpy as np

class PoseService:
    @staticmethod
    def process_image_files(color_image_path, depth_image_path, camera_params_path):
        try:
            with open(camera_params_path, 'r') as f:
                camera_params = json.load(f)
                
            # Debugging camera parameters
            print(f"DEBUG: Loaded camera parameters: {camera_params}")

            # Assuming that `camera_params['dist_coeffs']` is the source of the error
            if isinstance(camera_params['dist_coeffs'], list):
                print("DEBUG: Converting dist_coeffs list to NumPy array")
                camera_params['dist_coeffs'] = np.array(camera_params['dist_coeffs'])

            # Process the images here
            result = PoseService.dummy_process(color_image_path, depth_image_path, camera_params)
            
            # Convert NumPy arrays back to lists before returning the result
            result['camera_params']['dist_coeffs'] = result['camera_params']['dist_coeffs'].tolist()
            
            return result
        except Exception as e:
            print(f"DEBUG: Error in process_image_files: {str(e)}")
            return {'error': str(e)}

    @staticmethod
    def dummy_process(color_image_path, depth_image_path, camera_params):
        # This function would contain the actual image processing code.
        # For demonstration purposes, we'll return a mock result.
        result = {
            'color_image_path': color_image_path,
            'depth_image_path': depth_image_path,
            'camera_params': camera_params
        }
        return result
