import time
import requests
import random

URL = "http://localhost:8000/ingest"

while True:
    payload = {
        "device_id": "EN-001",
        "timestamp": time.time(),
        "sensors": {
            "VOC": random.uniform(0.2, 0.9),
            "MQ3": random.uniform(0.1, 0.8),
            "MQ135": random.uniform(0.3, 1.0),
            "TEMP": random.uniform(20, 30)
        }
    }
    r = requests.post(URL, json=payload)
    print(r.json())
    time.sleep(2)
