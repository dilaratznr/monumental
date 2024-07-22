import cv2
import numpy as np
from PIL import Image

# Helper functions
def segment_brick(color_image):
    gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    return mask

def create_point_cloud(depth_image, mask):
    print(f"Depth image shape: {depth_image.shape}")
    print(f"Mask shape: {mask.shape}")
    # Ensure mask and depth image have the same shape
    if depth_image.shape != mask.shape:
        print(f"Resizing mask from {mask.shape} to match depth image shape {depth_image.shape}")
        mask = cv2.resize(mask, (depth_image.shape[1], depth_image.shape[0]), interpolation=cv2.INTER_NEAREST)
    masked_depth = np.where(mask, depth_image, 0)
    point_cloud = np.dstack((masked_depth, masked_depth, masked_depth))  # Example point cloud
    return point_cloud

class PoseService:
    def process_image(self, color_image, depth_image):
        print("Called process_image")

        # Convert images to numpy arrays
        color_image_np = np.array(color_image)
        depth_image_np = np.array(depth_image)

        # Debugging information
        print(f"Color image shape: {color_image_np.shape}")
        print(f"Depth image shape: {depth_image_np.shape}")

        # Expected dimensions
        expected_height = 480
        expected_width = 640

        if depth_image_np.shape != (expected_height, expected_width):
            raise ValueError(f"Depth image shape mismatch. Expected: {(expected_height, expected_width)}, but got: {depth_image_np.shape}")

        # Segment the brick
        brick_mask = segment_brick(color_image_np)

        # Create point cloud
        point_cloud = create_point_cloud(depth_image_np, brick_mask)

        # Calculate pose
        position, orientation = self.calculate_pose(point_cloud)

        return position, orientation

    def resize_depth_image(self, depth_image_array, actual_size, expected_size):
        print("Called resize_depth_image")
        # Ensure buffer size is multiple of element size (2 bytes for uint16)
        if actual_size % 2 != 0:
            raise ValueError(f"Buffer size must be a multiple of element size. Actual size: {actual_size}")

        # Calculate new dimensions for resizing
        new_height = 480
        new_width = 640  # Since we know our expected dimensions
        print(f"Resizing depth image from actual size {actual_size} to expected size {expected_size} with shape ({new_height}, {new_width})")

        # Safely resize depth image
        depth_image_resized = np.resize(depth_image_array, (new_height, new_width))
        return depth_image_resized

    def calculate_pose(self, point_cloud):
        print("Called calculate_pose")
        # Placeholder for pose calculation logic
        position = [0, 0, 0]
        orientation = [0, 0, 0]
        return position, orientation

    @staticmethod
    def process_image_files(color_image_path, depth_image_path):
        """
        Dosya yollarından renk ve derinlik görüntülerini alır, işler ve sonuçları döndürür.
        """
        try:
            # Pillow ile resimleri aç
            color_image = Image.open(color_image_path)
            depth_image = Image.open(depth_image_path)

            # Hizmeti başlat ve görüntüyü işle
            service = PoseService()
            position, orientation = service.process_image(color_image, depth_image)

            return {'position': position, 'orientation': orientation}

        except Exception as e:
            return {'error': str(e)}  # Hata durumunda hata mesajını döndür
