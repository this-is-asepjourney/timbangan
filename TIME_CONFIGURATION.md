# Konfigurasi Waktu Real-Time - Timbangan Digital

## ✅ Fitur Waktu Real-Time

Program menggunakan **waktu sistem real-time** yang diambil setiap kali data timbangan disimpan. Waktu diambil langsung dari sistem operasi menggunakan `datetime.now()`.

### Format Waktu

Program menyimpan waktu dalam format lengkap dengan presisi milidetik:

```
Format: YYYY-MM-DD HH:MM:SS.mmm
Contoh: 2026-01-06 07:59:16.873
```

### Informasi Waktu yang Disimpan

Setiap data timbangan menyimpan:
1. **Waktu lengkap**: `2026-01-06 07:59:16.873` (dengan milidetik)
2. **Tanggal**: `2026-01-06` (untuk kemudahan parsing)
3. **Jam**: `07:59:16.873` (untuk kemudahan parsing)
4. **Timestamp ISO**: Format standar ISO 8601

### File Output

Data disimpan di `data_timbangan.txt` dengan format:
```
Waktu: 2026-01-06 07:59:16.873
Tanggal: 2026-01-06
Jam: 07:59:16.873
Berat: 1.234 kg
Timestamp: 2026-01-06 07:59:16.873
```

## ⚙️ Sinkronisasi Waktu Sistem (Raspberry Pi)

### Penting: Pastikan Waktu Sistem Akurat!

Waktu sangat penting untuk data timbangan. Pastikan Raspberry Pi sudah disinkronkan dengan server waktu (NTP).

### 1. Cek Status Waktu Sistem

```bash
timedatectl status
```

### 2. Aktifkan NTP (Network Time Protocol)

```bash
sudo timedatectl set-ntp true
```

### 3. Verifikasi Sinkronisasi

```bash
# Cek apakah NTP aktif
timedatectl show | grep NTPSynchronized

# Hasil harus: NTPSynchronized=yes
```

### 4. Set Timezone (Opsional)

```bash
# List timezone yang tersedia
timedatectl list-timezones

# Set timezone (contoh: Asia/Jakarta)
sudo timedatectl set-timezone Asia/Jakarta
```

### 5. Set Waktu Manual (Jika NTP tidak tersedia)

```bash
# Format: YYYY-MM-DD HH:MM:SS
sudo timedatectl set-time "2026-01-06 08:00:00"
```

## 🔍 Verifikasi Waktu di Program

Program secara otomatis memverifikasi waktu sistem saat dimulai:

```
Memverifikasi waktu sistem...
OK: Waktu sistem valid
   Tanggal: 2026-01-06
   Waktu: 07:59:16.873
   Timestamp lengkap: 2026-01-06 07:59:16.873
```

Jika waktu tidak valid (misalnya tahun 1970 atau masa depan terlalu jauh), program akan memberikan peringatan.

## 📊 Presisi Waktu

- **Update rate**: Setiap 100ms (10 kali per detik)
- **Presisi timestamp**: Milidetik (3 digit)
- **Akurasi**: Tergantung akurasi waktu sistem Raspberry Pi

## ⚠️ Troubleshooting

### Masalah: Waktu tidak akurat

**Solusi:**
1. Pastikan Raspberry Pi terhubung ke internet untuk sinkronisasi NTP
2. Cek status NTP: `timedatectl status`
3. Restart service NTP: `sudo systemctl restart systemd-timesyncd`

### Masalah: Waktu menunjukkan tahun 1970

**Penyebab:** Raspberry Pi tidak memiliki RTC (Real-Time Clock) dan tidak terhubung ke internet.

**Solusi:**
1. Hubungkan ke internet untuk sinkronisasi NTP
2. Atau set waktu manual: `sudo timedatectl set-time "YYYY-MM-DD HH:MM:SS"`

### Masalah: Waktu tidak update saat program berjalan

**Penyebab:** Program mengambil waktu setiap loop, jadi waktu selalu real-time.

**Verifikasi:** Cek file `data_timbangan.txt` - waktu harus berbeda setiap kali file diupdate.

## 📝 Catatan Penting

1. **Waktu Real-Time**: Program mengambil waktu dari sistem setiap kali data disimpan (bukan sekali di awal)
2. **Presisi Tinggi**: Menggunakan milidetik untuk presisi lebih tinggi
3. **Format Standar**: Menggunakan format ISO 8601 untuk kompatibilitas
4. **Verifikasi Otomatis**: Program memverifikasi waktu sistem saat dimulai

## 🔗 Referensi

- [Raspberry Pi Time Configuration](https://www.raspberrypi.org/documentation/configuration/date-time.md)
- [systemd-timesyncd Documentation](https://www.freedesktop.org/software/systemd/man/systemd-timesyncd.service.html)
- [ISO 8601 Date Format](https://en.wikipedia.org/wiki/ISO_8601)

