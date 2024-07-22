import os
import cv2
import numpy as np

# Helper functions
def segment_brick(color_image):
    gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    return mask

def create_point_cloud(depth_image, mask):
    mask = cv2.resize(mask, (depth_image.shape[1], depth_image.shape[0]), interpolation=cv2.INTER_NEAREST)
    masked_depth = np.where(mask, depth_image, 0)
    point_cloud = np.dstack((masked_depth, masked_depth, masked_depth))
    return point_cloud

class PoseService:
    def process_image(self, color_image, depth_image):
        print("Called process_image")
        color_image_array = np.frombuffer(color_image.read(), np.uint8)
        color_image_np = cv2.imdecode(color_image_array, cv2.IMREAD_COLOR)
        if color_image_np is None:
            raise ValueError("Color image could not be decoded")

        depth_image_array = np.frombuffer(depth_image.read(), np.uint16)

        print(f"Color image shape: {color_image_np.shape}")
        print(f"Depth image array size: {depth_image_array.size}")
        print(f"Depth image array dtype: {depth_image_array.dtype}")

        expected_size = 480 * 640
        actual_size = depth_image_array.size
        if actual_size != expected_size:
            print(f"Depth image size mismatch. Expected size: {expected_size}, but got size: {actual_size}")
            depth_image_array = self.resize_depth_image(depth_image_array, actual_size, expected_size)

        depth_image_np = depth_image_array.reshape((480, 640))
        depth_image_np = depth_image_np * 0.1

        brick_mask = segment_brick(color_image_np)
        point_cloud = create_point_cloud(depth_image_np, brick_mask)
        position, orientation = self.calculate_pose(point_cloud)

        return position, orientation

    def resize_depth_image(self, depth_image_array, actual_size, expected_size):
        print("Called resize_depth_image")
        if actual_size % 2 != 0:
            depth_image_array = depth_image_array[:-1]
            actual_size -= 1

        new_height = 480
        new_width = actual_size // new_height // 2
        return depth_image_array.reshape((new_height, new_width))

    def calculate_pose(self, point_cloud):
        print("Called calculate_pose")
        # Burada gerçek poz hesaplama mantığını ekleyin (örneğin, cv2.solvePnP)
        position = [0, 0, 0]  # Geçici değerler
        orientation = [0, 0, 0]  # Geçici değerler
        return position, orientation

def process_images_in_folders():
    base_folder = "place_quality_inputs"
    for folder_num in range(11):
        folder_path = os.path.join(base_folder, str(folder_num))
        color_image_path = os.path.join(folder_path, "color.png")
        depth_image_path = os.path.join(folder_path, "depth.png")

        try:
            with open(color_image_path, 'rb') as color_image, open(depth_image_path, 'rb') as depth_image:
                service = PoseService()
                position, orientation = service.process_image(color_image, depth_image)
                print(f"Klasör {folder_num} - Position: {position}, Orientation: {orientation}")
        except Exception as e:
            print(f"Klasör {folder_num} - Hata: {e}")

if __name__ == "__main__":
    process_images_in_folders()
