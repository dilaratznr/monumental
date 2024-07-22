import numpy as np
from brickpose.utils.image_processing import segment_brick, create_point_cloud

class PoseService:
    @staticmethod
    def estimate_pose(points):
        centroid = np.mean(points, axis=0)
        normalized_points = points - centroid
        u, s, vh = np.linalg.svd(normalized_points)
        normal = vh[2, :]
        
        return centroid, normal

    @staticmethod
    def process_image(rgb_image, depth_image):
        segmented_depth, _ = segment_brick(rgb_image, depth_image)
        if segmented_depth is None:
            return None, None
        
        points, _ = create_point_cloud(rgb_image, segmented_depth)
        position, orientation = PoseService.estimate_pose(points)
        
        return position, orientation
