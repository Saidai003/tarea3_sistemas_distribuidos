from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from kafka import KafkaProducer
import json
import time
from datetime import datetime
import logging

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WazeTrafficScraper:
    def __init__(self, kafka_servers=['localhost:9092'], kafka_topic='traffic-events'):
        self.kafka_topic = kafka_topic
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_servers,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        self.setup_driver()

    def setup_driver(self):
        """Configura el driver de Chrome con opciones headless"""
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("WebDriver configurado exitosamente")

    def get_traffic_data(self, location="Madrid,Spain"):
        """Obtiene datos de tráfico de Waze para una ubicación específica"""
        try:
            # URL de Waze Live Map
            url = f"https://www.waze.com/live-map/{location}"
            self.driver.get(url)
            
            # Esperar a que carguen los elementos de tráfico
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "wm-incidents-widget"))
            )

            # Obtener incidentes de tráfico
            incidents = self.driver.find_elements(By.CSS_SELECTOR, ".wm-incident-item")
            
            traffic_data = []
            for incident in incidents:
                try:
                    incident_data = {
                        'timestamp': datetime.now().isoformat(),
                        'type': incident.get_attribute('data-type'),
                        'subtype': incident.get_attribute('data-subtype'),
                        'location': location,
                        'description': incident.text,
                        'severity': incident.get_attribute('data-severity')
                    }
                    traffic_data.append(incident_data)
                except Exception as e:
                    logger.error(f"Error procesando incidente: {str(e)}")

            return traffic_data

        except Exception as e:
            logger.error(f"Error obteniendo datos de tráfico: {str(e)}")
            return []

    def send_to_kafka(self, data):
        """Envía los datos al tópico de Kafka"""
        try:
            for event in data:
                self.producer.send(self.kafka_topic, value=event)
            self.producer.flush()
            logger.info(f"Enviados {len(data)} eventos a Kafka")
        except Exception as e:
            logger.error(f"Error enviando datos a Kafka: {str(e)}")

    def run(self, locations=["Madrid,Spain"], interval_seconds=300):
        """Ejecuta el scraper continuamente para las ubicaciones especificadas"""
        try:
            while True:
                for location in locations:
                    logger.info(f"Obteniendo datos para {location}")
                    traffic_data = self.get_traffic_data(location)
                    if traffic_data:
                        self.send_to_kafka(traffic_data)
                    
                logger.info(f"Esperando {interval_seconds} segundos para la próxima actualización")
                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            logger.info("Deteniendo el scraper")
            self.cleanup()

    def cleanup(self):
        """Limpia los recursos"""
        self.driver.quit()
        self.producer.close()
        logger.info("Recursos liberados correctamente")

if __name__ == "__main__":
    # Ejemplo de uso
    locations = ["Madrid,Spain", "Barcelona,Spain"]  # Puedes añadir más ciudades
    scraper = WazeTrafficScraper(
        kafka_servers=['localhost:29092'],
        kafka_topic='traffic-events'
    )
    
    try:
        scraper.run(locations=locations, interval_seconds=300)  # Actualiza cada 5 minutos
    except Exception as e:
        logger.error(f"Error en la ejecución principal: {str(e)}")
        scraper.cleanup()