# image_processing/pose_estimation.py

import cv2
import numpy as np
import json

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
            z = depth_image[v, u] * 0.1
            if z > 0:
                x = (u - cx) * z / fx
                y = (v - cy) * z / fy
                points.append([x, y, z])
    
    points = np.array(points)
    
    # Estimate the pose of the brick (simplified example)
    centroid = np.mean(points, axis=0)
    return centroid
