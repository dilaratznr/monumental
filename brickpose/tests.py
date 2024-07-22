import os
import requests
import zipfile
import json

# ZIP dosyasını açın
with zipfile.ZipFile('place_quality_inputs.zip', 'r') as zip_ref:
    zip_ref.extractall('place_quality_inputs')

# Verileri işlemek için klasörleri dolaşın
for i in range(11):
    folder_path = os.path.join('place_quality_inputs', str(i))
    
    color_image_path = os.path.join(folder_path, 'color.png')
    depth_image_path = os.path.join(folder_path, 'depth.png')
    json_file_path = os.path.join(folder_path, 'data.json')

    # JSON dosyasını okuyun
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)

    # API endpoint'ine istek gönderin
    url = 'http://127.0.0.1:8000/api/process_image/'
    files = {
        'image': open(color_image_path, 'rb'),
        'depth_image': open(depth_image_path, 'rb')
    }

    response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Klasör {i} - Pozisyon: {result['position']}, Yönelim: {result['orientation']}")
    else:
        print(f"Klasör {i} - Hata: {response.json()}")
