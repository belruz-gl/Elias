from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, os


# URL_BASE
LOGIN_URL = 'https://accounts.claveunica.gob.cl/accounts/login/?next=/openid/authorize%3Fclient_id%3D672f76fa24044d36b28fd11b50d7a4ec%26redirect_uri%3Dhttps%253A%252F%252Frsh.ministeriodesarrollosocial.gob.cl%252Facceso%252Fcallback%26response_type%3Dcode%26scope%3Dopenid%2520rut%26state%3D3ece9a112105ed3f5307e12b87a5a373'

#Datos del usuario
USERNAME = REMOVED
PASSWORD = REMOVED

# Carpeta donde se guardaran los PDFs descargados
CARTOLA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "downloaded_Cartola_pdfs")
os.makedirs(CARTOLA_DIR, exist_ok=True)

def setup_driver():
    options = webdriver.ChromeOptions()
    
    # Ocultar la apertura de chrome en proceso de automatizacion...
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Configuracion para descargas automaticas
    prefs = {
        "download.default_directory": CARTOLA_DIR,
        "download.prompt_for_download": False, # (opcional) Mantiene la consistencia de la automatizacion evitando aparocopm de modales de chrome
        "download.directory_upgrade": True, # Permite cambio dinamico del directorio de descarga en la ejecucion del script 
        "safebrowsing.enabled": True, # Descarga segura
        "plugins.always_open_pdf_externally": True  # Evita que el pdf se abra dentro de la automatizacion
    }

    options.add_experimental_option("prefs", prefs)
    
    # Ocultar automatizacion (stealth)
    options.add_argument('--disable-blink-features=AutomationControlled') #Desabilita Motor de renderizado de chrome 
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"]) #Desabilita switch que indica automatizacion

    return webdriver.Chrome(options=options)

def wait_for_element(driver, locator, timeout=30):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located(locator)
    )

def login(driver):
    print("Iniciando sesión...")
    driver.get(LOGIN_URL)
    username_field = wait_for_element(driver, (By.ID, 'uname'))
    username_field.send_keys(USERNAME)
    
    password_field = wait_for_element(driver, (By.ID, 'pword'))
    password_field.send_keys(PASSWORD)
    
    login_button = wait_for_element(driver, (By.XPATH, '//button[contains(text(), "INGRESA")]'))
    driver.execute_script("arguments[0].click();", login_button)
    print("Login exitoso")

def download_file(driver):
    print("Buscando enlace de descarga...")
    
    # Selectores para seleccionar el enlace de descarga del documento
    selectors = [
        (By.XPATH, '//a[contains(@href, "printcartola-ux")]'),
        (By.CSS_SELECTOR, 'a[title*="Cartola"]'),
        (By.PARTIAL_LINK_TEXT, "Descargar Cartola")
    ]
    
    for selector in selectors:
        try:
            link = driver.find_element(*selector)
            break
        except:
            continue
    else:
        raise Exception("No se encontró el enlace de descarga")

    # Descargar archivo
    initial_files = set(os.listdir(CARTOLA_DIR))
    driver.execute_script("arguments[0].click();", link)
    
    # Esperar descarga
    print("Verificando la descarga...")
    start_time = time.time()
    while (time.time() - start_time) < 60:  # 60 segundos max
        time.sleep(2)
        current_files = set(os.listdir(CARTOLA_DIR))
        new_files = current_files - initial_files
        
        # Buscar archivos completos
        completed_files = [
            f for f in new_files
            if f.lower().endswith('.pdf') 
            and not any(f.endswith(ext) for ext in ['.tmp', '.crdownload', '.part'])
        ]
        
        if completed_files:
            file_path = os.path.join(CARTOLA_DIR, completed_files[0])
            print(f"Descarga completada: {file_path}")
            return file_path
    
    raise Exception("La descarga no se completo en el tiempo esperado")

def main():
    driver = None
    try:
        driver = setup_driver()
        login(driver)
        
        # Verificar exito en el logueo
        wait_for_element(driver, (By.XPATH, '//*[contains(text(), "Registro Social") or contains(text(), "RSH")]'))
        
        # Descargar archivo
        file_path = download_file(driver)
        print(f"\nProceso completado. Archivo guardado en:\n{file_path}")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        if driver:
            driver.save_screenshot(os.path.join(CARTOLA_DIR, 'error.png'))
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()