# II4021 Kriptografi — Tugas II

## Steganografi LSB pada Berkas AVI
Proyek ini merupakan implementasi tugas kedua dari mata kuliah II4021 Kriptografi. Program ini berfungsi untuk melakukan embedding dan ekstraksi data pada file video menggunakan teknik steganografi. Selain itu, program ini dilengkapi dengan antarmuka grafis (GUI) untuk mempermudah pengguna dalam menggunakan fitur-fitur yang tersedia.

---

## Struktur Repository
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
├── doc/                # Folder berisi dokumen tugas
│   ├── 18223063_18223088_18223097_Tugas 2_II4021.pdf
│   └── Tugas2-II4021-2026.pdf
│
├── test/               # Folder berisi kasus uji
│   ├── mp4_test/       # Kasus uji untuk file MP4
│   ├── normal_test/    # Kasus uji normal
│   └── overcapacity_test/ # Kasus uji kapasitas berlebih
│
└── README.md           # File dokumentasi utama (ini)
```

---

## Teknologi yang Digunakan
- **Python**: Bahasa pemrograman utama yang digunakan untuk mengembangkan aplikasi ini.
- **PyQt**: Digunakan untuk membangun antarmuka grafis pengguna (GUI).
- **OpenCV**: Digunakan untuk pengolahan video.
- **NumPy**: Digunakan untuk manipulasi data numerik.
- **CustomTkinter**: Digunakan untuk membangun antarmuka grafis berbasis Tkinter dengan tampilan modern.
- **Matplotlib**: Digunakan untuk visualisasi data.

---

## Tata Cara Menjalankan Program

### Persiapan Lingkungan
Pastikan sudah menginstal **Python 3.8+** dan library berikut:
```bash
pip install PyQt5 opencv-python numpy matplotlib
```

### Menjalankan Program
Jalankan file `main.py` yang berada di folder `gui` dengan perintah berikut:
```bash
python gui/main.py
```
Antarmuka grafis akan muncul, dan Anda dapat mulai menggunakan fitur-fitur yang tersedia.

---

## Anggota Kelompok
| NIM      | Nama Lengkap                       |
|----------|------------------------------------|
| 18223063 | Sendi Putra Alicia  |
| 18223088 | Wijaksara Aptaluhung         |
| 18223097 | Audy Alicia Renatha Tirayoh       |

---
