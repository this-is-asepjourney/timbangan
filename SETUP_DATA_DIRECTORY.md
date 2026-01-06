# Setup Directory Penyimpanan Data

## Lokasi Penyimpanan Data

Program menyimpan data di:
```
/home/project/datatimbangan/
```

File yang disimpan:
- `data_timbangan.txt` - Data timbangan real-time
- `kalibrasi.json` - File kalibrasi

## Setup Directory di Raspberry Pi

### 1. Buat Directory (jika belum ada)

```bash
sudo mkdir -p /home/project/datatimbangan
```

### 2. Set Permission

```bash
# Ubah owner ke user yang menjalankan program
sudo chown $USER:$USER /home/project/datatimbangan

# Atau ubah owner ke user tertentu (contoh: pi)
sudo chown pi:pi /home/project/datatimbangan

# Set permission agar bisa ditulis
sudo chmod 755 /home/project/datatimbangan
```

### 3. Verifikasi Permission

```bash
# Cek owner dan permission
ls -la /home/project/

# Harus menunjukkan:
# drwxr-xr-x  pi pi  datatimbangan
```

### 4. Test Write Access

```bash
# Test apakah bisa menulis
touch /home/project/datatimbangan/test.txt
rm /home/project/datatimbangan/test.txt

# Jika berhasil, permission sudah benar
```

## Troubleshooting

### Error: Permission Denied

**Solusi 1: Ubah owner directory**
```bash
sudo chown -R $USER:$USER /home/project/datatimbangan
```

**Solusi 2: Set permission lebih luas (tidak direkomendasikan untuk production)**
```bash
sudo chmod 777 /home/project/datatimbangan
```

**Solusi 3: Buat directory dengan user yang benar**
```bash
# Login sebagai user yang akan menjalankan program
mkdir -p /home/project/datatimbangan
```

### Error: Directory tidak ada

Program akan otomatis membuat directory jika tidak ada, tapi memerlukan permission yang cukup.

Jika gagal, buat manual:
```bash
sudo mkdir -p /home/project/datatimbangan
sudo chown $USER:$USER /home/project/datatimbangan
```

### Error: Cannot create directory

Pastikan:
1. User memiliki permission untuk membuat directory di `/home/project/`
2. Directory `/home/project/` sudah ada
3. Jika tidak ada, buat dulu:
   ```bash
   sudo mkdir -p /home/project
   sudo chown $USER:$USER /home/project
   ```

## Verifikasi di Program

Saat program dijalankan, akan muncul:
```
Memverifikasi directory penyimpanan data...
OK: Directory data siap: /home/project/datatimbangan
```

Jika muncul warning, ikuti instruksi yang ditampilkan.

## Catatan Penting

1. **Directory otomatis dibuat**: Program akan mencoba membuat directory jika tidak ada
2. **Permission check**: Program memverifikasi permission sebelum menyimpan data
3. **Error handling**: Jika gagal, program akan menampilkan instruksi perbaikan
4. **Path absolut**: Menggunakan path absolut untuk menghindari masalah permission

## Struktur Directory

```
/home/project/
└── datatimbangan/
    ├── data_timbangan.txt    # Data timbangan real-time
    └── kalibrasi.json         # File kalibrasi
```

