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

    if not color_image or not depth_image:
        return JsonResponse({'error': 'Both color and depth images are required.'}, status=400)

    # Dosyaları geçici olarak kaydet
    color_image_path = 'temp_color.png'
    depth_image_path = 'temp_depth.png'
    try:
        with open(color_image_path, 'wb+') as destination:
            for chunk in color_image.chunks():
                destination.write(chunk)
        with open(depth_image_path, 'wb+') as destination:
            for chunk in depth_image.chunks():
                destination.write(chunk)

        # Poz tahminini gerçekleştir
        result = PoseService.process_image_files(color_image_path, depth_image_path)

        # Geçici dosyaları sil
        os.remove(color_image_path)
        os.remove(depth_image_path)

        return JsonResponse(result)

    except Exception as e:
        if os.path.exists(color_image_path):
            os.remove(color_image_path)
        if os.path.exists(depth_image_path):
            os.remove(depth_image_path)
        return JsonResponse({'error': str(e)}, status=500)
