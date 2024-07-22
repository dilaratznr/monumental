import cv2
import numpy as np
from core.config import Config

class ImageRepository:
    @staticmethod
    def load_images(rgb_stream, depth_stream):
        rgb_image = cv2.imdecode(np.frombuffer(rgb_stream.read(), np.uint8), cv2.IMREAD_COLOR)
        depth_image = cv2.imdecode(np.frombuffer(depth_stream.read(), np.uint8), cv2.IMREAD_UNCHANGED)
        depth_image = depth_image.astype(np.float32) * Config.DEPTH_SCALE  # Convert to mm
        return rgb_image, depth_image
