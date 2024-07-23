# brickpose/views.py

import os
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .services.pose_service import PoseService
from django.conf import settings

@csrf_exempt
def process_images_from_request(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

    color_image = request.FILES.get('color_image')
    depth_image = request.FILES.get('depth_image')
    camera_params = request.FILES.get('camera_params')

    if not color_image or not depth_image or not camera_params:
        return JsonResponse({'error': 'All three files (color image, depth image, and camera params) are required.'}, status=400)

    unique_id = str(uuid.uuid4())
    color_image_path = os.path.join(settings.MEDIA_ROOT, f"{unique_id}_color.png")
    depth_image_path = os.path.join(settings.MEDIA_ROOT, f"{unique_id}_depth.png")
    camera_params_path = os.path.join(settings.MEDIA_ROOT, f"{unique_id}_cam.json")

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

        result = PoseService.process_image_files(color_image_path, depth_image_path, camera_params_path)
        result['color_image_path'] = f"{settings.MEDIA_URL}{unique_id}_color.png"
        result['depth_image_path'] = f"{settings.MEDIA_URL}{unique_id}_depth.png"
        result['processed_image_path'] = f"{settings.MEDIA_URL}results/{os.path.basename(result['processed_image_path'])}"

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
    folder_number = 0  # This can be dynamic based on your requirements
    
    color_image_path = f"place_quality_inputs/{folder_number}/color.png"
    depth_image_path = f"place_quality_inputs/{folder_number}/depth.png"
    processed_image_filename = "d659e799-33bd-4718-8a92-bf67be955106_processed.png"  # Adjust as needed
    processed_image_path = f"results/{processed_image_filename}"
    
    example_result = {
        'color_image_path': f"{settings.MEDIA_URL}{color_image_path}",
        'depth_image_path': f"{settings.MEDIA_URL}{depth_image_path}",
        'processed_image_path': f"{settings.MEDIA_URL}{processed_image_path}",
        'processed_image_mean_intensity': 105.7033190841195,  # Example value
        'camera_params': {
            'width': 848,
            'height': 480,
            'fx': 434.5079345703125,
            'fy': 434.5079345703125,
            'px': 427.6170654296875,
            'py': 238.77597045898438,
            'dist_coeffs': [0.0, 0.0, 0.0, 0.0, 0.0]
        },
        'translation': [100, 50, 25],  # Example value
        'rotation': [0, 90, 0]  # Example value
    }
    
    return render(request, 'result.html', {'result': example_result})
