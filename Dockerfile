# Usa una imagen base de Python 3.9
FROM python:3.9

# Instala dependencias del sistema para ChromeDriver
RUN apt-get update && apt-get install -y wget unzip \
    && wget -q -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip \
    && apt-get install -y chromium-driver

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos necesarios al contenedor
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY wazescraper.py .

# Comando por defecto para ejecutar el script
CMD ["python", "wazescraper.py"]
