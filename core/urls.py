from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from brickpose.views import process_images_from_request, display_results

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/process_image/', process_images_from_request, name='process_image'),
    path('display_results/', display_results, name='display_results'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
