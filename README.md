<p align="center">
  <img src="https://img.shields.io/github/stars/fjrmhri/ToDo-List?style=for-the-badge&logo=github&color=8b5cf6" alt="Stars"/>
  <img src="https://img.shields.io/badge/Lisensi-Non--komersial-10b981?style=for-the-badge" alt="License"/>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/Pygame-2.5%2B-4B8BBE?style=for-the-badge&logo=pygame" alt="Pygame"/>
  <img src="https://img.shields.io/badge/Desktop%20App-Pygame-0ea5e9?style=for-the-badge&logo=windowsterminal" alt="Desktop"/>
</p>

# To-Do List (Pygame)

Aplikasi daftar tugas desktop berbasis Python dan Pygame dengan latar animasi monokrom yang mengikuti kursor, kartu daftar minimalis, dan modal fokus untuk membaca detail.

## Deskripsi Singkat
Aplikasi ini menampilkan daftar tugas sederhana dengan gaya futuristik. Pengguna dapat menambahkan tugas, menandai selesai, menghapus, serta membaca detail di dalam modal. Animasi latar dan efek blur memberikan pengalaman visual tanpa mengubah alur dasar aplikasi todo.

## Fitur Utama
- Kartu tugas seragam dengan radius membulat dan indikator aksen di sisi kiri.
- Input tanpa border dengan kursor berkedip dan garis bawah; fokus dapat diaktifkan lewat Enter atau klik.
- Modal detail dengan latar blur yang menampilkan teks lengkap.
- Sorotan hover, checkbox untuk menandai selesai, dan tombol hapus pada setiap item.
- Sistem notifikasi ringan untuk input kosong atau error yang dapat dipulihkan.
- Font Monocraft disertakan lokal untuk tampilan konsisten.

## Instalasi
1. Pastikan Python 3.10+ sudah terpasang.
2. (Opsional) Buat dan aktifkan virtual environment.
3. Pasang dependensi:
   ```bash
   pip install -r requirements.txt
   ```

## Cara Menjalankan
Dari root proyek:
```bash
python main.py
```
Jendela Pygame akan terbuka dengan daftar tugas dan latar animasi.

## Konfigurasi
- **Font**: Berkas `todo_app/assets/fonts/Monocraft.otf` digunakan bila tersedia. Jika hilang, Pygame akan otomatis memakai font sistem sebagai fallback.
- **Lingkungan**: Tidak ada variabel lingkungan wajib. Pastikan display Anda mendukung jendela Pygame standar.

## Struktur Proyek
- `main.py`: Entry point yang menjalankan aplikasi.
- `todo_app/app.py`: Logika utama UI, event handling, dan render.
- `todo_app/animations.py`: Efek latar gelombang dan jitter input.
- `todo_app/utils.py`: Utilitas rendering teks dan efek blur.
- `todo_app/models.py`: Model data sederhana untuk item todo.

## Lisensi
Belum ada lisensi khusus. Perlakukan proyek ini sebagai all-rights-reserved kecuali lisensi ditambahkan di kemudian hari.
