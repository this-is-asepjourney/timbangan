#!/usr/bin/env python3
"""
Program Timbangan Digital dengan ADS1232
Raspberry Pi 4 + ADS1232 + Load Cell
"""

import time
import sys
import platform
import random
import json
import os
from datetime import datetime
from datetime import timezone

# Deteksi platform
IS_RASPBERRY_PI = platform.system() == 'Linux' and 'arm' in platform.machine().lower()

# Import library sesuai platform
if IS_RASPBERRY_PI:
    # Raspberry Pi - gunakan library asli
    import spidev
    import RPi.GPIO as GPIO
else:
    # Windows/Development - gunakan mock
    print("=" * 60)
    print("MODE SIMULASI - Program berjalan di Windows")
    print("Untuk penggunaan nyata, jalankan di Raspberry Pi")
    print("=" * 60)
    print()
    
    # Mock GPIO untuk Windows
    class MockGPIO:
        BCM = 'BCM'
        IN = 0
        OUT = 1
        LOW = 0
        HIGH = 1
        PUD_UP = 1
        
        @staticmethod
        def setmode(mode):
            pass
        
        @staticmethod
        def setwarn(warn):
            pass
        
        @staticmethod
        def setup(pin, mode, pull_up_down=None):
            pass
        
        @staticmethod
        def output(pin, value):
            pass
        
        @staticmethod
        def input(pin):
            # Simulasi: selalu ready (LOW = ready)
            return MockGPIO.LOW
        
        @staticmethod
        def cleanup():
            pass
    
    GPIO = MockGPIO()
    
    # Mock SPI untuk Windows
    class MockSPI:
        def __init__(self):
            self.max_speed_hz = 0
            self.mode = 0
            self._base_weight_kg = 2.0  # Berat dasar simulasi (kg)
            self._last_raw = int(2.0 * 1000000)  # Raw value awal
        
        def open(self, bus, device):
            pass
        
        def readbytes(self, n):
            # Simulasi data timbangan yang lebih realistis
            # Berat stabil dengan variasi kecil (seperti timbangan nyata)
            # Tambahkan sedikit drift dan noise
            noise = random.uniform(-0.01, 0.01)  # Noise kecil ±10g
            self._base_weight_kg += random.uniform(-0.001, 0.001)  # Drift sangat kecil
            
            # Simulasi raw ADC value (dengan scale factor yang masuk akal)
            # Asumsikan 1 kg = 1,000,000 raw units
            weight_kg = self._base_weight_kg + noise
            raw_value = int(weight_kg * 1000000)
            
            # Tambahkan noise kecil pada raw value (±1000 units = ±1g)
            raw_value += random.randint(-1000, 1000)
            
            # Simpan untuk konsistensi
            self._last_raw = raw_value
            
            # Konversi ke 3 byte (24-bit signed)
            if raw_value < 0:
                raw_value = raw_value + 0x1000000
            
            byte1 = (raw_value >> 16) & 0xFF
            byte2 = (raw_value >> 8) & 0xFF
            byte3 = raw_value & 0xFF
            
            return [byte1, byte2, byte3]
        
        def close(self):
            pass
    
    spidev = type('spidev', (), {'SpiDev': MockSPI})()



PDWN_PIN = 10  
SPEED_PIN = 22  
SPI_SCLK_PIN = 11  
SPI_MISO_PIN = 9  

# Konfigurasi SPI
SPI_BUS = 0      # SPI Bus 0 (default)
SPI_DEVICE = 0   # SPI Device 0 (default)
SPI_SPEED = 1000000  # 1 MHz (sesuai dengan ADS1232 spec)


SCALE_FACTOR = 0.0000015  # Faktor skala untuk konversi ke kg
OFFSET = 0.0  # Offset untuk zero adjustment

# File untuk menyimpan data
# Path untuk penyimpanan data di Raspberry Pi
DATA_DIR = "/home/project/datatimbangan"
DATA_FILE = os.path.join(DATA_DIR, "data_timbangan.txt")
CALIBRATION_FILE = os.path.join(DATA_DIR, "kalibrasi.json")  # File untuk menyimpan/memuat kalibrasi


