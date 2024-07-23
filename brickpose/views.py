import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services.pose_service import PoseService

@csrf_exempt
def process_images_from_request(request):
    """
    Django request nesnesinden dosyaları alır ve poz tahmini işlemini gerçekleştirir.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

    color_image = request.FILES.get('color_image')
    depth_image = request.FILES.get('depth_image')
    camera_params_file = request.FILES.get('camera_params')

    if not color_image or not depth_image or not camera_params_file:
        return JsonResponse({'error': 'Color image, depth image and camera parameters file are required.'}, status=400)

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
            for chunk in camera_params_file.chunks():
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
        print(f"DEBUG: Internal server error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
