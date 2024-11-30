import requests
import json


class JsonExtractorSpider(scrapy.Spider):
    # URL de la API
    url = "https://www.waze.com/live-map/api/georss?top=-33.531790034965724&bottom=-33.647275000141605&left=-70.64961137909596&right=-70.53466692108815&env=row&types=alerts,traffic"

    def fetch_and_process_waze_data():
        try:
            # Realizar la solicitud GET a la API
            response = requests.get(url)
            response.raise_for_status()  # Verificar errores HTTP

            # Parsear el contenido JSON
            data = response.json()

            # Procesar las alertas
            alerts = data.get("alerts", [])
            for alert in alerts:
                city = alert.get("city", "Desconocido")
                type_alert = alert.get("type", "Sin tipo")
                street = alert.get("street", "Desconocido")
                description = alert.get("reportDescription", "Sin descripción")
                location = alert.get("location", {})

                # Obtener coordenadas si están disponibles
                lat = location.get("y", "Desconocida")
                lon = location.get("x", "Desconocida")

                # Imprimir la información procesada
                print(f"Ciudad: {city}")
                print(f"Tipo: {type_alert}")
                print(f"Calle: {street}")
                print(f"Descripción: {description}")
                print(f"Ubicación: Latitud {lat}, Longitud {lon}")
                print("-" * 40)

        except requests.RequestException as e:
            print(f"Error al realizar la solicitud a la API: {e}")
        except json.JSONDecodeError:
            print("Error al decodificar la respuesta JSON")

# Llamar a la función
if __name__ == "__main__":
    fetch_and_process_waze_data()
