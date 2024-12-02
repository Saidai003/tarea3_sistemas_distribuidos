import requests
import json

def save_to_elasticsearch(data):
    url = "http://localhost:9200/waze/_doc"  # URL del índice en Elasticsearch
    headers = {"Content-Type": "application/json"}

    for row in data:
        try:
            # Convertir cada fila a JSON y enviarla a Elasticsearch
            response = requests.post(url, headers=headers, data=json.dumps(row))
            if response.status_code == 201:  # Código HTTP para "Created"
                print(f"Guardado en Elasticsearch: {row}")
            else:
                print(f"Error al guardar en Elasticsearch: {response.text}")
        except Exception as e:
            print(f"Excepción al intentar guardar en Elasticsearch: {e}")
