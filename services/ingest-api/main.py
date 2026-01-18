from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import requests
import os
from datetime import datetime

app = FastAPI(title="E-Nose Ingest API")

# Configuración de InfluxDB (Variables de entorno definidas en docker-compose)
INFLUX_URL = os.getenv("INFLUX_URL", "http://influxdb:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG", "enose_org")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "sensor_data")

# Cliente de InfluxDB
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

class SensorData(BaseModel):
    device_id: str
    timestamp: float
    sensors: dict  # Ej: {"VOC": 0.5, "MQ3": 0.1}

def process_prediction(data: dict):
    """Esta función corre en 'background' sin hacer esperar al sensor"""
    try:
        # Aquí llamarías a tu ML Service
        response = requests.post("http://ml-service:8000/predict", json=data)
        print(f"Predicción para {data['device_id']}: {response.json()}")
        # Opcional: Guardar también el resultado de la predicción en InfluxDB
    except Exception as e:
        print(f"Error conectando con ML Service: {e}")

@app.post("/ingest")
def ingest(data: SensorData, background_tasks: BackgroundTasks):
    try:
        # 1. Guardar en InfluxDB (Persistencia de Datos - CRÍTICO para MLOps)
        point = Point("breath_sample") \
            .tag("device_id", data.device_id) \
            .field("VOC", float(data.sensors.get("VOC", 0))) \
            .field("MQ3", float(data.sensors.get("MQ3", 0))) \
            .field("MQ135", float(data.sensors.get("MQ135", 0))) \
            .field("TEMP", float(data.sensors.get("TEMP", 0))) \
            .time(datetime.utcnow())
        
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)

        # 2. Disparar predicción en segundo plano (No bloquea)
        background_tasks.add_task(process_prediction, data.dict())

        return {"status": "accepted", "message": "Datos guardados y procesando"}
    
    except Exception as e:
        # Log del error real para ti, pero respuesta genérica al cliente
        print(f"Error en ingesta: {e}") 
        raise HTTPException(status_code=500, detail="Error procesando datos")

@app.on_event("shutdown")
def shutdown_db_client():
    client.close()