def verify_system_time():
    """
    Verifikasi waktu sistem dan tampilkan informasi waktu
    Returns: (is_valid, time_info)
    """
    try:
        now = datetime.now()
        time_info = {
            'current_time': now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            'date': now.strftime("%Y-%m-%d"),
            'time': now.strftime("%H:%M:%S.%f")[:-3],
            'iso_format': now.isoformat(),
            'timestamp': now.timestamp()
        }
        
        # Cek apakah waktu masuk akal (tidak tahun 1970 atau masa depan terlalu jauh)
        year = now.year
        if year < 2020 or year > 2100:
            return False, time_info
        
        return True, time_info
    except Exception as e:
        print(f"WARNING: Error memverifikasi waktu sistem: {e}")
        return False, {}


def ensure_data_directory():
    """
    Pastikan directory untuk penyimpanan data ada dan memiliki permission yang benar
    """
    try:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR, mode=0o755, exist_ok=True)
            print(f"OK: Directory {DATA_DIR} dibuat")
        
        # Pastikan directory bisa ditulis
        if not os.access(DATA_DIR, os.W_OK):
            print(f"WARNING: Directory {DATA_DIR} tidak bisa ditulis")
            print(f"   Jalankan: sudo chmod 755 {DATA_DIR}")
            print(f"   Atau: sudo chown $USER:$USER {DATA_DIR}")
            return False
        return True
    except PermissionError as e:
        print(f"ERROR: Permission denied saat membuat directory {DATA_DIR}")
        print(f"   Jalankan: sudo mkdir -p {DATA_DIR}")
        print(f"   Lalu: sudo chown $USER:$USER {DATA_DIR}")
        return False
    except Exception as e:
        print(f"ERROR: Gagal membuat directory {DATA_DIR}: {e}")
        return False


def load_calibration():
    """
    Muat nilai kalibrasi dari file kalibrasi.json
    Returns: (tare_value, scale_factor) atau (None, None) jika tidak ada
    """
    try:
        if os.path.exists(CALIBRATION_FILE):
            with open(CALIBRATION_FILE, 'r', encoding='utf-8') as f:
                calibration_data = json.load(f)
            
            tare_value = calibration_data.get('tare_value', 0.0)
            scale_factor = calibration_data.get('scale_factor', SCALE_FACTOR)
            
            print(f"OK: Kalibrasi dimuat dari {CALIBRATION_FILE}")
            print(f"   Tanggal kalibrasi: {calibration_data.get('calibrated_date', 'Tidak diketahui')}")
            print(f"   Load cell: {calibration_data.get('load_cell_type', 'Tidak diketahui')}")
            print(f"   Tare value: {tare_value:.2f}")
            print(f"   Scale factor: {scale_factor:.8f}")
            
            return tare_value, scale_factor
        else:
            print(f"ℹ️  File kalibrasi ({CALIBRATION_FILE}) tidak ditemukan.")
            print(f"   Menggunakan nilai default atau akan melakukan kalibrasi baru...")
            return None, None
    except json.JSONDecodeError as e:
        print(f"WARNING: Error membaca file kalibrasi (format JSON tidak valid): {e}")
        return None, None
    except Exception as e:
        print(f"WARNING: Error memuat kalibrasi: {e}")
        return None, None


def save_calibration(tare_value, scale_factor, load_cell_type="Unknown", max_capacity_kg=50):
    """
    Simpan nilai kalibrasi ke file kalibrasi.json
    """
    try:
        # Ambil waktu real-time dengan presisi milidetik
        now = datetime.now()
        calibrated_timestamp = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Dengan milidetik
        
        calibration_data = {
            'tare_value': float(tare_value),
            'scale_factor': float(scale_factor),
            'calibrated_date': calibrated_timestamp,
            'calibrated_date_iso': now.isoformat(),  # Format ISO standar
            'load_cell_type': load_cell_type,
            'max_capacity_kg': max_capacity_kg,
            'calibration_method': 'auto',
            'samples_taken': 10
        }
        
        with open(CALIBRATION_FILE, 'w', encoding='utf-8') as f:
            json.dump(calibration_data, f, indent=2, ensure_ascii=False)
        
        print(f"OK: Kalibrasi disimpan ke {CALIBRATION_FILE}")
        return True
    except Exception as e:
        print(f"WARNING: Error menyimpan kalibrasi: {e}")
        return False


