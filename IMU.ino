#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

const char* ssid = "Siwi Galuh"; 
const char* password = "12345678";
const char* udpAddress = "172.20.10.2";
const int udpPort = 1234;

bool skenarioA = false; 

WiFiUDP udp;
Adafruit_MPU6050 mpu;

#define N_PARTICLES 1000
float particles[N_PARTICLES];
float weights[N_PARTICLES];
bool pf_initialized = false;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  
  Serial.println();
  Serial.print("Menghubungkan ke WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { 
    delay(500); 
    Serial.print("."); 
  }
  Serial.println("\nWiFi Terhubung!");
  Serial.print("IP Address ESP8266: ");
  Serial.println(WiFi.localIP());
  
  Serial.println("Mencari sensor MPU6050...");
  if (!mpu.begin()) { 
    Serial.println("Gagal menemukan MPU6050! Cek kabel SDA/SCL."); 
    while (1) { delay(10); } 
  }
  Serial.println("MPU6050 Ditemukan!");
  
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
}

void loop() {
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  if (skenarioA) {
    unsigned long startTime = millis();
    unsigned long processTime = millis() - startTime;
    String payload = "A," + String(processTime) + "," + String(a.acceleration.x) + "," + String(a.acceleration.y) + "," + String(a.acceleration.z);
    
    sendUDP(payload);
    Serial.println("Dikirim (Skenario A) -> " + payload);
    
  } else {
    unsigned long startTime = millis();
    
    float filteredX = runParticleFilter(a.acceleration.x);

    unsigned long processTime = millis() - startTime;
    
    String payload = "B," + String(processTime) + "," + String(filteredX) + "," + String(a.acceleration.x) + ",0";
    
    sendUDP(payload);
    Serial.println("Dikirim (Skenario B) -> Waktu Eksekusi: " + String(processTime) + " ms | Hasil: " + String(filteredX));
  }

  delay(100); 
}

void sendUDP(String data) {
  udp.beginPacket(udpAddress, udpPort);
  udp.print(data);
  udp.endPacket();
}

float runParticleFilter(float raw_data) {
  if (!pf_initialized) {
    for (int i = 0; i < N_PARTICLES; i++) {
      particles[i] = raw_data; 
      weights[i] = 1.0 / N_PARTICLES;
    }
    pf_initialized = true;
  }

  float estimate = 0;
  float sum_weights = 0;

  for (int i = 0; i < N_PARTICLES; i++) {
    float noise = ((float)random(-100, 100) / 100.0) * 0.5; 
    particles[i] += noise;
    
    float dist = abs(particles[i] - raw_data);
    weights[i] = exp(-(dist * dist) / 0.1);
    sum_weights += weights[i];

    if (i % 100 == 0) yield(); 
  }

  for (int i = 0; i < N_PARTICLES; i++) {
    weights[i] /= sum_weights;
    estimate += particles[i] * weights[i];
    
    if (i % 100 == 0) yield(); 
  }

  static float new_particles[N_PARTICLES];
  for (int i = 0; i < N_PARTICLES; i++) {
    float beta = (float)random(0, 10000) / 10000.0;
    int index = 0;
    while (beta > weights[index] && index < N_PARTICLES - 1) {
      beta -= weights[index];
      index++;
    }
    new_particles[i] = particles[index];
    
    if (i % 100 == 0) yield(); 
  }

  for (int i = 0; i < N_PARTICLES; i++) {
    particles[i] = new_particles[i];
    weights[i] = 1.0 / N_PARTICLES; 
    
    if (i % 100 == 0) yield(); 
  }

  return estimate;
}