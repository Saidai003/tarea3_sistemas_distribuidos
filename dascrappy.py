from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

# Configuración del controlador (asegúrate de tener ChromeDriver en tu PATH)
driver = webdriver.Chrome()

# Abre la página web
url = "https://www.waze.com/live-map"  # Cambia por la URL correspondiente
driver.get(url)

# Esperar a que la página cargue completamente (ajusta según la página)
driver.implicitly_wait(5)

# Encontrar el botón con el texto "Entendido"
try:
    boton_entendido = driver.find_element(By.XPATH, "//button[text()='Entendido']")
    # Resaltar visualmente el botón (opcional, para depuración)
    ActionChains(driver).move_to_element(boton_entendido).perform()
    print("Botón 'Entendido' encontrado. Haciendo clic...")
    boton_entendido.click()
except Exception as e:
    print("Error al intentar presionar el botón 'Entendido':", e)

# Cerrar el navegador
driver.quit()
