import folium

# Crear un mapa centrado en una ubicación
mapa = folium.Map(location=[40.730610, -73.935242], zoom_start=12)

# Coordenadas de ejemplo (puedes obtenerlas de los datos de Waze)
coordenadas = [
    (40.730610, -73.935242),
    (40.730000, -73.935000),
    (40.731000, -73.936000)
]

# Añadir marcadores al mapa
for lat, lon in coordenadas:
    folium.Marker([lat, lon]).add_to(mapa)

# Guardar el mapa en un archivo HTML
mapa.save("mapa_waze.html")
