import re

class DFA_PlatNomor_Strict:
    def __init__(self):
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



    def process(self, input_string):
        self.reset()
        input_string = input_string.upper()
        
        print(f"Memproses: '{input_string}'")

        for char in input_string:
            if self.state == 'q0':
                if 'A' <= char <= 'Z':
                    self.buffer_wilayah += char 
                    self.state = 'q_check_region' 
                else:
                    return self._trap("Awal harus Huruf")

            elif self.state == 'q_check_region':
                if char == ' ':
                    if self.buffer_wilayah in self.valid_single:
                        self.state = 'q_space1'
                    else:
                        return self._trap(f"Kode wilayah '{self.buffer_wilayah}' tidak valid")
                elif 'A' <= char <= 'Z':
                    self.buffer_wilayah += char
                    if self.buffer_wilayah in self.valid_double:
                        self.state = 'q_region_done'
                    else:
                        return self._trap(f"Kode wilayah '{self.buffer_wilayah}' tidak valid")
                else:
                    return self._trap("Format wilayah salah")
                

            elif self.state == 'q_region_done':
                if char == ' ':
                    self.state = 'q_space1'
                else:
                    return self._trap("Harus spasi setelah kode wilayah 2 digit")

            elif self.state == 'q_space1':
                if '1' <= char <= '9':
                    self.state = 'q_digit1'
                else:
                    return self._trap("Harus angka setelah spasi dan tidak boleh diawali 0")



            elif self.state == 'q_digit1':
                if '0' <= char <= '9': self.state = 'q_digit2'
                elif char == ' ': self.state = 'q_space2'
                else: return self._trap("Input salah di digit")

            elif self.state == 'q_digit2':
                if '0' <= char <= '9': self.state = 'q_digit3'
                elif char == ' ': self.state = 'q_space2'
                else: return self._trap("Input salah di digit")

            elif self.state == 'q_digit3':
                if '0' <= char <= '9': self.state = 'q_digit4'
                elif char == ' ': self.state = 'q_space2'
                else: return self._trap("Input salah di digit")

            elif self.state == 'q_digit4':
                if char == ' ': self.state = 'q_space2'
                else: return self._trap("Maksimal 4 digit angka")




            elif self.state == 'q_space2':
                if 'A' <= char <= 'Z': self.state = 'q_final1'
                else: return self._trap("Harus huruf seri belakang")

            elif self.state == 'q_final1': # (Final State)
                if 'A' <= char <= 'Z': self.state = 'q_final2'
                elif char == ' ': return self._trap("Spasi tidak boleh di akhir")
                else: return self._trap("Karakter ilegal di seri")

            elif self.state == 'q_final2': # (Final State)
                if 'A' <= char <= 'Z': self.state = 'q_final3'
                else: return self._trap("Karakter ilegal di seri")

            elif self.state == 'q_final3': # (Final State)
                # Sudah 3 huruf, tidak boleh ada input lagi
                return self._trap("Maksimal 3 huruf seri belakang")
            
            elif self.state == 'TRAP':
                return False


        if self.state in ['q_final1', 'q_final2', 'q_final3']:
            return True
        else:
            print(f"-> Gagal: Berhenti di tengah jalan (State: {self.state})")
            return False

    def _trap(self, reason):
        print(f"-> Ditolak: {reason}")
        self.state = 'TRAP'
        return False



class main:
    def __init__(self):
        self.Plat_check = DFA_PlatNomor_Strict()


    def normalize_plate(raw):
        s = raw.strip().upper()
        s_clean = re.sub(r'\s+', '', s)
        match = re.match(r'^([A-Z]{1,2})([0-9]{1,4})([A-Z]{1,3})$', s_clean)
        
        if match:
            plat = f"{match.group(1)} {match.group(2)} {match.group(3)}"
        else:
            plat = re.sub(r'\s+', ' ', s)

        return plat


    def Start(self):
        normalize_plate = main.normalize_plate
        print("=== DFA Validasi Plat Nomor Kendaraan Indonesia ===")
        print("-----------------------------------------------")
        
        while True:
            data = input("Masukkan Plat Nomor Kendaraan (atau 'exit' untuk berhenti): ")

            if data.lower() == "exit":
                break

            print("\n--- PROSES NORMALISASI ---")
            print(f"Input Mentah: '{data}'")
            plat = normalize_plate(data)
            print(f"Hasil Normalisasi: '{plat}'\n")

            print("--- HASIL PENGUJIAN ---")
            result = "VALID" if self.Plat_check.process(plat) else "INVALID"
            print(f"Input: {plat} => {result}\n")


if __name__ == "__main__":
    main().Start()
