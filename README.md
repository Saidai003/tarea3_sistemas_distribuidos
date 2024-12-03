# Tarea3Distro

Sistema distribuido para el monitoreo y análisis de tráfico urbano en tiempo real, implementado como parte de la Tarea 3 del curso de Sistemas Distribuidos.

## Descripción del Proyecto

Este proyecto utiliza una arquitectura distribuida para procesar y almacenar datos de tráfico urbano en tiempo real proporcionados por la API de Waze. Los datos son procesados mediante Apache Spark, almacenados en Apache Cassandra como datos históricos, y analizados con Elasticsearch y Kibana para visualización. Se utiliza Apache Kafka para la comunicación asíncrona entre los componentes.

## Componentes Principales

- **Waze Scraper**: Obtiene datos de tráfico en tiempo real desde la API de Waze y los envía a Kafka.
- **Apache Kafka**: Actúa como sistema de mensajería para transmitir datos entre componentes.
- **Apache Spark**: Procesa los datos en tiempo real desde Kafka.
- **Kibana**: Visualiza los datos de Elasticsearch.
- **Elasticsearch**: Almacena datos procesados para análisis rápido y consultas.
- **Apache Cassandra**: Almacena datos históricos de tráfico para consultas analíticas profundas.
- **Docker Compose**: Configura y ejecuta todos los servicios necesarios en contenedores.

## Requisitos Previos

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Python 3.9+](https://www.python.org/downloads/)
- [Apache Kafka](https://kafka.apache.org/)
- [Apache Spark](https://spark.apache.org/)
- [Elasticsearch](https://www.elastic.co/)
- [Cassandra](https://cassandra.apache.org/)

## Configuración

### 1. Clonar el Repositorio
```bash
git clone https://github.com/Soundsur/Tarea3Distro.git
cd Tarea3Distro
```

### 2. Configurar el Entorno Virtual

Crear y activar el entorno virtual:

```bash
python3 -m venv venv
source venv/bin/activate
```
Instalar las dependencias:
```bash
pip install -r requirements.txt
```
### 3. Configurar y ejecutar Docker Compose
Desde la raíz del proyecto, ejecutar:
```bash
docker-compose up --build
```
Esto iniciará los servicios de Kafka, Zookeeper, Elasticsearch, Cassandra, y Spark.

### 4. Configuración de Selenium y Chrome

Para que *selenium-wire* funcione con un navegador Chrome en sistemas basados en Linux:

#### 1. Instalar Chrome o Chromium:
```bash
sudo apt update
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb

```
#### 2. Instalar el controlador de Chrome (ChromeDriver):
Verifica tu versión de Chrome/Chromium y descarga el controlador compatible [ChromeDriver]

```bash
wget https://chromedriver.storage.googleapis.com/$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/

```

## Ejecución del Proyecto
### 1. Ejecutar el Waze Scraper
En una nueva terminal, activa el entorno virtual y ejecuta el scraper:
```bash
source venv/bin/activate
python3 wazescraper.py
```
Este componente se encargará de obtener datos de tráfico y enviarlos al tópico *reportes_trafico* en Kafka.

### 2. Procesar Datos con Spark
En otra terminal, activa el entorno virtual y ejecuta el script de Spark:
```bash
source venv/bin/activate
python3 spark.py
```
Esto procesará los datos en tiempo real, guardándolos en Cassandra y Elasticsearch.
### 3. Consultar Datos en Cassandra
Puedes acceder a los datos históricos almacenados en Cassandra mediante el cliente CQL:
```bash

cqlsh
USE waze_keyspace;
SELECT * FROM alerts;

```
### 4. Visualizar Datos en Kibana

Abre Kibana en tu navegador en [http://localhost:5601](http://localhost:5601) y usa las herramientas de visualización para analizar los datos almacenados en Elasticsearch.

## Limpieza del Sistema

Para detener y limpiar todos los contenedores, volúmenes y datos, usa:

```bash

docker-compose down --volumes --rmi all --remove-orphans

```

Notas Adicionales

    Asegúrate de activar el entorno virtual en cada terminal antes de ejecutar cualquier script.
    Los datos en Cassandra están diseñados para consultas analíticas históricas, mientras que Elasticsearch se utiliza para análisis en tiempo real.
    El sistema puede ser escalado horizontalmente mediante la adición de más instancias de consumidores y productores.
    Considerar Readme pensado para OS Ubuntu 24.04.1 por lo tanto para los pip install de requirement es necesario aplicar --break-system-packages
