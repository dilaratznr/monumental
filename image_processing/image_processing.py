import cv2
import numpy as np

def segment_brick(color_image):
    try:
        # Görüntüyü numpy array olarak oku
        color_image_np = np.frombuffer(color_image.read(), np.uint8)
        color_image_np = cv2.imdecode(color_image_np, cv2.IMREAD_COLOR)
        
        if color_image_np is None:
            raise ValueError("Görüntü yüklenemedi.")
        
        # Görüntüyü gri tonlamaya çevir
        gray_image = cv2.cvtColor(color_image_np, cv2.COLOR_BGR2GRAY)
        return gray_image
    except Exception as e:
        raise ValueError(f"Görüntü işleme hatası: {str(e)}")

def create_point_cloud(depth_image):
    try:
        # Derinlik görüntüsünü numpy array olarak oku
        depth_image_data = depth_image.read()
        depth_image_np = np.frombuffer(depth_image_data, np.uint16)
        
        # Derinlik görüntüsünün boyutunu kontrol et
        expected_width = 640
        expected_height = 480
        expected_size = expected_width * expected_height
        
        if depth_image_np.size != expected_size:
            raise ValueError(f"Derinlik görüntüsünün boyutları uyuşmuyor. Beklenen boyut: {expected_size}, Alınan boyut: {depth_image_np.size}")
        
        # Derinlik görüntüsünü şekillendir
        depth_image_np = depth_image_np.reshape((expected_height, expected_width))
        
        if depth_image_np is None:
            raise ValueError("Derinlik görüntüsü yüklenemedi.")
        
        # Derinlik görüntüsünden nokta bulutu oluştur (örnek kod)
        point_cloud = depth_image_np / 1000.0  # 0.1mm ölçeği
        return point_cloud
    except Exception as e:
        raise ValueError(f"Derinlik görüntüsü işleme hatası: {str(e)}")
