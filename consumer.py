from kafka import KafkaConsumer
import json

# Crear un consumidor que se conecta al tópico 'traffic-events'
consumer = KafkaConsumer(
    'reportes_trafico',
    bootstrap_servers=['localhost:9093'],
    group_id='traffic-consumer-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# Consumir mensajes y procesarlos
for message in consumer:
    print(f"Received message: {message.value}")
