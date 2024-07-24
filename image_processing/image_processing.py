import os
import cv2
from django.conf import settings
import numpy as np
import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def load_images_and_camera_params(paths):
    color_image = cv2.imread(paths['color_image_path'])
    depth_image = cv2.imread(paths['depth_image_path'], cv2.IMREAD_UNCHANGED)
    with open(paths['camera_params'], 'r') as f:
        camera_params = json.load(f)
    return color_image, depth_image, camera_params

def calculate_3d_pose(color_image, depth_image, camera_params):
    # Extract intrinsic parameters
    fx = camera_params['fx']
    fy = camera_params['fy']
    cx = camera_params['cx']
    cy = camera_params['cy']

    # Convert depth to 3D points
    points = []
    for v in range(depth_image.shape[0]):
        for u in range(depth_image.shape[1]):
            z = depth_image[v, u] * 0.1  # Depth scale
            if z > 0:
                x = (u - cx) * z / fx
                y = (v - cy) * z / fy
                points.append([x, y, z])
    
    points = np.array(points)
    
    # Estimate the pose of the brick (simplified example)
    centroid = np.mean(points, axis=0)

    # Görselleştirme işlemi
    visualize_pose(centroid)
    
    
    output_path = os.path.join(settings.MEDIA_ROOT, 'results', 'pose_visualization.png')
    visualize_pose(centroid, output_path)

    return centroid
def visualize_pose(translation):
    # Görsel dosyasının kaydedileceği yol
    output_path = os.path.join(settings.MEDIA_ROOT, 'results', 'pose_visualization.png')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

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

    return output_path  # Kaydedilen dosyanın yolunu döndür