def verify_pin_safety():
    """
    Verifikasi keamanan konfigurasi pin
    Returns: (is_safe, warnings, errors)
    """
    warnings = []
    errors = []
    
    # Daftar pin yang digunakan - Sesuai dengan ads1232_handler.py (18 pin, TIDAK ADA DRDY)
    used_pins = {
        'PDWN': PDWN_PIN,
        'SPEED': SPEED_PIN,
        'SPI_SCLK': SPI_SCLK_PIN,  # GPIO 11 untuk SPI SCLK
        'SPI_MISO': SPI_MISO_PIN,   # GPIO 9 untuk SPI MISO/DOUT (juga untuk data ready)
    }
    
    # Pin-pin yang tidak boleh digunakan (reserved/system pins)
    reserved_pins = {
        0, 1,   # ID_SD, ID_SC (reserved)
        2, 3,   # I2C SDA, SCL (bisa konflik jika I2C digunakan)
        14, 15, # UART TX, RX (bisa konflik jika UART digunakan)
    }
    
    # Cek konflik dengan reserved pins
    for name, pin in used_pins.items():
        if pin in reserved_pins:
            errors.append(f"⚠️ {name} (GPIO {pin}) adalah reserved pin! Ganti dengan pin lain.")
    
    # Cek duplikasi pin
    pin_values = list(used_pins.values())
    duplicates = [pin for pin in pin_values if pin_values.count(pin) > 1]
    if duplicates:
        errors.append(f"⚠️ Pin duplikat terdeteksi: {set(duplicates)}")
    
    # Cek pin SPI (harus dedicated SPI pins)
    if used_pins['SPI_SCLK'] != 11:
        warnings.append("⚠️ SPI SCLK sebaiknya menggunakan GPIO 11 (dedicated SPI pin)")
    if used_pins['SPI_MISO'] != 9:
        warnings.append("⚠️ SPI MISO sebaiknya menggunakan GPIO 9 (dedicated SPI pin)")
    
    # Cek range pin (GPIO 0-27 untuk Pi 4)
    for name, pin in used_pins.items():
        if pin < 0 or pin > 27:
            errors.append(f"⚠️ {name} (GPIO {pin}) di luar range valid (0-27)")
    
    is_safe = len(errors) == 0
    
    return is_safe, warnings, errors


