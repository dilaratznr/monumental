# core/urls.py
from django.contrib import admin
from django.urls import path
from brickpose.views import process_images_from_request

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/process_image/', process_images_from_request, name='process_image'),
    
]
