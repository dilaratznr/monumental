import requests

url = 'http://localhost:8000/process_image/'
files = {
    'color_image': open('place_quality_inputs/0/color.png', 'rb'),
    'depth_image': open('place_quality_inputs/0/depth.png', 'rb')
}
response = requests.post(url, files=files)
print(response.json())
