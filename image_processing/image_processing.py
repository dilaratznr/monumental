import os
import cv2
import numpy as np
import json
from scipy.spatial.transform import Rotation as R
from django.conf import settings

def load_images_and_camera_params(color_image_path, depth_image_path, camera_params_path):
    color_image = cv2.imread(color_image_path)
    depth_image = cv2.imread(depth_image_path, cv2.IMREAD_UNCHANGED)
    with open(camera_params_path, 'r') as f:
        camera_params = json.load(f)
    return color_image, depth_image, camera_params

def detect_brick_in_center(depth_image):
    """Detects the brick in the center of the image based on depth information."""
    height, width = depth_image.shape
    center_x, center_y = width // 2, height // 2
    region_size = 100  # Size of the region to search for the brick
    region = depth_image[center_y - region_size:center_y + region_size,
                         center_x - region_size:center_x + region_size]
    
    # Example processing: Find contours in this region
    _, thresholded = cv2.threshold(region, 1, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresholded.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        # Assume the largest contour is the brick
        largest_contour = max(contours, key=cv2.contourArea)
        return largest_contour, (center_x, center_y)
    return None, (center_x, center_y)
def calculate_3d_pose(depth_image, camera_params):
    # Get the camera parameters
    fx = camera_params['fx']
    fy = camera_params['fy']
    cx = camera_params['px']
    cy = camera_params['py']

    # Assuming the brick is in the center of the image
    height, width = depth_image.shape
    center_x, center_y = width // 2, height // 2

    # Extract the depth value at the center
    depth_value = depth_image[center_y, center_x] * 0.1  # Convert to mm assuming depth scale is 0.1

    # Calculate the 3D position (translation) of the brick
    x = (center_x - cx) * depth_value / fx
    y = (center_y - cy) * depth_value / fy
    z = depth_value
    translation = [x, y, z]

    # Detecting more points around the center for better rotation estimation
    # You can customize the size and points used based on your requirements
    offsets = [(-10, -10), (10, -10), (-10, 10), (10, 10)]
    points_3d = []

    for dx, dy in offsets:
        depth = depth_image[center_y + dy, center_x + dx] * 0.1
        x_offset = (center_x + dx - cx) * depth / fx
        y_offset = (center_y + dy - cy) * depth / fy
        z_offset = depth
        points_3d.append([x_offset, y_offset, z_offset])

    # Compute the normal vector using points
    points_3d = np.array(points_3d)
    v1 = points_3d[1] - points_3d[0]
    v2 = points_3d[2] - points_3d[0]
    normal_vector = np.cross(v1, v2)
    normal_vector /= np.linalg.norm(normal_vector)

    # Calculate the rotation angles (yaw, pitch, roll) from the normal vector
    # Using the z-axis as the forward vector for comparison
    forward_vector = np.array([0, 0, 1])
    rotation_vector = np.cross(forward_vector, normal_vector)
    rotation_angle = np.arcsin(np.linalg.norm(rotation_vector))
    rotation_axis = rotation_vector / np.linalg.norm(rotation_vector)

    # Convert rotation to Euler angles
    rotation = R.from_rotvec(rotation_angle * rotation_axis).as_euler('xyz', degrees=True)
    rotation_dict = {'yaw': rotation[0], 'pitch': rotation[1], 'roll': rotation[2]}

    return translation, rotation_dict



def process_images_and_save_rgbd(folder_path):
    color_image_path = os.path.join(folder_path, 'color.png')
    depth_image_path = os.path.join(folder_path, 'depth.png')
    camera_params_path = os.path.join(folder_path, 'cam.json')
    
    color_image, depth_image, camera_params = load_images_and_camera_params(
        color_image_path, depth_image_path, camera_params_path)
    
    if color_image is None or depth_image is None:
        print("Error: One or both images could not be loaded.")
        return None, None, None, None, None

    # Normalize depth values for visualization
    normalized_depth = cv2.normalize(depth_image, None, 0, 255, cv2.NORM_MINMAX)
    normalized_depth = np.uint8(normalized_depth)
    color_mapped_depth = cv2.applyColorMap(normalized_depth, cv2.COLORMAP_JET)

    # Overlay depth map on color image (RGB-D representation)
    alpha = 0.6
    rgbd_image = cv2.addWeighted(color_image, alpha, color_mapped_depth, 1 - alpha, 0)

    # Detect the brick and highlight it in the processed image
    brick_contour, (center_x, center_y) = detect_brick_in_center(depth_image)
    processed_image = color_image.copy()
    if brick_contour is not None:
        cv2.drawContours(processed_image, [brick_contour], -1, (0, 255, 0), 2)
    else:
        cv2.circle(processed_image, (center_x, center_y), 10, (0, 0, 255), 2)  # Mark center if no contour found

    results_dir = os.path.join(settings.MEDIA_ROOT, 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    rgbd_image_path = os.path.join(results_dir, f'{os.path.basename(folder_path)}_rgbd.png')
    processed_image_path = os.path.join(results_dir, f'{os.path.basename(folder_path)}_processed.png')

    cv2.imwrite(rgbd_image_path, rgbd_image)
    cv2.imwrite(processed_image_path, processed_image)

    processed_image_mean_intensity = np.mean(rgbd_image)

    # Calculate 3D pose
    translation, rotation = calculate_3d_pose(depth_image, camera_params)

    return rgbd_image_path, processed_image_path, processed_image_mean_intensity, translation, rotation
