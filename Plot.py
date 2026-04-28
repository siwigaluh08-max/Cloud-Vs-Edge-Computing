import socket
import numpy as np
import matplotlib.pyplot as plt

# --- KONFIGURASI JARINGAN ---
UDP_IP = "0.0.0.0"
UDP_PORT = 1234
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# --- VARIABEL PENYIMPAN DATA ---
JUMLAH_SAMPEL = 100 # Berapa banyak data yang direkam sebelum grafik muncul
raw_data_list = []
filtered_data_list = []

# --- FUNGSI PARTICLE FILTER (Skenario A) ---
N_PARTICLES = 1000
particles = np.zeros(N_PARTICLES)
weights = np.ones(N_PARTICLES) / N_PARTICLES
pf_initialized = False

def run_particle_filter(raw_val):
    global particles, weights, pf_initialized
    if not pf_initialized:
        particles = np.ones(N_PARTICLES) * raw_val
        pf_initialized = True

    particles += np.random.normal(0, 0.5, N_PARTICLES)
    weights *= np.exp(-((particles - raw_val)**2) / 0.1)
    
    sum_w = sum(weights)
    if sum_w == 0: sum_w = 1e-9 # Pengaman NaN
    weights /= sum_w
    
    filtered_val = np.sum(particles * weights)
    
    indices = np.random.choice(np.arange(N_PARTICLES), size=N_PARTICLES, p=weights)
    particles = particles[indices]
    weights.fill(1.0 / N_PARTICLES)
    return filtered_val

print(f"Merekam {JUMLAH_SAMPEL} sampel data... Silakan goyangkan sensor IMU Anda!")

skenario_saat_ini = "Unknown"

# --- PROSES PEREKAMAN DATA ---
while len(raw_data_list) < JUMLAH_SAMPEL:
    data, addr = sock.recvfrom(1024)
    payload = data.decode('utf-8').split(',')
    skenario_saat_ini = payload[0]
    
    if skenario_saat_ini == 'A':
        raw_x = float(payload[2])
        filtered_x = run_particle_filter(raw_x)
        
        raw_data_list.append(raw_x)
        filtered_data_list.append(filtered_x)
        print(f"Merekam Skenario A... ({len(raw_data_list)}/{JUMLAH_SAMPEL})")
        
    elif skenario_saat_ini == 'B':
        filtered_x = float(payload[2])
        raw_x = float(payload[3]) # Mengambil raw data yang baru kita tambahkan di Arduino
        
        raw_data_list.append(raw_x)
        filtered_data_list.append(filtered_x)
        print(f"Merekam Skenario B... ({len(raw_data_list)}/{JUMLAH_SAMPEL})")

print("Perekaman selesai! Menampilkan grafik...")

# --- PROSES MENGGAMBAR GRAFIK UNTUK LAPORAN ---
plt.figure(figsize=(10, 5))
plt.plot(raw_data_list, label='Raw Data (Sinyal Mentah Kasar)', color='lightgray', linestyle='--')

if skenario_saat_ini == 'A':
    plt.plot(filtered_data_list, label='Filtered Cloud (Skenario A)', color='blue', linewidth=2)
    plt.title("Hasil Pengujian Skenario A (Cloud Computing)")
elif skenario_saat_ini == 'B':
    plt.plot(filtered_data_list, label='Filtered Edge (Skenario B)', color='red', linewidth=2)
    plt.title("Hasil Pengujian Skenario B (Edge Computing)")

plt.xlabel("Sampel Waktu")
plt.ylabel("Akselerasi (Sumbu X)")
plt.legend()
plt.grid(True)
plt.show() # Ini akan memunculkan jendela grafik
