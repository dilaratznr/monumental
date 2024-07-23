# brickpose/views.py
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services.pose_service import PoseService
from django.shortcuts import render
import json
@csrf_exempt
def process_images_from_request(request):
    """
    Django request nesnesinden dosyaları alır ve poz tahmini işlemini gerçekleştirir.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

    color_image = request.FILES.get('color_image')
    depth_image = request.FILES.get('depth_image')
    camera_params = request.FILES.get('camera_params')

    if not color_image or not depth_image or not camera_params:
        return JsonResponse({'error': 'All three files (color image, depth image, and camera params) are required.'}, status=400)

    # Dosyaları geçici olarak kaydet
    color_image_path = 'temp_color.png'
    depth_image_path = 'temp_depth.png'
    camera_params_path = 'temp_cam.json'
    try:
        with open(color_image_path, 'wb+') as destination:
            for chunk in color_image.chunks():
                destination.write(chunk)
        with open(depth_image_path, 'wb+') as destination:
            for chunk in depth_image.chunks():
                destination.write(chunk)
        with open(camera_params_path, 'wb+') as destination:
            for chunk in camera_params.chunks():
                destination.write(chunk)

        # Poz tahminini gerçekleştir
        result = PoseService.process_image_files(color_image_path, depth_image_path, camera_params_path)

        # Geçici dosyaları sil
        os.remove(color_image_path)
        os.remove(depth_image_path)
        os.remove(camera_params_path)

        return JsonResponse(result)

    except Exception as e:
        if os.path.exists(color_image_path):
            os.remove(color_image_path)
        if os.path.exists(depth_image_path):
            os.remove(depth_image_path)
        if os.path.exists(camera_params_path):
            os.remove(camera_params_path)
        return JsonResponse({'error': str(e)}, status=500)
def display_results(request):
    # Örnek verilerle HTML şablonunu doldurmak için bir test verisi oluşturuyoruz.
    example_result = {
        'color_image_path': 'temp_color.png',
        'depth_image_path': 'temp_depth.png',
        'processed_image_mean_intensity': 105.7033190841195,
        'camera_params': {
            'width': 848,
            'height': 480,
            'fx': 434.5079345703125,
            'fy': 434.5079345703125,
            'px': 427.6170654296875,
            'py': 238.77597045898438,
            'dist_coeffs': [0.0, 0.0, 0.0, 0.0, 0.0]
        }
    }
    return render(request, 'result.html', {'result': example_result})