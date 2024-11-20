import scrapy
import json

class JsonExtractorSpider(scrapy.Spider):
    name = "json_extractor"
    
    # URL inicial
    start_urls = [
        "https://www.waze.com/es-419/live-map/directions/puente-alto-region-metropolitana-cl?to=place.ChIJwwMqdVLWYpYRki6i0m7kXY8&from=place.Ej5Bdi4gUGFycXVlIGRlbCBFc3RlLCBQdWVudGUgQWx0bywgUmVnacOzbiBNZXRyb3BvbGl0YW5hLCBDaGlsZSIuKiwKFAoSCWUjVCu01mKWEcWW5nMYB-EtEhQKEgnDAyp1UtZilhGSLqLSbuRdjw"
    ]
    
    def parse(self, response):
        # Buscar el contenido del <script type="application/ld+json">
        scripts = response.xpath('//script[@type="application/ld+json"]/text()').getall()
        
        for script in scripts:
            try:
                # Convertir el texto JSON en un diccionario
                json_data = json.loads(script)
                
                # Procesar o guardar los datos
                yield {
                    "data": json_data
                }
            except json.JSONDecodeError:
                self.logger.error("Error decoding JSON")
