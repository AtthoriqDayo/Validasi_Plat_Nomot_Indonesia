import cv2
import pytesseract
import re

# --- CONFIGURATION ---
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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
    """
    print(f"DEBUG Raw: {raw_text}")
    
    # 1. Remove non-alphanumeric chars (keep spaces) to clean up noise
    # We turn newlines into spaces so the date (usually on a new line) becomes just more text
    clean_line = re.sub(r'[^A-Z0-9\s]', '', raw_text.upper().replace('\n', ' '))
    
    # 2. Use Regex to find the pattern: [1-2 Letters] [1-4 Numbers] [1-3 Letters]
    # This specifically IGNORES the "05 28" date format (Number Number)
    
    # Pattern explanation:
    # ([A-Z]{1,2})   -> Group 1: Area Code (1 or 2 letters)
    # \s+            -> Space
    # ([0-9]{1,4})   -> Group 2: Plate Number (1 to 4 digits)
    # \s+            -> Space
    # ([A-Z]{1,3})   -> Group 3: Suffix (1 to 3 letters)
    
    match = re.search(r'([A-Z0-9]{1,2})\s+([A-Z0-9]{1,4})\s+([A-Z0-9]{1,3})', clean_line)
    
    if not match:
        return "Failed to match pattern"

    # 3. Extract the parts (which might still have typos, e.g. 'B 1234 XY')
    area_raw = match.group(1)
    number_raw = match.group(2)
    suffix_raw = match.group(3)

    # 4. Apply Logic Fixes
    # Area: Expect Letters
    area_clean = fix_confusions(area_raw, is_digit_zone=False)
    
    # Number: Expect Digits (This fixes the O/0 diagonal strip issue!)
    number_clean = fix_confusions(number_raw, is_digit_zone=True)
    
    # Suffix: Expect Letters
    suffix_clean = fix_confusions(suffix_raw, is_digit_zone=False)
    
    final_plate = f"{area_clean} {number_clean} {suffix_clean}"
    return final_plate

# --- TEST ON YOUR FILES ---
# Use the best processing function from our previous step (e.g., smart_scan or diagnostic_scan)
# Here is a simplified runner using the logic we know works (PSM 11)

def final_pipeline(image_path):
    img = cv2.imread(image_path)
    if img is None: return

    # Resize (Standardize)
    aspect_ratio = img.shape[0] / img.shape[1]
    new_width = 800
    img = cv2.resize(img, (new_width, int(new_width * aspect_ratio)))

    # Grayscale + Otsu
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Run OCR with PSM 11 (Find text anywhere)
    custom_config = r'--oem 3 --psm 11'
    raw_output = pytesseract.image_to_string(binary, config=custom_config)
    
    # --- THE MAGIC STEP ---
    result = parse_plate(raw_output)
    print(f"File: {image_path} -> DETECTED: {result}\n")

# Run it
files = [
    r"C:\Users\attho\Downloads\downloadfhosfusafoa.jpeg",
    r'C:\Users\attho\Downloads\plat-nomor-1.webp',
    r'C:\Users\attho\Downloads\Latest_motor_vehicle_number_plate_designs_in_Indonesia.jpg',
    r'C:\Users\attho\Downloads\1678275755219-IMG_20230308_183755_618.jpg'
]

for f in files:
    final_pipeline(f)