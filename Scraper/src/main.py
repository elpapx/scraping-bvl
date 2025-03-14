from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Configurar Selenium con ChromeDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Opcional: Ejecuta sin abrir ventana
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# URL de la página
url = "https://www.bvl.com.pe/mercado/movimientos-diarios"
driver.get(url)

# Esperar a que la página cargue completamente
driver.implicitly_wait(10)


# Localiza el elemento usando XPath basado en el atributo title
xpath_elemento = "//span[@title='CARTAVIO SOCIEDAD ANONIMA ABIERTA (CARTAVIO S.A.A.)']"
elemento = driver.find_element(By.XPATH, xpath_elemento)

# Imprime el texto contenido en el elemento
print(elemento.text)

# Cierra el navegador
driver.quit()