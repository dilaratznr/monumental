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
    height, width = depth_image.shape
    center_x, center_y = width // 2, height // 2
    region_size = 100
    region = depth_image[center_y - region_size:center_y + region_size,
                         center_x - region_size:center_x + region_size]
    
    min_val, max_val = np.min(region), np.max(region)
    if max_val == min_val:
        print("No variation in depth values, returning.")
        return None, (center_x, center_y)
    
    normalized_region = (region - min_val) / (max_val - min_val) * 255
    normalized_region = np.uint8(normalized_region)
    
    _, thresholded = cv2.threshold(normalized_region, 50, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    print(f"Contours found: {len(contours)}")
    if contours:
        largest_contour = None
        max_area = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            x, y, w, h = cv2.boundingRect(contour)
            print(f"Contour area: {area}, Bounding box: x={x}, y={y}, w={w}, h={h}")

            if (center_x - region_size / 2 < x + w / 2 < center_x + region_size / 2) and \
               (center_y - region_size / 2 < y + h / 2 < center_y + region_size / 2):
                aspect_ratio = float(w) / h
                if 0.5 < aspect_ratio < 2.0:
                    if area > max_area:
                        max_area = area
                        largest_contour = contour
        
        if largest_contour is not None:
            x, y, w, h = cv2.boundingRect(largest_contour)
            print(f"Detected Brick Center: ({x + w // 2}, {y + h // 2})")
            print(f"Bounding Box: x={x}, y={y}, w={w}, h={h}")
            return largest_contour, (x + w // 2, y + h // 2)
    
    print("No suitable contour found.")
    return None, (center_x, center_y)

def draw_brick_boundaries(image, contour, center, translation, rotation):
    # Draw the contour if available
    if contour is not None:
        cv2.drawContours(image, [contour], -1, (0, 255, 0), 2)
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Always mark the center and display coordinates
    cv2.circle(image, center, 5, (0, 0, 255), -1)
    center_coords = f"Center: ({center[0]}, {center[1]})"
    cv2.putText(image, center_coords, (center[0] + 10, center[1] - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    # Display 3D Pose Information
    pose_text = (f"Translation (mm): x={translation[0]:.2f}, y={translation[1]:.2f}, z={translation[2]:.2f}\n"
                 f"Rotation (degrees): yaw={rotation['yaw']:.2f}, pitch={rotation['pitch']:.2f}, roll={rotation['roll']:.2f}")
    y_offset = center[1] + 20
    for i, line in enumerate(pose_text.split('\n')):
        cv2.putText(image, line, (10, y_offset + i * 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    print("Drawing completed. Center coordinates:", center_coords)
    print("3D Pose Information:", pose_text)

    # Visualization of the Estimated 3D Pose
    # Draw translation vector as an arrow
    origin = (int(center[0]), int(center[1]))
    translation_vector = (int(center[0] + translation[0] * 10), int(center[1] - translation[1] * 10))
    cv2.arrowedLine(image, origin, translation_vector, (255, 255, 0), 2, tipLength=0.3)

    # Visualize rotation using small arrows
    rotation_vectors = {
        'yaw': (np.cos(np.radians(rotation['yaw'])), np.sin(np.radians(rotation['yaw']))),
        'pitch': (np.cos(np.radians(rotation['pitch'])), np.sin(np.radians(rotation['pitch']))),
        'roll': (np.cos(np.radians(rotation['roll'])), np.sin(np.radians(rotation['roll'])))
    }

    # Drawing the rotation vectors
    for angle_name, vector in rotation_vectors.items():
        end_point = (int(center[0] + vector[0] * 50), int(center[1] + vector[1] * 50))
        cv2.arrowedLine(image, origin, end_point, (0, 255, 255), 2, tipLength=0.3)
        cv2.putText(image, angle_name, end_point, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)

    print("3D Pose Visualization drawn on image.")

def calculate_3d_pose(depth_image, camera_params):
    fx = camera_params['fx']
    fy = camera_params['fy']
    cx = camera_params['px']
    cy = camera_params['py']

    height, width = depth_image.shape
    center_x, center_y = width // 2, height // 2

    depth_value = depth_image[center_y, center_x] * 0.1

    x = (center_x - cx) * depth_value / fx
    y = (center_y - cy) * depth_value / fy
    z = depth_value
    translation = [x, y, z]

    offsets = [(-10, -10), (10, -10), (-10, 10), (10, 10)]
    points_3d = []

    for dx, dy in offsets:
        depth = depth_image[center_y + dy, center_x + dx] * 0.1
        x_offset = (center_x + dx - cx) * depth / fx
        y_offset = (center_y + dy - cy) * depth / fy
        z_offset = depth
        points_3d.append([x_offset, y_offset, z_offset])

    points_3d = np.array(points_3d)
    v1 = points_3d[1] - points_3d[0]
    v2 = points_3d[2] - points_3d[0]
    normal_vector = np.cross(v1, v2)
    normal_vector /= np.linalg.norm(normal_vector)

    forward_vector = np.array([0, 0, 1])
    rotation_vector = np.cross(forward_vector, normal_vector)
    rotation_angle = np.arcsin(np.linalg.norm(rotation_vector))
    rotation_axis = rotation_vector / np.linalg.norm(rotation_vector)

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

    normalized_depth = cv2.normalize(depth_image, None, 0, 255, cv2.NORM_MINMAX)
    normalized_depth = np.uint8(normalized_depth)
    color_mapped_depth = cv2.applyColorMap(normalized_depth, cv2.COLORMAP_JET)

    # Create RGB-D image by overlaying depth map on color image
    alpha = 0.6
    rgbd_image = cv2.addWeighted(color_image, alpha, color_mapped_depth, 1 - alpha, 0)

    # Detect the brick and highlight it in the processed image
    brick_contour, center = detect_brick_in_center(depth_image)
    processed_image = color_image.copy()  # Use the original color image for drawing

    # Calculate 3D pose
    translation, rotation = calculate_3d_pose(depth_image, camera_params)

    if brick_contour is not None:
        draw_brick_boundaries(processed_image, brick_contour, center, translation, rotation)
    else:
        cv2.circle(processed_image, center, 10, (0, 0, 255), 2)  # Mark center if no contour found
        center_coords = f"Center: ({center[0]}, {center[1]})"
        cv2.putText(processed_image, center_coords, (center[0] + 10, center[1] - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        # Display 3D Pose Information
        pose_text = (f"Translation (mm): x={translation[0]:.2f}, y={translation[1]:.2f}, z={translation[2]:.2f}\n"
                     f"Rotation (degrees): yaw={rotation['yaw']:.2f}, pitch={rotation['pitch']:.2f}, roll={rotation['roll']:.2f}")
        y_offset = center[1] + 20
        for i, line in enumerate(pose_text.split('\n')):
            cv2.putText(processed_image, line, (10, y_offset + i * 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        # Visualization of the Estimated 3D Pose
        # Draw translation vector as an arrow
        origin = (int(center[0]), int(center[1]))
        translation_vector = (int(center[0] + translation[0] * 10), int(center[1] - translation[1] * 10))
        cv2.arrowedLine(processed_image, origin, translation_vector, (255, 255, 0), 2, tipLength=0.3)

        # Visualize rotation using small arrows
        rotation_vectors = {
            'yaw': (np.cos(np.radians(rotation['yaw'])), np.sin(np.radians(rotation['yaw']))),
            'pitch': (np.cos(np.radians(rotation['pitch'])), np.sin(np.radians(rotation['pitch']))),
            'roll': (np.cos(np.radians(rotation['roll'])), np.sin(np.radians(rotation['roll'])))
        }

        # Drawing the rotation vectors
        for angle_name, vector in rotation_vectors.items():
            end_point = (int(center[0] + vector[0] * 50), int(center[1] + vector[1] * 50))
            cv2.arrowedLine(processed_image, origin, end_point, (0, 255, 255), 2, tipLength=0.3)
            cv2.putText(processed_image, angle_name, end_point, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)

    results_dir = os.path.join(settings.MEDIA_ROOT, 'results')
    os.makedirs(results_dir, exist_ok=True, mode=0o755)
    
    rgbd_image_path = os.path.join(results_dir, f'{os.path.basename(folder_path)}_rgbd.png')
    processed_image_path = os.path.join(results_dir, f'{os.path.basename(folder_path)}_processed.png')
    pose_visualization_path = os.path.join(results_dir, f'{os.path.basename(folder_path)}_pose_visualization.png')

    # Save images
    cv2.imwrite(rgbd_image_path, rgbd_image)
    cv2.imwrite(processed_image_path, processed_image)
    cv2.imwrite(pose_visualization_path, processed_image)

    # Return the paths and pose information
    return rgbd_image_path, processed_image_path, pose_visualization_path, np.mean(rgbd_image), translation, rotation
