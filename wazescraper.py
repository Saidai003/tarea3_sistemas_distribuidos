import json
import time
from seleniumwire import webdriver  # Para interceptar tráfico de red
from confluent_kafka import Producer
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Configurar el productor de Kafka
producer = Producer({'bootstrap.servers': 'localhost:9092'})  # Dirección del broker de Kafka

# Callback para confirmar entrega de mensajes
def delivery_report(err, msg):
    if err:
        print(f"Error enviando mensaje: {err}")
    else:
        print(f"Mensaje enviado al tópico {msg.topic()} [partición: {msg.partition()}]")

# Función para inicializar Selenium
def iniciar_selenium():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Para ejecutar sin interfaz gráfica
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

# Función para interactuar con Waze
def interactuar_con_waze(driver):
    driver.get("https://www.waze.com/live-map")
    driver.implicitly_wait(10)

    # Hacer clic en el botón "Entendido"
    try:
        boton_entendido = driver.find_element(By.XPATH, "//button[text()='Entendido']")
        boton_entendido.click()
    except Exception as e:
        print("Botón 'Entendido' no encontrado o ya no es necesario:", e)

    # Modificar los formularios de búsqueda
    try:
        punto_partida = driver.find_element(By.CSS_SELECTOR, "div.wm-search__input")
        punto_partida_input = punto_partida.find_element(By.TAG_NAME, "input")
        punto_partida_input.clear()
        punto_partida_input.send_keys("Puente Alto, Región Metropolitana, Chile")
        punto_partida_input.send_keys(Keys.RETURN)

        destino = driver.find_elements(By.CSS_SELECTOR, "div.wm-search__input")[1]
        destino_input = destino.find_element(By.TAG_NAME, "input")
        destino_input.clear()
        destino_input.send_keys("Avenida San Carlos 1173, Puente Alto, Atenas, Chile")
        destino_input.send_keys(Keys.RETURN)
        print("Formulario completado exitosamente.")
    except Exception as e:
        print("Error al completar los formularios:", e)

# Función para capturar y enviar datos a Kafka
def capturar_y_enviar_datos(driver):
    try:
        print("\nCapturando solicitudes de tipo GeoRSS...")
        for request in driver.requests:
            if "georss?top=" in request.url and request.response:
                print(f"Solicitud capturada: {request.url}")
                response_data = json.loads(request.response.body.decode("utf-8"))
                print("Datos obtenidos:", json.dumps(response_data, indent=2))

                # Enviar a Kafka
                producer.produce(
                    topic="reportes_trafico",
                    key="georss_data",
                    value=json.dumps(response_data),
                    callback=delivery_report
                )
                producer.flush()
                print("Enviado a Kafka.")
    except Exception as e:
        print("Error al capturar y enviar datos:", e)

# Función principal
def main():
    driver = iniciar_selenium()
    try:
        interactuar_con_waze(driver)
        capturar_y_enviar_datos(driver)
    finally:
        driver.quit()
        print("Navegador cerrado.")

if __name__ == "__main__":
    main()
