# Konfigurasi Pin ADS1232 - Timbangan Digital

## Pin Mapping (BCM Mode)

| ADS1232 Pin | Function | Raspberry Pi GPIO | Physical Pin | Direction | Status |
|-------------|----------|-------------------|--------------|-----------|--------|
| SCLK        | Clock    | GPIO 11 (SPI0 SCLK) | Pin 23     | Output    | ✅ Dedicated SPI |
| DOUT        | Data Out | GPIO 9 (SPI0 MISO)  | Pin 21     | Input     | ✅ Dedicated SPI |
| PDWN        | Power Down | GPIO 10          | Pin 19     | Output    | ✅ Safe GPIO |
| SPEED       | Speed Select | GPIO 22        | Pin 15     | Output    | ✅ Safe GPIO |
| DRDY        | Data Ready | GPIO 24         | Pin 18     | Input     | ✅ Safe GPIO |
| VCC         | Power 5V | 5V                | Pin 2/4    | Power     | ✅ Power |
| GND         | Ground   | GND               | Pin 6/9/14 | Ground    | ✅ Ground |

## Verifikasi Keamanan

### ✅ Pin yang Aman Digunakan

1. **GPIO 11 (SCLK)** - Dedicated SPI pin
   - Tidak akan konflik dengan fungsi lain
   - Hardwired ke SPI0 SCLK
   - ✅ **AMAN**

2. **GPIO 9 (DOUT/MISO)** - Dedicated SPI pin
   - Tidak akan konflik dengan fungsi lain
   - Hardwired ke SPI0 MISO
   - ✅ **AMAN**

3. **GPIO 10 (PDWN)** - GPIO biasa
   - Tidak reserved
   - Tidak konflik dengan fungsi sistem
   - ✅ **AMAN**

4. **GPIO 22 (SPEED)** - GPIO biasa
   - Tidak reserved
   - Tidak konflik dengan fungsi sistem
   - ✅ **AMAN**

5. **GPIO 24 (DRDY)** - GPIO biasa
   - Tidak reserved
   - Tidak konflik dengan fungsi sistem
   - ✅ **AMAN**

### ⚠️ Catatan Penting

- **Logic Level**: Semua pin GPIO menggunakan 3.3V logic level (aman untuk ADS1232)
- **Power Supply**: ADS1232 menggunakan 5V dari Pin 2/4 (aman, sesuai spec)
- **Ground**: Pastikan ground terhubung dengan baik untuk mengurangi noise
- **SPI Speed**: 1 MHz (sesuai dengan ADS1232 specification)

## Load Cell Connection

| Load Cell Wire | Color | ADS1232 Pin | Function |
|----------------|-------|-------------|----------|
| E+ (Excitation+) | Red   | AVDD / REFP | Excitation+ |
| E- (Excitation-) | Black | AGND / REFN | Excitation- |
| A+ (Signal+)    | White | AINP        | Signal+ |
| A- (Signal-)    | Blue  | AINN        | Signal- |

## Speed Settings

| SPEED Pin | Sampling Rate | Use Case |
|-----------|---------------|----------|
| LOW (0)   | 10 Hz         | High precision, slow response (default) |
| HIGH (1)  | 80 Hz         | Fast response, lower precision |

Program saat ini menggunakan **LOW (10 Hz)** untuk presisi tinggi.

## Troubleshooting

### Jika Pin Tidak Berfungsi:

1. **Cek koneksi fisik** - Pastikan semua kabel terhubung dengan benar
2. **Cek SPI aktif** - Jalankan `sudo raspi-config` dan aktifkan SPI
3. **Cek permission** - Program harus dijalankan dengan `sudo` untuk akses GPIO
4. **Cek pin conflict** - Pastikan tidak ada program lain yang menggunakan pin yang sama

### Jika Data Tidak Akurat:

1. **Grounding** - Pastikan ground terhubung dengan baik
2. **Power supply** - Pastikan 5V stabil (gunakan multimeter)
3. **Kabel** - Gunakan kabel pendek dan tebal untuk mengurangi noise
4. **Kalibrasi** - Lakukan kalibrasi dengan beban yang diketahui

## Kesimpulan

✅ **Konfigurasi pin AMAN dan VALID**
- Tidak ada konflik dengan pin reserved
- Tidak ada duplikasi pin
- Semua pin dalam range valid
- SPI pins menggunakan dedicated pins
- Logic level sesuai (3.3V)

Program siap digunakan dengan konfigurasi ini!

