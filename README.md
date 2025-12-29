# Sistem Validasi Plat Nomor Indonesia Berbasis DFA

> **Mata Kuliah:** Teori Graf dan Automata  
> **Kelompok:** 11  
> **Institusi:** Universitas Muhammadiyah Kalimantan Timur

## 📖 Deskripsi Proyek

Aplikasi ini adalah implementasi nyata dari teori **Deterministic Finite Automata (DFA)** dan **Regular Expression (Regex)** untuk memvalidasi format Tanda Nomor Kendaraan Bermotor (TNKB) Indonesia.

Sistem ini dirancang untuk mendemonstrasikan efisiensi algoritma DFA (`O(L)`) dibandingkan dengan metode pencarian basis data konvensional (`O(log N)`). Aplikasi web dibangun menggunakan **Django Framework**.

### Fitur Utama:
1.  **DFA Visualizer:** Visualisasi langkah-demi-langkah (step-by-step) bagaimana mesin automata memproses input karakter plat nomor secara *real-time*.
2.  **Performance Benchmark:** Alat uji stres (*stress test*) untuk membandingkan kecepatan validasi antara Algoritma DFA vs Database Query.
3.  **Strict Mode Validation:** Validasi ketat kode wilayah (misal: 'B' valid, 'C' invalid).
4.  **OCR Integration:** Fitur ekstraksi teks dari gambar plat nomor menggunakan Tesseract OCR.

---

## 🛠️ Prasyarat (Prerequisites)

Sebelum memulai, pastikan komputer Anda telah terinstal:
1.  **Python 3.10+**: [Download di sini](https://www.python.org/downloads/)
2.  **Git**: Untuk kloning repositori.
3.  **Tesseract OCR** (Wajib jika ingin menggunakan fitur Upload Gambar):
    * *Windows:* [Download Installer](https://github.com/UB-Mannheim/tesseract/wiki) (Pastikan path tesseract didaftarkan ke Environment Variables).
    * *Linux:* `sudo apt install tesseract-ocr`
    * *Mac:* `brew install tesseract`

---

## 🚀 Panduan Instalasi (Step-by-Step)

Ikuti langkah-langkah berikut di terminal/command prompt Anda:

### 1. Clone Repositori
Unduh kode sumber ke komputer lokal Anda.
```bash
git clone https://github.com/AtthoriqDayo/Validasi_Plat_Nomot_Indonesia.git
cd Validasi_Plat_Nomot_Indonesia
```

### 2. Buat Virtual Environment
Sangat disarankan menggunakan lingkungan virtual agar dependensi tidak bentrok.

* Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

* Mac/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instal Dependensi
Instal seluruh paket yang dibutuhkan secara otomatis menggunakan file requirements.
```bash
pip install -r requirements.txt
```

### 4. Migrasi Database
Siapkan struktur database SQLite lokal.
```bash
python manage.py makemigrations
python manage.py migrate
```

## 5. Seed Data (PENTING UNTUK BENCHMARK) ⚠️
Fitur Benchmark membutuhkan data dummy di database agar perbandingannya valid. Jalankan perintah kustom ini untuk mengisi database dengan ribuan data plat nomor acak:
```bash
python manage.py seed_plates
```
(Tunggu hingga proses selesai. Script ini akan men-generate data sampel untuk pengujian).

## 6. Menjalankan Server
Terakhir, nyalakan server pengembangan Django dengan perintah:
```bash
python manage.py runserver
```

## 7. Akses Aplikasi
Setelah server berjalan (biasanya muncul pesan Starting development server at http://127.0.0.1:8000/), buka browser Anda (Chrome/Firefox/Edge) dan kunjungi alamat:

http://127.0.0.1:8000/

---
## 📂 Struktur Proyek Utama
- myapp/utils/dfa.py: Core Logic. Berisi kelas DFA_PlatNomor_Web yang menangani logika transisi state automata.
- myapp/views.py: Controller. Menghubungkan frontend dengan logika DFA dan Database.
- myapp/models.py: Database Model. Struktur tabel untuk penyimpanan data plat nomor.
- myapp/management/commands/seed_plates.py: Data Seeder. Script untuk membuat data dummy.
- static/js/script.js: Frontend Logic. Mengatur animasi visualisasi DFA pada browser.

---
## 👥 Tim Pengembang (Kelompok 11)
- Rizqi Atthoriq Ramadhan
- Sayid Muhammad Raffi Raihan Assegaf
- Ihwal Marhamdi
- Reza Pahlevi
- Fadhlan Iman Nur Ichsan
---
© 2025 Program Studi Teknik Informatika - Universitas Muhammadiyah Kalimantan Timur.



