from kafka import KafkaProducer
import json
import logging

# Set up logging to debug connection issues if needed
logging.basicConfig(level=logging.INFO)

# Create a Kafka producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9093'],  # Replace with your Kafka broker's address
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),  # Serialize value to JSON
    key_serializer=lambda k: k.encode('utf-8') if k else None,  # Serialize key if provided
    retries=3,  # Retry on failure
    acks='all'  # Wait for acknowledgment from all replicas
)

# Send messages

try:
    for i in range(10):
        producer.send(
            topic='reportes_trafico',  # Replace with your topic name
            key=f'key-{i}',  # Optional key
            value={'number': i}  # Value to send
        )
        print(f"Message {i} sent to topic 'my-topic'")
except Exception as e:
    print(f"Error sending message: {e}")
finally:
    producer.flush()  # Ensure all messages are sent before exiting
    producer.close()
