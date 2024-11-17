from kafka import KafkaConsumer

# Crear un consumidor
consumer = KafkaConsumer('traffic-events', bootstrap_servers=['localhost:9092'])

# Consumir mensajes
for message in consumer:
    print(f"Message: {message.value.decode('utf-8')}")
