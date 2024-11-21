import json
import time
from seleniumwire import webdriver  # Para interceptar tráfico de red
from kafka import KafkaProducer
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Configurar el productor de Kafka
producer = KafkaProducer(
    bootstrap_servers=['localhost:9093'],  # Dirección del broker de Kafka
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),  # Serializador de valores en JSON
    key_serializer=lambda k: k.encode('utf-8') if k else None,  # Serializador de claves
    retries=3,
    acks='all'  # Asegurando que Kafka confirme la recepción de los mensajes
)

# Configurar Selenium con interceptación de red
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Para ejecutar sin abrir el navegador
driver = webdriver.Chrome(options=options)

# Navegar a la página de Waze
url = "https://www.waze.com/live-map"
driver.get(url)

# Esperar a que cargue la página
driver.implicitly_wait(10)

# Hacer clic en el botón "Entendido"
try:
    boton_entendido = driver.find_element(By.XPATH, "//button[text()='Entendido']")
    print("Botón 'Entendido' encontrado. Haciendo clic...")
    boton_entendido.click()
except Exception as e:
    print("No se encontró el botón 'Entendido':", e)

# Modificar los formularios
try:
    # Campo "Elige el punto de partida"
    punto_partida = driver.find_element(By.CSS_SELECTOR, "div.wm-search__input")
    punto_partida_input = punto_partida.find_element(By.TAG_NAME, "input")
    punto_partida_input.clear()
    punto_partida_input.send_keys("Puente Alto, Región Metropolitana, Chile")
    punto_partida_input.send_keys(Keys.RETURN)

    # Campo "Elige el destino"
    destino = driver.find_elements(By.CSS_SELECTOR, "div.wm-search__input")[1]
    destino_input = destino.find_element(By.TAG_NAME, "input")
    destino_input.clear()
    destino_input.send_keys("Avenida San Carlos 1173, Puente Alto, Atenas, Chile")
    destino_input.send_keys(Keys.RETURN)

    print("Formularios modificados exitosamente.")
except Exception as e:
    print("Error al modificar los formularios:", e)

try:
    print("\nCapturando solicitudes de tipo GeoRSS...")
    for request in driver.requests:
        # Verificar si el contenido es de tipo GeoRSS o contiene "georss?top="
        if "georss?top=" in request.url and request.response:
            print(f"Solicitud capturada: {request.url}")
            # Decodificar la respuesta JSON
            response_data = json.loads(request.response.body.decode("utf-8"))
            print("Datos obtenidos:", json.dumps(response_data, indent=2))

            # Enviar a Kafka
            producer.send(
                topic="reportes_trafico",  # Nombre del tópico en Kafka
                key="georss_data",  # Clave para identificar los mensajes
                value=response_data  # Los datos JSON extraídos
            )
            print("Enviado a Kafka.")

        
except Exception as e:
    print("Error al capturar solicitudes:", e)
    # Cerrar el navegador
    driver.quit()

# Cerrar el productor y el navegador
producer.flush()
producer.close()
driver.quit()
