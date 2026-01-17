from fastapi import FastAPI
from model import predict

app = FastAPI(title="E-Nose ML Service")

@app.post("/predict")
def prediction(data: dict):
    sensors = data["sensors"]
    features = list(sensors.values())
    result = predict(features)
    return {"class": result}
