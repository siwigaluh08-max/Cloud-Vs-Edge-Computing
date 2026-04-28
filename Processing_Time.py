import socket
import time
import matplotlib.pyplot as plt
import numpy as np

UDP_IP = "0.0.0.0"
UDP_PORT = 1234

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

N_PARTICLES = 1000
particles = np.zeros(N_PARTICLES)
weights = np.ones(N_PARTICLES) / N_PARTICLES

def particle_filter_python(raw_data):
	global particles, weights

	particles += np.random.normal(0, 0.5, N_PARTICLES)
	weights *= np.exp(-((particles - raw_data)**2) / 0.1)
	weights += 1.e-300
	weights /= sum(weights)

	filtered_value = np.sum(particles * weights)

	indices = np.random.choice(np.arange(N_PARTICLES), size=N_PARTICLES, p=weights)
	particles = particles[indices]
	weights.fill(1.0 / N_PARTICLES)

	return filtered_value
print("Menunggu data UDP...")

while True:
	data, addr = sock.recvfrom(1024)
	payload = data.decode('utf-8').split(',')

	tipe_skenario = payload[0]

	if tipe_skenario == 'A':
		raw_x = float(payload[2])

		start_time = time.time()
		filtered_x = particle_filter_python(raw_x)
		process_time_ms = (time.time() - start_time) * 1000

		print(f"skenario A (Cloud) - Waktu Proses Python: {process_time_ms:.2f} ms")

	elif tipe_skenario == 'B':
		esp_process_time = float(payload[1])
		filtered_x = float(payload[2])

		print(f"Skenario B (Edge) - Waktu Proses : {esp_process_time} ms")

