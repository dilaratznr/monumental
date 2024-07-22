import os
import sys

# Proje dizinini Python yoluna ekleyin
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from brickpose.services.pose_service import PoseService  # PoseService sınıfını doğru şekilde import edin

# Test scripti
if __name__ == "__main__":
    print("Executing PoseService script")
    try:
        for i in range(11):  # Örneğin 11 klasör üzerinde test
            color_image_path = f'/Users/dilaratuzuner/Desktop/brick_pose_estimation/place_quality_inputs/{i}/color_image_{i}.png'
            depth_image_path = f'/Users/dilaratuzuner/Desktop/brick_pose_estimation/place_quality_inputs/{i}/depth_image_{i}.png'

            if not os.path.exists(color_image_path) or not os.path.exists(depth_image_path):
                print(f"Klasör {i} - Hata: Dosya yolları bulunamadı.")
                continue

            result = PoseService.process_image_files(color_image_path, depth_image_path)
            print(f"Klasör {i} - Sonuç: {result}")

    except Exception as e:
        print(f"Error occurred: {e}")
