# Program Timbangan Digital dengan ADS1232

Program Python untuk membaca data timbangan dari ADS1232 dan menampilkannya secara real-time.

## Hardware
- Raspberry Pi 4
- ADS1232 (ADC untuk load cell)
- Load Cell (BENZ WERKZ BZ6150 / NEWTECH NT-15E / KRISBOW TCS-150-ZE61Z)

## Koneksi Hardware

### ADS1232 ke Raspberry Pi:
- **SCLK** → GPIO 11 (SPI0 SCLK)
- **DOUT** → GPIO 9 (SPI0 MISO)
- **DRDY** → GPIO 24 (Data Ready)
- **PDWN** → GPIO 25 (Power Down, opsional)
- **SPEED** → GPIO 23 (Speed, opsional)
- **VCC** → 3.3V atau 5V (sesuai spesifikasi ADS1232)
- **GND** → Ground

### Load Cell ke ADS1232:
- **E+** → AINP
- **E-** → AINN
- **S+** → AINP
- **S-** → AINN

## Instalasi

### Untuk Raspberry Pi (Penggunaan Nyata)

1. Install dependencies:
```bash
pip install RPi.GPIO>=0.7.1 spidev>=3.5
```

2. Aktifkan SPI di Raspberry Pi:
```bash
sudo raspi-config
# Pilih Interface Options → SPI → Enable
```

3. Edit konfigurasi pin di `timbangan.py` jika berbeda:
   - `DRDY_PIN`: Pin untuk Data Ready
   - `PDWN_PIN`: Pin untuk Power Down (opsional)
   - `SPEED_PIN`: Pin untuk Speed (opsional)

### Untuk Windows (Testing/Development)

Program dapat dijalankan di Windows untuk testing tanpa perlu install dependencies Raspberry Pi. Program akan otomatis menggunakan **mode simulasi** dengan data timbangan yang disimulasikan.

Cukup jalankan:
```bash
python timbangan.py
```

**Catatan:** Di Windows, program akan menampilkan data simulasi. Untuk penggunaan nyata, jalankan di Raspberry Pi.

## Kalibrasi

1. Edit konstanta kalibrasi di `timbangan.py`:
   - `SCALE_FACTOR`: Faktor konversi dari raw value ke kg
   - `OFFSET`: Offset untuk zero adjustment

2. Untuk kalibrasi:
   - Jalankan program tanpa beban (tare otomatis)
   - Letakkan beban yang diketahui beratnya
   - Hitung `SCALE_FACTOR = berat_kg / (raw_value - tare_value)`

## Penggunaan

Jalankan program:
```bash
sudo python3 timbangan.py
```

**Catatan:** Program memerlukan akses root untuk menggunakan GPIO dan SPI.

## Fitur

- ✅ Pembacaan data real-time dari ADS1232
- ✅ Tampilan berat dalam satuan kg
- ✅ Auto tare (zero calibration)
- ✅ Simpan data ke file `data_timbangan.txt` (replace setiap update)
- ✅ Format data: Waktu dan Berat

## File Output

Data disimpan di `data_timbangan.txt` dengan format:
```
Waktu: 2024-01-01 12:00:00
Berat: 1.234 kg
```

File akan di-replace setiap kali ada data baru (tidak menumpuk).

