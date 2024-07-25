import json
import cv2
import numpy as np
from scipy.spatial.transform import Rotation as R
import os
from django.conf import settings

class PoseService:
    @staticmethod
    def process_image_files(color_image_path, depth_image_path, camera_params_path):
        try:
            # Kamera parametrelerini JSON dosyasından yükleyin
            with open(camera_params_path, 'r') as f:
                camera_params = json.load(f)
            
            print(f"DEBUG: Loaded camera parameters: {camera_params}")

            if isinstance(camera_params['dist_coeffs'], list):
                camera_params['dist_coeffs'] = np.array(camera_params['dist_coeffs'])

            # Görüntüleri işleyin ve sonuçları alın
            result = PoseService.process_images(color_image_path, depth_image_path, camera_params)
            
            # Kamera parametrelerindeki numpy dizisini listeye dönüştürün
            result['camera_params']['dist_coeffs'] = result['camera_params']['dist_coeffs'].tolist()
            
            return result
        except Exception as e:
            print(f"DEBUG: Error in process_image_files: {str(e)}")
            return {'error': str(e)}

    @staticmethod
    def process_images(color_image_path, depth_image_path, camera_params):
        color_image = cv2.imread(color_image_path)
        depth_image = cv2.imread(depth_image_path, cv2.IMREAD_UNCHANGED)

        if color_image is None or depth_image is None:
            raise ValueError("Color or depth image could not be loaded.")

        # Dummy brick detection and pose estimation (to be replaced with actual algorithm)
        brick_center = (color_image.shape[1] // 2, color_image.shape[0] // 2)
        brick_depth = depth_image[brick_center[1], brick_center[0]] * 0.1  # Depth in mm

        # 2D pixel coordinates to 3D coordinates conversion
        x = (brick_center[0] - camera_params['px']) * brick_depth / camera_params['fx']
        y = (brick_center[1] - camera_params['py']) * brick_depth / camera_params['fy']
        z = brick_depth

        translation = [x, y, z]

        # Calculate normal vector and Euler angles
        normal_vector = PoseService.calculate_normal_vector([[x, y, z], [x + 0.01, y, z], [x, y + 0.01, z]])
        rotation = PoseService.calculate_euler_angles(normal_vector)

        # Process the image (dummy processing)
        processed_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

        # Draw a rectangle around the detected brick (dummy visualization)
        cv2.rectangle(color_image, (brick_center[0] - 50, brick_center[1] - 25), (brick_center[0] + 50, brick_center[1] + 25), (0, 255, 0), 2)

        # Save the processed image in the results directory
        results_dir = os.path.join(settings.MEDIA_ROOT, 'results')
        os.makedirs(results_dir, exist_ok=True)
        processed_image_filename = os.path.basename(color_image_path).replace('_color.png', '_processed.png')
        processed_image_path = os.path.join(results_dir, processed_image_filename)
        cv2.imwrite(processed_image_path, color_image)

        result = {
            'color_image_path': color_image_path,
            'depth_image_path': depth_image_path,
            'processed_image_mean_intensity': np.mean(processed_image),
            'camera_params': camera_params,
            'translation': translation,
            'rotation': rotation,
            'processed_image_path': processed_image_path
        }
        return result

    @staticmethod
    def calculate_normal_vector(points):
        v1 = np.array(points[1]) - np.array(points[0])
        v2 = np.array(points[2]) - np.array(points[0])
        normal_vector = np.cross(v1, v2)
        normal_vector = normal_vector / np.linalg.norm(normal_vector)
        return normal_vector

    @staticmethod
    def calculate_euler_angles(normal_vector):
        # Normal vektöründen dönüş matrisini oluşturma
        z_axis = normal_vector
        x_axis = np.array([1, 0, 0]) if not np.allclose(z_axis, [1, 0, 0]) else np.array([0, 1, 0])
        y_axis = np.cross(z_axis, x_axis)
        y_axis /= np.linalg.norm(y_axis)
        x_axis = np.cross(y_axis, z_axis)
        x_axis /= np.linalg.norm(x_axis)

        rotation_matrix = np.vstack([x_axis, y_axis, z_axis]).T
        r = R.from_matrix(rotation_matrix)
        euler_angles = r.as_euler('xyz', degrees=True)
        return euler_angles
