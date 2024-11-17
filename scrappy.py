from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import json
from kafka import KafkaProducer

# Configurar el WebDriver de Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # No abrir ventana de navegador (modo "headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Kafka Producer (enviando datos a Kafka)
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def scrape_waze():
    # Acceder a la página de Waze
    driver.get("https://www.waze.com/livemap")

    # Esperar unos segundos para que la página cargue completamente
    time.sleep(10)  # Ajusta el tiempo según la velocidad de tu conexión

    # Obtener el HTML de la página cargada
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Buscar los eventos de tráfico. Aquí estamos buscando atributos de la estructura HTML que nos mencionaste.
    traffic_data = []

    # Asumiendo que los eventos de tráfico están contenidos en algún contenedor específico:
    # Busca por etiquetas o atributos relevantes que podrían contener los datos (de acuerdo con la información proporcionada)
    events = soup.find_all("div", class_="event_class_name")  # Esto debe ajustarse a la estructura real de Waze

    for event in events:
        # Extraer los atributos relevantes del HTML para los eventos de tráfico
        location = event.get("q", "Unknown Location")  # Nombre de la ubicación
        exp = event.get("exp", "Unknown")
        geo_env = event.get("geo-env", "Unknown")
        sll = event.get("sll", "Unknown")
        lang = event.get("lang", "Unknown")
        top = event.get("top", "Unknown")
        bottom = event.get("bottom", "Unknown")
        left = event.get("left", "Unknown")
        right = event.get("right", "Unknown")
        env = event.get("env", "Unknown")
        types = event.get("types", "Unknown")

        # Crear un diccionario con los datos extraídos
        traffic_data.append({
            "location": location,
            "exp": exp,
            "geo-env": geo_env,
            "sll": sll,
            "lang": lang,
            "top": top,
            "bottom": bottom,
            "left": left,
            "right": right,
            "env": env,
            "types": types
        })

    # Retornar los datos extraídos
    return traffic_data

# Enviar los datos extraídos a Kafka
def send_data_to_kafka(data):
    for event in data:
        producer.send("traffic-events", event)
        print(f"Data sent to Kafka: {event}")

# Función principal para ejecutar el scraping y envío de datos a Kafka
def main():
    while True:
        # Realizar el scraping de Waze
        data = scrape_waze()

        # Enviar los datos a Kafka
        send_data_to_kafka(data)

        # Esperar un tiempo antes de hacer otro scraping
        time.sleep(30)  # Puedes ajustar el tiempo de espera entre las consultas

if __name__ == "__main__":
    main()

    # Cerrar el driver cuando termine
    driver.quit()
