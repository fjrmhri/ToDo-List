# To-Do List (Pygame)

Aplikasi daftar tugas desktop berbasis Python dan Pygame dengan latar animasi monokrom yang mengikuti kursor, kartu daftar minimalis, dan modal fokus untuk membaca detail.

## Fitur
- Kartu tugas seragam dengan radius membulat dan indikator aksen di sisi kiri.
- Input tanpa border dengan kursor berkedip dan garis bawah; fokus dapat diaktifkan lewat Enter.
- Modal detail dengan latar blur yang menampilkan teks lengkap.
- Sorotan saat hover, checkbox untuk menandai selesai, dan tombol hapus pada setiap item.
- Sistem notifikasi ringan untuk input kosong atau error yang dapat dipulihkan.
- Font Monocraft disertakan lokal untuk tampilan konsisten.

## Instalasi
1. Pastikan Python 3.10+ sudah terpasang.
2. (Disarankan) Buat dan aktifkan virtual environment.
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

## Kontrol / Panduan
- **Enter**: Fokus ke input; saat mengetik, tekan Enter lagi untuk menambah tugas.
- **Klik area input**: Fokus ke input.
- **Klik kartu**: Buka modal detail; **Esc** atau **Enter** menutupnya.
- **Klik checkbox**: Ubah status selesai.
- **Klik X**: Hapus tugas.

## Teknologi
- Python 3.10+
- Pygame 2.5+
- Font Monocraft (tersedia di `todo_app/assets/fonts`)

## Kontribusi
Masukan dan pull request dipersilakan. Usahakan perubahan kecil dan fokus, serta pastikan `python -m py_compile main.py` berjalan tanpa error sebelum mengirim.

## Lisensi
Belum ada lisensi khusus. Perlakukan proyek ini sebagai all-rights-reserved kecuali lisensi ditambahkan.

