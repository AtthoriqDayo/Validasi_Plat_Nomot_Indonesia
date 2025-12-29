import csv
import random
import string

# Daftar Kode Wilayah (Sampel kode wilayah di Indonesia)
kode_wilayah = [
    "BL", "BB", "BK", "BA", "BM", "BH", "BD", "BP", "BG", "BN", "BE", # Sumatera
    "A", "B", "D", "E", "F", "T", "Z", # DKI, Jabar, Banten
    "G", "H", "K", "R", "AA", "AB", "AD", # Jateng & DIY
    "L", "M", "N", "P", "S", "W", "AE", "AG", # Jatim
    "DK", "DR", "EA", "DH", "EB", "ED", # Bali & Nusa Tenggara
    "KB", "DA", "KH", "KT", "KU", # Kalimantan
    "DB", "DL", "DM", "DN", "DT", "DC", # Sulawesi
    "DE", "DG", "PA", "PB" # Maluku & Papua
]

def generate_plat():
    # 1. Pilih Kode Wilayah
    wilayah = random.choice(kode_wilayah)
    
    # 2. Generate Angka (1 sampai 4 digit)
    angka = random.randint(1, 9999)
    
    # 3. Generate Kode Belakang (1 sampai 3 huruf)
    # Huruf pertama kode belakang biasanya menunjukkan wilayah spesifik/jenis kendaraan
    panjang_suffix = random.randint(1, 3) 
    huruf_belakang = ''.join(random.choices(string.ascii_uppercase, k=panjang_suffix))
    
    # Format: B 1234 XYZ
    return f"{wilayah} {angka} {huruf_belakang}"

def main():
    jumlah_data = 25000
    filename = "data_plat_indonesia.csv"
    
    # Menggunakan set untuk memastikan data unik (tidak ada duplikat)
    data_unik = set()
    
    print(f"Sedang men-generate {jumlah_data} data plat nomor...")
    
    while len(data_unik) < jumlah_data:
        data_unik.add(generate_plat())
        
    # Menyimpan ke CSV
    print("Menyimpan ke file CSV...")
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Menulis Header
        writer.writerow(["Plat Nomor"])
        
        # Menulis Data
        for index, plat in enumerate(data_unik, start=1):
            writer.writerow([plat])
            
    print(f"Selesai! File '{filename}' telah berhasil dibuat.")

if __name__ == "__main__":
    main()