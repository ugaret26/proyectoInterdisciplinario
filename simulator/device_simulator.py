import time
import requests
import random
import math

import os

# Configuración de URL flexible para Docker y local
URL = os.getenv("INGEST_URL", "http://localhost:8000/ingest")

def generate_breath_curve(t, peak_value):
    """Simula la curva de respuesta de un sensor MOS (Metal Oxide)"""
    # Función simple de ataque y decaimiento
    if t < 10: return 0.1 # Línea base
    if t < 20: return 0.1 + (peak_value - 0.1) * ((t-10)/10) # Subida
    if t < 30: return peak_value # Meseta (el paciente está soplando)
    return 0.1 + (peak_value - 0.1) * math.exp(-(t-30)/5) # Recuperación

print("Iniciando simulación de paciente con Diabetes (Simulado)...")
start_time = time.time()

# Simulación de un ciclo de respiración (60 segundos)
for i in range(60):
    # Simulamos Acetona alta (marcador de diabetes) en VOC
    voc_val = generate_breath_curve(i, peak_value=0.85) 
    # Simulamos otros gases normales
    mq3_val = generate_breath_curve(i, peak_value=0.3)
    
    # Añadimos un poco de ruido eléctrico aleatorio (Realismo)
    noise = random.uniform(-0.02, 0.02)
    
    payload = {
        "device_id": "EN-001-PATIENT-X",
        "timestamp": time.time(),
        "sensors": {
            "VOC": max(0, voc_val + noise),
            "MQ3": max(0, mq3_val + noise),
            "MQ135": random.uniform(0.3, 0.35), # Estable
            "TEMP": random.uniform(36.5, 37.0) # Temp corporal
        }
    }
    
    try:
        r = requests.post(URL, json=payload)
        print(f"T={i}s | Estado: {r.status_code} | {r.json().get('message')}")
    except Exception as e:
        print(f"Error de conexión: {e}")
        
    time.sleep(1) # 1 dato por segundo