class ADS1232:
    """Kelas untuk mengontrol ADS1232"""
    
    def __init__(self, pdwn_pin=PDWN_PIN, speed_pin=SPEED_PIN, force_calibration=False):
        # CATATAN: ADS1232 18 pin TIDAK memiliki pin DRDY terpisah
        #          Data ready dideteksi melalui DOUT (SPI_MISO_PIN)
        self.pdwn_pin = pdwn_pin
        self.speed_pin = speed_pin
        self.dout_pin = SPI_MISO_PIN  # DOUT digunakan untuk data ready detection
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarn(False)
        # Setup DOUT sebagai input untuk data ready detection
        GPIO.setup(self.dout_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        if self.pdwn_pin:
            GPIO.setup(self.pdwn_pin, GPIO.OUT)
            GPIO.output(self.pdwn_pin, GPIO.HIGH)  # Power on
        
        if self.speed_pin:
            GPIO.setup(self.speed_pin, GPIO.OUT)
            GPIO.output(self.speed_pin, GPIO.LOW)  # 10 SPS (atau HIGH untuk 80 SPS)
        
        # Setup SPI
        self.spi = spidev.SpiDev()
        self.spi.open(SPI_BUS, SPI_DEVICE)
        self.spi.max_speed_hz = SPI_SPEED
        self.spi.mode = 0b01  # Mode 1: CPOL=0, CPHA=1
        
        # Load atau lakukan kalibrasi
        self.tare_value = 0
        self.scale_factor = SCALE_FACTOR  # Default scale factor
        
        if force_calibration:
            print("🔄 Memaksa kalibrasi baru...")
            self.tare()
            self.save_calibration()
        else:
            # Coba muat kalibrasi yang sudah ada
            loaded_tare, loaded_scale = load_calibration()
            if loaded_tare is not None and loaded_scale is not None:
                self.tare_value = loaded_tare
                self.scale_factor = loaded_scale
                print("OK: Menggunakan kalibrasi yang sudah ada")
                # Lakukan tare ulang untuk zero point yang lebih akurat
                print("🔄 Melakukan tare ulang untuk zero point...")
                self.tare()
                # Update tare_value di file kalibrasi
                self.save_calibration()
            else:
                # Jika tidak ada, lakukan kalibrasi baru
                print("🔄 Melakukan kalibrasi baru...")
                self.tare()
                self.save_calibration()
    
    def is_ready(self):
        """
        Cek apakah data siap dibaca
        Untuk ADS1232 18 pin: DOUT LOW = data ready (tidak ada pin DRDY terpisah)
        """
        return GPIO.input(self.dout_pin) == GPIO.LOW
    
    def read_raw(self):
        """
        Baca data mentah dari ADS1232
        Untuk ADS1232 18 pin: DOUT digunakan untuk mendeteksi data ready
        """
        # Tunggu sampai DOUT LOW (data ready) - sesuai ads1232_handler.py
        timeout = time.time() + 1.0  # Timeout 1 detik
        while GPIO.input(self.dout_pin) == GPIO.HIGH:
            if time.time() > timeout:
                return None
            time.sleep(0.001)
        
        # Baca 3 byte data (24-bit)
        data = self.spi.readbytes(3)
        
        if len(data) != 3:
            return None
        
        # Konversi 24-bit signed integer
        value = (data[0] << 16) | (data[1] << 8) | data[2]
        
        # Convert to signed 24-bit
        if value & 0x800000:
            value = value - 0x1000000
        
        return value
    
    def tare(self, samples=10):
        """Kalibrasi zero point (tare)"""
        print("Melakukan kalibrasi zero point...")
        values = []
        for _ in range(samples):
            raw = self.read_raw()
            if raw is not None:
                values.append(raw)
            time.sleep(0.1)
        
        if values:
            self.tare_value = sum(values) / len(values)
            print(f"Zero point: {self.tare_value:.2f}")
        else:
            print("Gagal melakukan kalibrasi zero point")
    
    def save_calibration(self):
        """Simpan kalibrasi saat ini ke file"""
        # Coba muat info load cell dari file kalibrasi yang ada
        load_cell_type = "BENZ WERKZ BZ6150"
        max_capacity = 50
        
        try:
            if os.path.exists(CALIBRATION_FILE):
                with open(CALIBRATION_FILE, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    load_cell_type = existing_data.get('load_cell_type', load_cell_type)
                    max_capacity = existing_data.get('max_capacity_kg', max_capacity)
        except:
            pass
        
        save_calibration(self.tare_value, self.scale_factor, load_cell_type, max_capacity)
    
    def calibrate_weight(self, known_weight_kg, samples=10):
        """
        Kalibrasi dengan beban yang diketahui
        known_weight_kg: berat yang diketahui dalam kg
        """
        print(f"\n📏 Kalibrasi dengan beban {known_weight_kg} kg...")
        print("Pastikan beban sudah diletakkan di timbangan!")
        time.sleep(2)
        
        values = []
        for i in range(samples):
            raw = self.read_raw()
            if raw is not None:
                values.append(raw)
            print(f"\rMembaca sample {i+1}/{samples}...", end='', flush=True)
            time.sleep(0.1)
        
        print()  # New line
        
        if values:
            avg_raw = sum(values) / len(values)
            adjusted_raw = avg_raw - self.tare_value
            
            if abs(adjusted_raw) > 100:  # Pastikan ada perubahan signifikan
                self.scale_factor = known_weight_kg / adjusted_raw
                print(f"OK: Kalibrasi berhasil!")
                print(f"   Raw value: {avg_raw:.2f}")
                print(f"   Adjusted: {adjusted_raw:.2f}")
                print(f"   Scale factor: {self.scale_factor:.8f}")
                self.save_calibration()
                return True
            else:
                print(f"WARNING: Error: Adjusted raw value terlalu kecil ({adjusted_raw:.2f})")
                print("   Pastikan beban sudah diletakkan dengan benar!")
                return False
        else:
            print("WARNING: Gagal membaca data untuk kalibrasi")
            return False
    
    def read_weight(self):
        """Baca berat dalam kg"""
        raw = self.read_raw()
        if raw is None:
            return None
        
        # Kurangi dengan tare value
        adjusted = raw - self.tare_value
        
        # Konversi ke kg menggunakan scale factor dari kalibrasi
        weight_kg = adjusted * self.scale_factor
        
        return weight_kg
    
    def cleanup(self):
        """Bersihkan resources"""
        self.spi.close()
        GPIO.cleanup()


class TimbanganApp:
    """Aplikasi utama timbangan"""
    
    def __init__(self):
        self.ads = ADS1232()
        self.running = True
    
    def save_to_file(self, weight, timestamp):
        """Simpan data ke file (replace, tidak append) dengan timestamp real-time"""
        try:
            # Pastikan directory ada
            if not ensure_data_directory():
                print("WARNING: Gagal menyimpan data - directory tidak bisa diakses")
                return
            
            # Tulis data ke file
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                f.write(f"Waktu: {timestamp}\n")
                f.write(f"Tanggal: {timestamp.split()[0]}\n")  # Tanggal saja
                f.write(f"Jam: {timestamp.split()[1]}\n")  # Waktu saja
                f.write(f"Berat: {weight:.3f} kg\n")
                # Tambahkan timestamp dalam format ISO untuk kompatibilitas
                f.write(f"Timestamp: {timestamp}\n")
        except PermissionError as e:
            print(f"\nERROR: Permission denied saat menyimpan data ke {DATA_FILE}")
            print(f"   Jalankan: sudo chown $USER:$USER {DATA_DIR}")
            print(f"   Atau: sudo chmod 755 {DATA_DIR}")
        except Exception as e:
            print(f"Error menyimpan data: {e}")
    
    def display_weight(self, weight):
        """Tampilkan berat di console"""
        if weight is not None:
            # Format tampilan
            print(f"\rBerat: {weight:8.3f} kg    ", end='', flush=True)
        else:
            print(f"\rBerat: ERROR          ", end='', flush=True)
    
    def run(self):
        """Jalankan aplikasi utama"""
        print("=" * 50)
        print("Program Timbangan Digital")
        print("Tekan Ctrl+C untuk keluar")
        print("=" * 50)
        print()
        
        try:
            while self.running:
                weight = self.ads.read_weight()
                # Ambil waktu real-time dengan presisi milidetik
                now = datetime.now()
                timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
                timestamp_ms = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Dengan milidetik
                
                if weight is not None:
                    # Tampilkan di console
                    self.display_weight(weight)
                    
                    # Simpan ke file (replace) dengan timestamp lengkap
                    self.save_to_file(weight, timestamp_ms)
                
                time.sleep(0.1)  # Update setiap 100ms
        
        except KeyboardInterrupt:
            print("\n\nProgram dihentikan oleh user")
        except Exception as e:
            print(f"\n\nError: {e}")
        finally:
            self.ads.cleanup()
            print("Program selesai")


def main():
    """Fungsi utama"""
    try:
        # Pastikan directory data ada dan bisa diakses
        if IS_RASPBERRY_PI:
            print("Memverifikasi directory penyimpanan data...")
            if not ensure_data_directory():
                print("WARNING: Directory data tidak bisa diakses, program tetap berjalan")
                print(f"   File akan dicoba disimpan di: {DATA_FILE}")
            else:
                print(f"OK: Directory data siap: {DATA_DIR}")
            print()
        
        # Verifikasi waktu sistem
        print("Memverifikasi waktu sistem...")
        is_time_valid, time_info = verify_system_time()
        if is_time_valid:
            print(f"OK: Waktu sistem valid")
            print(f"   Tanggal: {time_info['date']}")
            print(f"   Waktu: {time_info['time']}")
            print(f"   Timestamp lengkap: {time_info['current_time']}")
        else:
            print(f"WARNING: Waktu sistem mungkin tidak valid!")
            print(f"   Pastikan Raspberry Pi sudah disinkronkan dengan NTP")
            print(f"   Jalankan: sudo timedatectl set-ntp true")
        print()
        
        # Verifikasi keamanan pin sebelum memulai
        if IS_RASPBERRY_PI:
            print("Memverifikasi konfigurasi pin...")
            is_safe, warnings, errors = verify_pin_safety()
            
            if errors:
                print("\n❌ ERROR: Masalah keamanan pin terdeteksi:")
                for error in errors:
                    print(f"  {error}")
                print("\n⚠️  Program tidak dapat dilanjutkan. Perbaiki konfigurasi pin terlebih dahulu.")
                return
            
            if warnings:
                print("\n⚠️  PERINGATAN:")
                for warning in warnings:
                    print(f"  {warning}")
            
            if is_safe and not warnings:
                print("✅ Konfigurasi pin aman dan valid")
            print()
        
        app = TimbanganApp()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        if IS_RASPBERRY_PI:
            GPIO.cleanup()


if __name__ == "__main__":
    main()

