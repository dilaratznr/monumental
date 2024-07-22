from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to the Brick Pose Estimation API")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('brickpose.urls')),
    path('', home, name='home'),  # Ana sayfa URL'i eklendi
]
