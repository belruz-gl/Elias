from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Variables globales
BASE_URL = "https://oficinajudicialvirtual.pjud.cl/home/"
USERNAME = REMOVED
PASSWORD = REMOVED

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
        wait_for_element(driver, (By.XPATH, '//*[contains(text(), "Oficina Judicial Virtual")]'), 30)
        
        print("Inicio de sesión exitoso!")
        return True
        
    except Exception as e:
        print(f"Error durante el proceso de login: {str(e)}")
        return False

def navigate_to_mis_causas(driver):
    try:
        print("Navegando a 'Mis Causas'...")
        
        mis_causas_link = wait_for_clickable(driver, (By.XPATH, "//a[contains(@onclick, 'misCausas')]"))
        
        # Ejecutar JavaScript directamente para llamar a la función misCausas()
        driver.execute_script("misCausas();")
        
        # Esperar a que cargue la página de Mis Causas
        print("Esperando que cargue la página de Mis Causas...")
        time.sleep(3) 
        
        print("Navegación a 'Mis Causas' exitosa!")
        return True
        
    except Exception as e:
        print(f"Error al navegar a 'Mis Causas': {str(e)}")
        # Intento alternativo haciendo clic directamente en el elemento
        try:
            print("Intentando método alternativo para 'Mis Causas'...")
            mis_causas_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Mis Causas')]")
            driver.execute_script("arguments[0].click();", mis_causas_link)
            time.sleep(3)
            return True
        except Exception as e2:
            print(f"Error en el segundo intento: {str(e2)}")
            return False

def navigate_to_estado_diario(driver):
    try:
        print("Navegando a 'Mi Estado Diario'...")
        
        estado_diario_link = wait_for_clickable(driver, (By.XPATH, "//a[contains(@onclick, 'miEstadoDiario')]"))
        
        # Ejecutar JavaScript directamente para llamar a la función miEstadoDiario()
        driver.execute_script("miEstadoDiario();")
        
        # Esperar a que cargue la página
        print("Esperando que cargue la página de Mi Estado Diario...")
        time.sleep(3) 
        
        print("Navegación a 'Mi Estado Diario' exitosa!")
        return True
        
    except Exception as e:
        print(f"Error al navegar a 'Mi Estado Diario': {str(e)}")
        # Intento alternativo haciendo clic directamente en el elemento
        try:
            print("Intentando método alternativo para 'Mi Estado Diario'...")
            estado_diario_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Mi Estado Diario')]")
            driver.execute_script("arguments[0].click();", estado_diario_link)
            time.sleep(3)
            return True
        except Exception as e2:
            print(f"Error en el segundo intento: {str(e2)}")
            return False

def main():
    driver = None
    try:
        print("Iniciando navegador...")
        driver = setup_driver()
        
        # Abrir la página principal
        print("Accediendo a la página principal...")
        driver.get(BASE_URL)
        
        # Esperar y hacer clic en "Todos los servicios"
        print("Buscando botón 'Todos los servicios'...")
        todos_servicios_btn = wait_for_clickable(driver, (By.XPATH, "//button[contains(text(), 'Todos los servicios') or contains(@class, 'todos-servicios')]"))
        todos_servicios_btn.click()
        
        # Esperar y hacer clic en "Clave Única"
        print("Buscando opción 'Clave Única'...")
        clave_unica_btn = wait_for_clickable(driver, (By.XPATH, "//a[contains(text(), 'Clave Única')]"))
        clave_unica_btn.click()
        
        # Llamar a la función de login cuando ya estamos en la página de Clave Única
        login_success = login_to_pjud(driver)
        
        if login_success:
            print("Login completado con éxito")
            
            # Dar un tiempo para que la página principal se cargue completamente
            time.sleep(3)
            
            # Navegar a Mis Causas
            navigate_to_mis_causas(driver)
            
            # Esperar un momento antes de navegar a otra sección
            time.sleep(3)
            
            # Navegar a Mi Estado Diario
            navigate_to_estado_diario(driver)
            
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