import os
import cv2
import numpy as np
import json
from scipy.spatial.transform import Rotation as R
from django.conf import settings
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

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
        bounding_box_coords = f"Bounding Box: x={x}, y={y}, w={w}, h={h}"
        # Green text with a black outline for better readability
        cv2.putText(image, bounding_box_coords, (x, y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(image, bounding_box_coords, (x, y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

    # Mark the center and display coordinates
    cv2.circle(image, center, 5, (0, 0, 255), -1)
    center_coords = f"Center: ({center[0]}, {center[1]})"
    # Green text with a black outline for better readability
    cv2.putText(image, center_coords, (center[0] + 10, center[1] - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(image, center_coords, (center[0] + 10, center[1] - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

    # Display 3D Pose Information
    pose_text = (f"Translation (mm): x={translation[0]:.2f}, y={translation[1]:.2f}, z={translation[2]:.2f}\n"
                 f"Rotation (degrees): yaw={rotation['yaw']:.2f}, pitch={rotation['pitch']:.2f}, roll={rotation['roll']:.2f}")
    y_offset = center[1] + 30  # Adjusted for better spacing
    for i, line in enumerate(pose_text.split('\n')):
        # Green text with a black outline for better readability
        cv2.putText(image, line, (10, y_offset + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(image, line, (10, y_offset + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

    print("Drawing completed. Center coordinates:", center_coords)
    print("3D Pose Information:", pose_text)

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

def visualize_3d_pose(translation, rotation, save_path):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot the translation point
    ax.scatter(translation[0], translation[1], translation[2], color='r', label='Translation')
    ax.text(translation[0], translation[1], translation[2], 
            f"({translation[0]:.2f}, {translation[1]:.2f}, {translation[2]:.2f})",
            color='red', fontsize=10, ha='right')

    # Plot the rotation vectors (Yaw, Pitch, Roll)
    rotation_angles = [rotation['yaw'], rotation['pitch'], rotation['roll']]
    labels = ['Yaw', 'Pitch', 'Roll']
    colors = ['g', 'b', 'm']
    length = 50  # Vector length scale

    # Apply each rotation separately
    yaw_vector = R.from_euler('z', rotation['yaw'], degrees=True).apply([1, 0, 0])
    pitch_vector = R.from_euler('y', rotation['pitch'], degrees=True).apply([0, 1, 0])
    roll_vector = R.from_euler('x', rotation['roll'], degrees=True).apply([0, 0, 1])

    vectors = [yaw_vector, pitch_vector, roll_vector]

    for vector, label, color, angle in zip(vectors, labels, colors, rotation_angles):
        ax.quiver(translation[0], translation[1], translation[2], 
                  vector[0], vector[1], vector[2], 
                  color=color, length=length, normalize=True, label=f"{label} ({angle:.2f}°)")
        end_point = translation + vector * length
        ax.text(end_point[0], end_point[1], end_point[2], 
                f"{label}: {angle:.2f}°", color=color, fontsize=10, ha='center')

    # Set labels and title
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')
    ax.legend()

    plt.title('Estimated 3D Pose Visualization')
    plt.savefig(save_path)
    plt.close()
def process_images_and_save_rgbd(folder_path):
    color_image_path = os.path.join(folder_path, 'color.png')
    depth_image_path = os.path.join(folder_path, 'depth.png')
    camera_params_path = os.path.join(folder_path, 'cam.json')
    
    color_image, depth_image, camera_params = load_images_and_camera_params(
        color_image_path, depth_image_path, camera_params_path)
    
    if color_image is None or depth_image is None:
        print("Error: One or both images could not be loaded.")
        return None, None, None, None, None

    # Normalize the depth image and apply color mapping
    depth_min, depth_max = depth_image.min(), depth_image.max()
    if depth_max == depth_min:
        depth_max += 1  # Avoid division by zero
    normalized_depth = cv2.normalize(depth_image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    color_mapped_depth = cv2.applyColorMap(normalized_depth, cv2.COLORMAP_JET)

    # Create RGB-D image by overlaying the color-mapped depth image onto the original color image
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
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(processed_image, center_coords, (center[0] + 10, center[1] - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
        # Display 3D Pose Information
        pose_text = (f"Translation (mm): x={translation[0]:.2f}, y={translation[1]:.2f}, z={translation[2]:.2f}\n"
                     f"Rotation (degrees): yaw={rotation['yaw']:.2f}, pitch={rotation['pitch']:.2f}, roll={rotation['roll']:.2f}")
        y_offset = center[1] + 30
        for i, line in enumerate(pose_text.split('\n')):
            cv2.putText(processed_image, line, (10, y_offset + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 3, cv2.LINE_AA)
            cv2.putText(processed_image, line, (10, y_offset + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

    results_dir = os.path.join(settings.MEDIA_ROOT, 'results')
    os.makedirs(results_dir, exist_ok=True, mode=0o755)
    
    rgbd_image_path = os.path.join(results_dir, f'{os.path.basename(folder_path)}_rgbd.png')
    processed_image_path = os.path.join(results_dir, f'{os.path.basename(folder_path)}_processed.png')
    pose_visualization_path = os.path.join(results_dir, f'{os.path.basename(folder_path)}_pose_visualization.png')

    # Save images
    cv2.imwrite(rgbd_image_path, rgbd_image)
    cv2.imwrite(processed_image_path, processed_image)

    # Visualize 3D Pose with Matplotlib
    visualize_3d_pose(translation, rotation, pose_visualization_path)

    # Return the paths and pose information
    return rgbd_image_path, processed_image_path, pose_visualization_path, np.mean(normalized_depth), translation, rotation
