import time
import json
import pytesseract
from PIL import Image
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import RegisteredPlate
from .utils.dfa import DFA_PlatNomor_Web

def index(request):
    """Renders the main futuristic dashboard."""
    return render(request, 'index.html')

def validate_plate_api(request):
    """API for the DFA Animation."""
    plate = request.GET.get('plate', '')
    dfa = DFA_PlatNomor_Web()
    result = dfa.process(plate)
    return JsonResponse(result)

@csrf_exempt
@csrf_exempt
def compare_performance(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            test_plates = data.get('plates', [])
            include_details = data.get('include_details', False) # <--- NEW PARAMETER
            
            if not test_plates:
                return JsonResponse({'error': 'No plates provided'}, status=400)

            # 1. DFA Speed
            start_cpu = time.perf_counter()
            dfa = DFA_PlatNomor_Web()
            
            # We store results here now
            detailed_results = [] 
            
            for p in test_plates:
                res = dfa.process(p)
                if include_details:
                    detailed_results.append({
                        'plate': p, 
                        'is_valid': res['is_valid'],
                        'reason': res['final_message']
                    })
            end_cpu = time.perf_counter()

            # 2. DB Speed (Logic unchanged)
            start_db = time.perf_counter()
            for p in test_plates:
                clean_p = dfa.normalize_plate(p)
                RegisteredPlate.objects.filter(plate_number=clean_p).exists()
            end_db = time.perf_counter()

            response_data = {
                'dfa_duration_ms': round((end_cpu - start_cpu) * 1000, 4),
                'db_duration_ms': round((end_db - start_db) * 1000, 4),
                'count': len(test_plates),
                'winner': 'DFA Algorithm' if (end_cpu - start_cpu) < (end_db - start_db) else 'Database'
            }

            if include_details:
                response_data['details'] = detailed_results # <--- Send back the list

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'POST required'}, status=405)

@csrf_exempt
def ocr_scan(request):
    """
    Accepts an image upload, runs Tesseract, then runs DFA.
    """
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            # Open image directly from memory
            img_file = request.FILES['image']
            image = Image.open(img_file)
            
            # --- TESSERACT PROCESSING ---
            # Using LSTM engine (default)
            # Configuring to treat image as a single line of text (--psm 7) can help for plates
            custom_config = r'--oem 3 --psm 7' 
            detected_text = pytesseract.image_to_string(image, config=custom_config)
            
            # Run our DFA on the detected text
            dfa = DFA_PlatNomor_Web()
            validation_result = dfa.process(detected_text)
            
            return JsonResponse({
                'raw_text': detected_text.strip(),
                'validation': validation_result
            })
        except Exception as e:
            return JsonResponse({'error': f"OCR Failed: {str(e)}"}, status=500)

    return JsonResponse({'error': 'Image required'}, status=400)