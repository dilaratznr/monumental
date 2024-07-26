import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from image_processing.image_processing import process_images_and_save_rgbd, load_images_and_camera_params
from mpl_toolkits.mplot3d import Axes3D
import uuid

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

def format_translation_rotation(translation, rotation):
    try:
        translation = [float(coord) for coord in translation]
        yaw = float(rotation.get('yaw', 0.0))
        pitch = float(rotation.get('pitch', 0.0))
        roll = float(rotation.get('roll', 0.0))

        translation_str = f"Translation (mm): [{translation[0]:.2f}, {translation[1]:.2f}, {translation[2]:.2f}]"
        rotation_str = f"Rotation (degrees): [Yaw: {yaw:.2f}, Pitch: {pitch:.2f}, Roll: {roll:.2f}]"

        return translation_str, rotation_str
    except Exception as e:
        return "Error formatting translation", f"Error formatting rotation: {str(e)}"

def display_results(request):
    # Fetch and sort folders numerically
    folders = sorted(
        [d for d in os.listdir(os.path.join(settings.MEDIA_ROOT, 'place_quality_inputs')) if os.path.isdir(os.path.join(settings.MEDIA_ROOT, 'place_quality_inputs', d))],
        key=lambda x: int(x) if x.isdigit() else float('inf')
    )

    selected_folder = request.GET.get('folder')
    result = None
    
    if selected_folder:
        folder_path = os.path.join(settings.MEDIA_ROOT, 'place_quality_inputs', selected_folder)
        color_image_path = os.path.join(settings.MEDIA_URL, 'place_quality_inputs', selected_folder, 'color.png')
        depth_image_path = os.path.join(settings.MEDIA_URL, 'place_quality_inputs', selected_folder, 'depth.png')

        absolute_rgbd_image_path, absolute_processed_image_path, absolute_pose_visualization_path, processed_image_mean_intensity, translation, rotation = process_images_and_save_rgbd(folder_path)
        
        if absolute_rgbd_image_path:
            relative_rgbd_path = os.path.relpath(absolute_rgbd_image_path, settings.MEDIA_ROOT)
            rgbd_image_path = os.path.join(settings.MEDIA_URL, relative_rgbd_path).replace("\\", "/")
        if absolute_processed_image_path:
            relative_processed_path = os.path.relpath(absolute_processed_image_path, settings.MEDIA_ROOT)
            processed_image_path = os.path.join(settings.MEDIA_URL, relative_processed_path).replace("\\", "/")
        if absolute_pose_visualization_path:
            relative_pose_visualization_path = os.path.relpath(absolute_pose_visualization_path, settings.MEDIA_ROOT)
            pose_visualization_path = os.path.join(settings.MEDIA_URL, relative_pose_visualization_path).replace("\\", "/")

        try:
            with open(os.path.join(folder_path, 'cam.json'), 'r') as f:
                camera_params = json.load(f)
        except Exception as e:
            camera_params = str(e)

        formatted_translation, formatted_rotation = format_translation_rotation(translation, rotation)

        result = {
            'color_image_path': color_image_path,
            'depth_image_path': depth_image_path,
            'rgbd_image_path': rgbd_image_path,
            'processed_image_path': processed_image_path,
            'pose_visualization_path': pose_visualization_path,
            'processed_image_mean_intensity': processed_image_mean_intensity,
            'camera_params': camera_params,
            'translation': formatted_translation,
            'rotation': formatted_rotation
        }

    return render(request, 'result.html', {
        'folders': folders,
        'selected_folder': selected_folder,
        'result': result
    })