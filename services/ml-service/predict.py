from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# from model import predict  <-- Reemplazaremos esto eventualmente con MLflow load

app = FastAPI(title="E-Nose ML Service")

class PredictionRequest(BaseModel):
    sensors: dict

# Simulación de carga de modelo (Más adelante usaremos mlflow.pyfunc.load_model)
def dummy_model_predict(features):
    # Lógica temporal: Si VOC es alto, alerta posible enfermedad
    voc_level = features[0]
    if voc_level > 0.7:
        return "Alerta: Posible Marcador Detectado"
    return "Normal"

@app.post("/predict")
def prediction(data: PredictionRequest):
    # 1. Validación Estricta del Orden de Features (Vital para ML)
    # El modelo fue entrenado con un orden específico, debemos respetarlo.
    expected_order = ["VOC", "MQ3", "MQ135", "TEMP"]
    
    try:
        features = []
        for sensor_name in expected_order:
            val = data.sensors.get(sensor_name)
            if val is None:
                raise ValueError(f"Falta el sensor {sensor_name}")
            features.append(val)
            
        # 2. Predicción
        result = dummy_model_predict(features)
        
        return {
            "class": result, 
            "model_version": "v1.0-beta" # Importante para trazabilidad
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))