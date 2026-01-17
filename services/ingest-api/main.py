from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI(title="E-Nose Ingest API")

class SensorData(BaseModel):
    device_id: str
    timestamp: float
    sensors: dict

@app.post("/ingest")
def ingest(data: SensorData):
    # enviar al servicio ML
    response = requests.post(
        "http://ml-service:8001/predict",
        json=data.dict()
    )
    return {
        "status": "ok",
        "prediction": response.json()
    }
