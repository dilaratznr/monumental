import os
import json
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .services.pose_service import PoseService
from django.conf import settings
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

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
    # Convert numpy float64 to regular float
    translation = [float(coord) for coord in translation]
    rotation = [float(angle) for angle in rotation]

    translation_str = f"Translation (mm): [{translation[0]:.2f}, {translation[1]:.2f}, {translation[2]:.2f}]"
    rotation_str = f"Rotation (degrees): [{rotation[0]:.2f}, {rotation[1]:.2f}, {rotation[2]:.2f}]"

    return translation_str, rotation_str

def display_results(request):
    folders = sorted([d for d in os.listdir(os.path.join(settings.MEDIA_ROOT, 'place_quality_inputs')) if os.path.isdir(os.path.join(settings.MEDIA_ROOT, 'place_quality_inputs', d))])

    selected_folder = request.GET.get('folder')
    if selected_folder is not None:
        folder_path = os.path.join(settings.MEDIA_ROOT, 'place_quality_inputs', selected_folder)
        color_image_path = os.path.join(folder_path, 'color.png')
        depth_image_path = os.path.join(folder_path, 'depth.png')
        camera_params_path = os.path.join(folder_path, 'cam.json')

        result = PoseService.process_image_files(color_image_path, depth_image_path, camera_params_path)
        result['color_image_path'] = f"{settings.MEDIA_URL}place_quality_inputs/{selected_folder}/color.png"
        result['depth_image_path'] = f"{settings.MEDIA_URL}place_quality_inputs/{selected_folder}/depth.png"
        result['processed_image_path'] = f"{settings.MEDIA_URL}results/{os.path.basename(result['processed_image_path'])}"

        # Format the translation and rotation
        formatted_translation, formatted_rotation = format_translation_rotation(result['translation'], result['rotation'])

        # Görselleştirme için output_path'i belirleyin ve visualize_pose fonksiyonunu çağırın
        output_path = os.path.join(settings.MEDIA_ROOT, 'results', 'pose_visualization.png')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Pozisyonu alın ve görselleştirme fonksiyonunu çağırın
        translation = result.get('translation', [0, 0, 0])  # Translation bilgisini alın
        visualize_pose(translation, output_path)

        # Görselin URL'sini result'a ekleyin
        result['pose_visualization_path'] = f"{settings.MEDIA_URL}results/pose_visualization.png"

        return render(request, 'result.html', {
            'result': result,
            'folders': folders,
            'selected_folder': selected_folder,
            'formatted_translation': formatted_translation,
            'formatted_rotation': formatted_rotation,
            'pose_visualization_path': result['pose_visualization_path']
        })
    
    return render(request, 'result.html', {'folders': folders})

def visualize_pose(translation, output_path):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(0, 0, 0, c='r', marker='o', label='Camera Origin')
    ax.scatter(*translation, c='b', marker='^', label='Estimated Brick Position')
    ax.plot([0, translation[0]], [0, translation[1]], [0, translation[2]], 'g--')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    ax.set_title('Estimated 3D Pose of the Brick')
    ax.legend()

    plt.savefig(output_path)
    plt.close(fig)
