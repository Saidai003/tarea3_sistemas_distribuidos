from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

def ensure_topic_exists(admin_client, topic_name, num_partitions=1, replication_factor=1):
    """Verifica o crea un tema en Kafka."""
    try:
        topic_list = [NewTopic(name=topic_name, num_partitions=num_partitions, replication_factor=replication_factor)]
        admin_client.create_topics(new_topics=topic_list, validate_only=False)
        print(f"Topic '{topic_name}' creado exitosamente.")
    except TopicAlreadyExistsError:
        print(f"El topic '{topic_name}' ya existe.")
    except Exception as e:
        print(f"Error al crear el topic '{topic_name}': {e}")

# Configuración del cliente Kafka Admin
admin_client = KafkaAdminClient(
    bootstrap_servers="localhost:9092",  # Cambia por la dirección de tu broker
    client_id='scraper-admin'
)

topic_name = "traffic_data"
ensure_topic_exists(admin_client, topic_name)
