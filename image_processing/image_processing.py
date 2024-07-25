import os
import cv2
import numpy as np
import json
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R
from django.conf import settings

def load_images_and_camera_params(paths):
    color_image = cv2.imread(paths['color_image_path'])
    depth_image = cv2.imread(paths['depth_image_path'], cv2.IMREAD_UNCHANGED)
    with open(paths['camera_params'], 'r') as f:
        camera_params = json.load(f)
    return color_image, depth_image, camera_params

def depth_to_point_cloud(depth_image, camera_params):
    fx = camera_params['fx']
    fy = camera_params['fy']
    cx = camera_params['cx']
    cy = camera_params['cy']
    points = []
    for v in range(depth_image.shape[0]):
        for u in range(depth_image.shape[1]):
            z = depth_image[v, u] * 0.1  # Depth scale, adjust as necessary
            if z > 0:
                x = (u - cx) * z / fx
                y = (v - cy) * z / fy
                points.append((x, y, z))
    return np.array(points)

def detect_brick(color_image):
    height, width, _ = color_image.shape
    brick_center = (width // 2, height // 2)
    return brick_center

def calculate_normal_vector(points):
    v1 = points[1] - points[0]
    v2 = points[2] - points[0]
    normal_vector = np.cross(v1, v2)
    normal_vector = normal_vector / np.linalg.norm(normal_vector)
    return normal_vector

def calculate_euler_angles(normal_vector):
    z_axis = normal_vector
    if np.allclose(z_axis, [1, 0, 0]):
        x_axis = np.array([0, 1, 0])
    elif np.allclose(z_axis, [-1, 0, 0]):
        x_axis = np.array([0, -1, 0])
    else:
        x_axis = np.array([1, 0, 0])
    y_axis = np.cross(z_axis, x_axis)
    y_axis /= np.linalg.norm(y_axis)
    x_axis = np.cross(y_axis, z_axis)
    x_axis /= np.linalg.norm(x_axis)

    rotation_matrix = np.vstack([x_axis, y_axis, z_axis]).T
    r = R.from_matrix(rotation_matrix)
    euler_angles = r.as_euler('xyz', degrees=True)
    roll, pitch, yaw = euler_angles
    return {
        'yaw': yaw,
        'pitch': pitch,
        'roll': roll
    }

def estimate_pose(points):
    centroid = np.mean(points, axis=0)
    normal_vector = calculate_normal_vector(points)
    rotation = calculate_euler_angles(normal_vector)
    return centroid, rotation

def calculate_3d_pose(color_image, depth_image, camera_params):
    points = depth_to_point_cloud(depth_image, camera_params)
    centroid, rotation = estimate_pose(points)

    output_path = os.path.join(settings.MEDIA_ROOT, 'results', 'pose_visualization.png')
    visualize_pose(centroid, output_path)

    return centroid, rotation

def visualize_pose(translation, output_path):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(0, 0, 0, c='r', marker='o', label='Camera Origin')
    ax.scatter(*translation, c='b', marker='^', label='Estimated Brick Position')
    ax.plot([0, translation[0]], [0, translation[1]], [0, translation[2]], 'g--')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    ax.set_title('Estimated 3D Pose of the Brick')
    ax.legend()

    plt.savefig(output_path)
    plt.close(fig)

class PoseService:
    @staticmethod
    def process_image_files(color_image_path, depth_image_path, camera_params_path):
        try:
            # Load camera parameters from JSON file
            with open(camera_params_path, 'r') as f:
                camera_params = json.load(f)

            if isinstance(camera_params['dist_coeffs'], list):
                camera_params['dist_coeffs'] = np.array(camera_params['dist_coeffs'])

            # Process images and get results
            result = PoseService.process_images(color_image_path, depth_image_path, camera_params)

            # Convert numpy array to list for JSON serialization
            result['camera_params']['dist_coeffs'] = result['camera_params']['dist_coeffs'].tolist()

            return result
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def process_images(color_image_path, depth_image_path, camera_params):
        color_image = cv2.imread(color_image_path)
        depth_image = cv2.imread(depth_image_path, cv2.IMREAD_UNCHANGED)

        if color_image is None or depth_image is None:
            raise ValueError("Color or depth image could not be loaded.")

        # Detect the brick and estimate pose
        brick_center = (color_image.shape[1] // 2, color_image.shape[0] // 2)
        brick_depth = depth_image[brick_center[1], brick_center[0]] * 0.1  # Depth in mm

        # Convert 2D pixel coordinates to 3D coordinates
        x = (brick_center[0] - camera_params['px']) * brick_depth / camera_params['fx']
        y = (brick_center[1] - camera_params['py']) * brick_depth / camera_params['fy']
        z = brick_depth

        translation = [x, y, z]

        # Calculate normal vector and Euler angles
        points = [[x, y, z], [x + 0.01, y, z], [x, y + 0.01, z]]
        normal_vector = PoseService.calculate_normal_vector(points)
        rotation = PoseService.calculate_euler_angles(normal_vector)

        # Dummy image processing
        processed_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
        cv2.rectangle(color_image, (brick_center[0] - 50, brick_center[1] - 25), (brick_center[0] + 50, brick_center[1] + 25), (0, 255, 0), 2)

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
            'rotation': rotation,  # Rotation as a dictionary with yaw, pitch, roll
            'processed_image_path': processed_image_path
        }
        return result
