from django.urls import path
from . import views

urlpatterns = [
    # The Frontend
    path('', views.index, name='home'),
    
    # The APIs
    path('api/validate-dfa/', views.validate_plate_api, name='api_validate'),
    path('api/compare-speed/', views.compare_performance, name='api_compare'),
    path('api/ocr-scan/', views.ocr_scan, name='api_ocr'),
]