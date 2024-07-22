from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .repositories.image_repository import ImageRepository
from .services.pose_service import PoseService

class ProcessImageView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            rgb_file = request.FILES['image']
            depth_file = request.FILES['depth_image']
            
            # Görüntüleri yükleyin
            rgb_image, depth_image = ImageRepository.load_images(rgb_file, depth_file)
            
            # Tuğlanın pozunu hesaplayın
            position, orientation = PoseService.process_image(rgb_image, depth_image)
            
            if position is None:
                return Response({'error': 'Brick not found'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Sonucu JSON formatında döndürün
            return Response({
                'position': position.tolist(),
                'orientation': orientation.tolist()
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
