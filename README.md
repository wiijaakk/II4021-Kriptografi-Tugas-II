# 🕵️‍♂️ II4021 Kriptografi — Tugas II

## 🔐 Steganografi LSB pada Berkas AVI
Proyek ini merupakan implementasi tugas kedua dari mata kuliah II4021 Kriptografi. Program ini berfungsi untuk melakukan embedding dan ekstraksi data pada file video menggunakan teknik steganografi. Selain itu, program ini dilengkapi dengan antarmuka grafis (GUI) untuk mempermudah pengguna dalam menggunakan fitur-fitur yang tersedia.

---

## 📂 Struktur Repository
```
II4021-Kriptografi-Tugas-II/
│
├── core/               # Folder berisi logika utama program
│   ├── A5_1.py         # Implementasi algoritma A5/1
│   ├── embedding.py    # Modul embedding data
│   ├── lsb_core.py     # Logika Least Significant Bit (LSB)
│   ├── metadata.py     # Pengolahan metadata video
│   ├── mp4_core.py     # Manipulasi file MP4
│   ├── stego.py        # Modul utama steganografi
│   ├── tesmanual.py    # Skrip pengujian manual
│   └── video_io.py     # Modul input/output video
│
├── gui/                # Folder berisi antarmuka grafis pengguna
│   ├── crypto_util.py  # Utilitas kriptografi
│   ├── embed_tab.py    # Tab GUI untuk embedding
│   ├── extract_tab.py  # Tab GUI untuk ekstraksi
│   ├── main.py         # Entry point GUI
│   ├── metrics.py      # Penghitungan metrik evaluasi
│   └── stego_service.py# Layanan steganografi untuk GUI
│
└── README.md           # File dokumentasi utama (ini)
```

---

## 📜 Teknologi yang Digunakan
- **Python**: Bahasa pemrograman utama yang digunakan untuk mengembangkan aplikasi ini.
- **PyQt**: Digunakan untuk membangun antarmuka grafis pengguna (GUI).
- **OpenCV**: Digunakan untuk pengolahan video.
- **NumPy**: Digunakan untuk manipulasi data numerik.

---

## 🏃‍♀️ Tata Cara Menjalankan Program

### 1️⃣ Persiapan Lingkungan
Pastikan sudah menginstal **Python 3.8+** dan library berikut:
```bash
pip install PyQt5 opencv-python numpy
```

### 2️⃣ Menjalankan Program
Jalankan file `main.py` yang berada di folder `gui` dengan perintah berikut:
```bash
python gui/main.py
```
Antarmuka grafis akan muncul, dan Anda dapat mulai menggunakan fitur-fitur yang tersedia.

---

## 👥 Anggota Kelompok
| NIM      | Nama Lengkap                       |
|----------|------------------------------------|
| 18223063 | Sendi Putra Alicia  |
| 18223088 | Wijaksara Aptaluhung         |
| 18223097 | Audy Alicia Renatha Tirayoh       |

---
