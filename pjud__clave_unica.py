from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Variables globales
"""
Ingresar usuario y contraseña

"""
USERNAME = 'USERNAME'
PASSWORD = 'PASSWORD'
LOGIN_URL = "https://accounts.claveunica.gob.cl/accounts/login/?next=/openid/authorize%3Fclient_id%3Dd602a0071f3f4db8b37a87cffd89bf23%26redirect_uri%3Dhttps%253A%252F%252Foficinajudicialvirtual.pjud.cl%252Fclaveunica%252Freturn.php%253Fboton%253D1%26response_type%3Dcode%26scope%3Dopenid%2Brut%26state%3DeyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvb2ZpY2luYWp1ZGljaWFsdmlydHVhbC5wanVkLmNsIiwiYXVkIjoiaHR0cHM6XC9cL29maWNpbmFqdWRpY2lhbHZpcnR1YWwucGp1ZC5jbCIsImlhdCI6MTc0NTUwOTExMCwiZXhwIjoxNzQ1NTEwMDEwLCJkYXRhIjoiWW1uNzRYZVwvVmt1Z2hNeUl1S0VLUkx0RzhGOEpSdWt5eVBrMjdCeUNsdEk9In0.FBeGmLkfZMXocRwqAHbYsQ8VaTizzT1ccvKrpvxNjuk"



def setup_driver():
    options = webdriver.ChromeOptions()
    
    # Configuración
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Para evitar detección de automatización
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    
    return webdriver.Chrome(options=options)

def wait_for_element(driver, locator, timeout=30):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located(locator)
    )

def wait_for_clickable(driver, locator, timeout=30):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable(locator)
    )

def login_to_pjud(driver):
    try:
        # Esperar a que cargue la página de Clave Única
        print("Esperando página de Clave Única...")
        username_field = wait_for_element(driver, (By.ID, 'uname'))
        
        # Ingresar credenciales
        print("Ingresando credenciales...")
        username_field.send_keys(USERNAME)
        
        password_field = wait_for_element(driver, (By.ID, 'pword'))
        password_field.send_keys(PASSWORD)
        
        # Hacer clic en el botón de ingreso
        login_button = wait_for_element(driver, (By.XPATH, '//button[contains(text(), "INGRESA")]'))
        driver.execute_script("arguments[0].click();", login_button)
        
        # Verificar que el login fue exitoso esperando algún elemento de la página tras el login
        print("Verificando inicio de sesión...")
        wait_for_element(driver, (By.XPATH, '//*[contains(text(), "Oficina Judicial Virtual") or contains(@class, "user-profile")]'), 30)
        
        print("Inicio de sesión exitoso!")
        return True
        
    except Exception as e:
        print(f"Error durante el proceso de login: {str(e)}")
        return False

def main():
    driver = None
    try:
        print("Iniciando navegador...")
        driver = setup_driver()
        
        # Accede a la página de login de Clave Única
        print("Accediendo directamente a la página de login...")
        driver.get(LOGIN_URL)
        
        # Llama a la función de login
        login_success = login_to_pjud(driver)
        
        if login_success:
            print("Login completado con éxito")
        else:
            print("No se pudo completar el proceso de login")
        
        # Esperar a que el usuario presione Enter para cerrar el navegador
        input("\nPresione Enter para cerrar el navegador...")
            
    except Exception as e:
        print(f"Error en la ejecución principal: {str(e)}")
        # Aún con error, esperamos a que el usuario decida cerrar
        input("\nPresione Enter para cerrar el navegador...")
    finally:
        if driver:
            print("Cerrando el navegador...")
            driver.quit()
            
if __name__ == "__main__":
    main()