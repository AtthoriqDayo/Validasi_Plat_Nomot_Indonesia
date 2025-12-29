import time
import json
import pytesseract
import cv2
import numpy as np
import re
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

def fix_confusions(text, is_digit_zone):
    """
    Swaps commonly confused characters based on where they are.
    """
    # If we expect NUMBERS but got letters:
    if is_digit_zone:
        replacements = {'O': '0', 'D': '0', 'Q': '0', 'U': '0', 
                        'I': '1', 'L': '1', 
                        'S': '5', 'B': '8', 'Z': '2', 'A': '4'}
    # If we expect LETTERS but got numbers:
    else:
        replacements = {'0': 'O', '1': 'I', '5': 'S', '8': 'B', '4': 'A', '2': 'Z'}
        
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text

def parse_plate(raw_text):
    """
    Extracts ONLY the license plate and ignores the expiration date.
    Returns (plate_string, error_message).
    """
    # 1. Cleaning: Remove non-alphanumeric chars (keep spaces)
    clean_line = re.sub(r'[^A-Z0-9\s]', '', raw_text.upper().replace('\n', ' '))
    
    # 2. Regex Pattern: [1-2 Letters] [Space] [1-4 Numbers] [Space] [1-3 Letters]
    match = re.search(r'([A-Z0-9]{1,2})\s+([A-Z0-9]{1,4})\s+([A-Z0-9]{1,3})', clean_line)
    
    if not match:
        return None, "Failed to match pattern"

    # 3. Extract parts
    area_raw, number_raw, suffix_raw = match.groups()

    # 4. Apply Logic Fixes (Your System)
    area_clean = fix_confusions(area_raw, is_digit_zone=False)
    number_clean = fix_confusions(number_raw, is_digit_zone=True)
    suffix_clean = fix_confusions(suffix_raw, is_digit_zone=False)
    
    final_plate = f"{area_clean} {number_clean} {suffix_clean}"
    return final_plate, None

# --- DJANGO VIEWS ---

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
def compare_performance(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            test_plates = data.get('plates', [])
            include_details = data.get('include_details', False)
            
            if not test_plates:
                return JsonResponse({'error': 'No plates provided'}, status=400)

            # 1. DFA Speed
            start_cpu = time.perf_counter()
            dfa = DFA_PlatNomor_Web()
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

            # 2. DB Speed
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
                response_data['details'] = detailed_results

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'POST required'}, status=405)

@csrf_exempt
def ocr_scan(request):
    """
    Accepts an image upload, runs OpenCV Preprocessing, Tesseract, DFA, and DB Save.
    """
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            # 1. Read Image from Memory (Django -> OpenCV)
            img_file = request.FILES['image']
            file_bytes = np.frombuffer(img_file.read(), np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            
            if img is None:
                return JsonResponse({'error': "Could not decode image"}, status=400)

            # 2. Pre-processing (Your "Final Pipeline" Logic)
            # Resize
            aspect_ratio = img.shape[0] / img.shape[1]
            new_width = 800
            img_resized = cv2.resize(img, (new_width, int(new_width * aspect_ratio)))
            
            # Grayscale + Threshold (Otsu)
            gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # 3. Run Tesseract (PSM 11 for sparse text)
            custom_config = r'--oem 3 --psm 11'
            raw_output = pytesseract.image_to_string(binary, config=custom_config)
            
            # 4. Parse & Fix Confusions
            parsed_plate, error_msg = parse_plate(raw_output)
            
            if not parsed_plate:
                # If regex failed, we return the error but still show raw text
                return JsonResponse({
                    'raw_text': raw_output.strip(),
                    'validation': {'is_valid': False, 'final_message': error_msg}
                })

            # 5. DFA Validation
            dfa = DFA_PlatNomor_Web()
            validation_result = dfa.process(parsed_plate)
            
            # 6. Database Auto-Save (The Critical Step)
            db_status = "Skipped (Invalid)"
            if validation_result['is_valid']:
                # Save clean data
                obj, created = RegisteredPlate.objects.get_or_create(
                    plate_number=validation_result['normalized_input'],
                    defaults={'owner_name': 'Auto-Scan'}
                )
                db_status = "Saved to Database" if created else "Already in Database"

            return JsonResponse({
                'raw_text': raw_output.strip(),  # What Tesseract saw
                'detected_plate': parsed_plate,  # What your Logic fixed
                'validation': validation_result, # What DFA thought
                'database_message': db_status    # Storage status
            })

        except Exception as e:
            return JsonResponse({'error': f"System Error: {str(e)}"}, status=500)

    return JsonResponse({'error': 'Image required'}, status=400)