import re

class DFA_PlatNomor_Web:
    def __init__(self):
        # Define the Alphabet / Valid Token Sets
        self.valid_single = {
            'G', 'H', 'K', 'L', 'M', 'N', 'P', 'R', 'S', 'T', 'W', 'Z', 'B', 'D', 'E', 'F','A'
        }
        self.valid_double = {
            'AA', 'AB', 'AD', 'AE', 'AG','DK','DR','EA', 'DH','EB','ED','KB','DA','KH','KT','KU',
            'DB','DL','DM','DN','DT','DD','DP','DW','DC','PA','PB','DE','DG','BL','BB','BK','BM',
            'BH','BP','BD','BG','BN','BE'      
        }
        self.reset()

    def reset(self):
        self.state = 'q0'
        self.buffer_wilayah = ""
        self.history = []  # Stores the animation steps

    @staticmethod
    def normalize_plate(raw_text):
        """
        Pre-processing: cleans input using Regex before the DFA touches it.
        """
        if not raw_text:
            return ""
            
        # 1. Strip whitespace and uppercase
        s = raw_text.strip().upper()
        
        # 2. Remove all internal whitespace to check structure
        s_clean = re.sub(r'\s+', '', s)
        
        # 3. Regex capture groups to format it nicely: (Letters)(Numbers)(Letters)
        match = re.match(r'^([A-Z]{1,2})([0-9]{1,4})([A-Z]{1,3})$', s_clean)
        
        if match:
            # Reconstruct with proper spacing: "AB 1234 XY"
            return f"{match.group(1)} {match.group(2)} {match.group(3)}"
        else:
            # Fallback: Just single spaces
            return re.sub(r'\s+', ' ', s)

    def log_state(self, char, reason=None):
        """Records the current step for the frontend animation."""
        self.history.append({
            'state': self.state,
            'input': char,
            'status': 'rejected' if self.state == 'TRAP' else 'accepted',
            'reason': reason
        })

    def _trap(self, reason):
        self.state = 'TRAP'
        self.log_state(None, reason)

    def process(self, raw_input):
        # STEP 1: Normalize the input
        clean_input = self.normalize_plate(raw_input)
        
        self.reset()
        
        # Log initial state
        self.log_state(None, "Start") 

        # STEP 2: Run the DFA on the cleaned input
        for char in clean_input:
            
            # --- STATE TRANSITIONS ---
            if self.state == 'q0':
                if 'A' <= char <= 'Z':
                    self.buffer_wilayah += char 
                    self.state = 'q_check_region' 
                else:
                    self._trap("Awal harus Huruf")
                    break

            elif self.state == 'q_check_region':
                if char == ' ':
                    if self.buffer_wilayah in self.valid_single:
                        self.state = 'q_space1'
                    else:
                        self._trap(f"Kode wilayah '{self.buffer_wilayah}' tidak valid")
                        break
                elif 'A' <= char <= 'Z':
                    self.buffer_wilayah += char
                    if self.buffer_wilayah in self.valid_double:
                        self.state = 'q_region_done'
                    else:
                        self._trap(f"Kode wilayah '{self.buffer_wilayah}' tidak valid")
                        break
                else:
                    self._trap("Format wilayah salah")
                    break

            elif self.state == 'q_region_done':
                if char == ' ':
                    self.state = 'q_space1'
                else:
                    self._trap("Harus spasi setelah kode wilayah 2 digit")
                    break

            elif self.state == 'q_space1':
                if '1' <= char <= '9':
                    self.state = 'q_digit1'
                else:
                    self._trap("Harus angka setelah spasi (tidak boleh 0 di depan)")
                    break

            elif self.state == 'q_digit1':
                if '0' <= char <= '9': self.state = 'q_digit2'
                elif char == ' ': self.state = 'q_space2'
                else: 
                    self._trap("Input salah di digit")
                    break

            elif self.state == 'q_digit2':
                if '0' <= char <= '9': self.state = 'q_digit3'
                elif char == ' ': self.state = 'q_space2'
                else: 
                    self._trap("Input salah di digit")
                    break

            elif self.state == 'q_digit3':
                if '0' <= char <= '9': self.state = 'q_digit4'
                elif char == ' ': self.state = 'q_space2'
                else: 
                    self._trap("Input salah di digit")
                    break

            elif self.state == 'q_digit4':
                if char == ' ': self.state = 'q_space2'
                else: 
                    self._trap("Maksimal 4 digit angka")
                    break

            elif self.state == 'q_space2':
                if 'A' <= char <= 'Z': self.state = 'q_final1'
                else: 
                    self._trap("Harus huruf seri belakang")
                    break

            elif self.state == 'q_final1': # (Final State)
                if 'A' <= char <= 'Z': self.state = 'q_final2'
                elif char == ' ': 
                    self._trap("Spasi tidak boleh di akhir")
                    break
                else: 
                    self._trap("Karakter ilegal di seri")
                    break

            elif self.state == 'q_final2': # (Final State)
                if 'A' <= char <= 'Z': self.state = 'q_final3'
                else: 
                    self._trap("Karakter ilegal di seri")
                    break

            elif self.state == 'q_final3': # (Final State)
                # Sudah 3 huruf, tidak boleh ada input lagi
                self._trap("Maksimal 3 huruf seri belakang")
                break
            
            # Log valid transition
            self.log_state(char)

        # --- END OF LOOP CHECKS ---
        
        is_valid = self.state in ['q_final1', 'q_final2', 'q_final3']
        
        # If loop finished but state is not final (e.g. "B 1234" -> stops at q_digit4)
        if not is_valid and self.state != 'TRAP':
             self.log_state(None, "Input tidak lengkap")

        return {
            'original_input': raw_input,
            'normalized_input': clean_input,
            'is_valid': is_valid,
            'history': self.history,
            'final_message': "Valid Plat Nomor" if is_valid else self.history[-1].get('reason', 'Invalid Format')
        }