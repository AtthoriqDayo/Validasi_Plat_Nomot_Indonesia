from django.contrib import admin
from django.urls import path
from myapp import views  # Make sure 'my_app' matches your actual app folder name

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- The API Endpoints ---
    # This matches the URL you tried to visit: /api/validate-dfa/
    path('api/validate-dfa/', views.validate_plate_api, name='api_validate'),
    
    # This matches the speed test script: /api/compare-speed/
    path('api/compare-speed/', views.compare_performance, name='api_compare'),
    
    # This matches the OCR feature: /api/ocr-scan/
    path('api/ocr-scan/', views.ocr_scan, name='api_ocr'),

    # --- The Frontend ---
    # This matches the root URL: http://127.0.0.1:8000/
    path('', views.index, name='home'),
]