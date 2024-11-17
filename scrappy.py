from kafka import KafkaProducer
import json
import time
import requests
from bs4 import BeautifulSoup

# Kafka Producer
producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def scrape_waze():
    # Simulando la extracción de datos desde Waze (deberías adaptarlo a la estructura real)
    url = "https://www.waze.com/livemap"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Esto es un ejemplo, deberías reemplazarlo con los datos reales del scraping
    traffic_data = [
        {"type": "accident", "location": "Avenida Principal", "severity": "high"},
        {"type": "congestion", "location": "Intersección Central", "severity": "medium"}
    ]
    return traffic_data

while True:
    data = scrape_waze()
    for event in data:
        producer.send("traffic-events", event)
    print("Data sent to Kafka")
    time.sleep(10)
