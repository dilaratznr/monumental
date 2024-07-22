from django.urls import path
from .views import ProcessImageView

urlpatterns = [
    path('process_image/', ProcessImageView.as_view(), name='process_image'),
]
