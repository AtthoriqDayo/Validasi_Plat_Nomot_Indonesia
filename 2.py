import re

class DFA_PlatNomor_Strict:
    def __init__(self):
        # DATASET KODE WILAYAH INDONESIA (Strict Data)
        # Set 1: Kode yang valid sebagai 1 Huruf (Contoh: B, D, F)
        self.valid_single = {
            'B', 'D', 'E', 'F', 'G', 'H', 'K', 'L', 'M', 'N', 'P', 'R', 'S', 'T', 'W', 'Z'
        }
        
        # Set 2: Kode yang valid sebagai 2 Huruf (Contoh: AA, AB, DK)
        # Ini mencakup seluruh Indonesia (Jawa, Sumatera, Kalimantan, Sulawesi, Papua, dll)
        self.valid_double = {
            'AA', 'AB', 'AD', 'AE', 'AG', 'BA', 'BB', 'BD', 'BE', 'BG', 'BH', 'BK', 'BL', 'BM', 'BN', 'BP',
            'DA', 'DB', 'DC', 'DD', 'DE', 'DG', 'DH', 'DK', 'DL', 'DM', 'DN', 'DP', 'DR', 'DT',
            'EA', 'EB', 'ED', 'KB', 'KH', 'KT', 'KU', 'PA', 'PB', 'KT', 'KU' 
            # (List bisa ditambah sesuai data Samsat lengkap)
        }

        self.reset()

    def reset(self):
        self.state = 'q0'
        self.buffer_wilayah = "" # Membantu menyimpan huruf pertama untuk pengecekan 2 huruf



    def process(self, input_string):
        self.reset()
        # Preprocessing: Ubah ke huruf besar
        input_string = input_string.upper()
        
        print(f"Memproses: '{input_string}'")

        for char in input_string:
            # --- LOGIKA TRANSISI ---
            
            if self.state == 'q0':
                if 'A' <= char <= 'Z':
                    self.buffer_wilayah += char # Simpan huruf pertama
                    # Cek apakah huruf ini valid sebagai awalan kode 2 huruf?
                    # (Hampir semua huruf bisa jadi awalan, validasi ada di langkah berikutnya)
                    self.state = 'q_check_region' 
                else:
                    return self._trap("Awal harus Huruf")

            elif self.state == 'q_check_region':
                if char == ' ':
                    # Transisi: Huruf -> Spasi (Berarti Kode 1 Huruf)
                    if self.buffer_wilayah in self.valid_single:
                        self.state = 'q_space1'
                    else:
                        return self._trap(f"Kode wilayah '{self.buffer_wilayah}' tidak valid")
                elif 'A' <= char <= 'Z':
                    # Transisi: Huruf -> Huruf (Berarti Kode 2 Huruf)
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

            # --- BAGIAN ANGKA (Sama seperti sebelumnya) ---
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

            # --- BAGIAN SERI AKHIR ---
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

        # Cek State Akhir
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
        # 1. Bersihkan dasar: Hapus spasi depan/belakang, ubah ke Uppercase
        s = raw.strip().upper()
        
        # 2. Hapus SEMUA spasi yang ada di dalam text (biar kita susun ulang dari nol)
        # Contoh: "B  1234 abc" -> "B1234ABC"
        s_clean = re.sub(r'\s+', '', s)
        
        # 3. Gunakan Regex untuk mendeteksi struktur Plat Nomor (tanpa spasi)
        # Group 1: Huruf Depan (1-2 digit)
        # Group 2: Angka (1-4 digit)
        # Group 3: Huruf Belakang (1-3 digit)
        match = re.match(r'^([A-Z]{1,2})([0-9]{1,4})([A-Z]{1,3})$', s_clean)
        
        if match:
            # Jika pola ketemu, susun ulang dengan SPASI STANDAR
            # Contoh: "B" + " " + "1234" + " " + "ABC"
            plat = f"{match.group(1)} {match.group(2)} {match.group(3)}"
        
        else:
            # Jika polanya aneh banget (misal: "12345" atau "ABCDEFG"), 
            # kembalikan apa adanya (trim & upper saja).
            # Biarkan DFA yang nanti menolaknya (karena DFA adalah hakim terakhir).
            # Kita juga replace double space jadi single space untuk input sampah ini.
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
