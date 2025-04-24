from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Variables globales
BASE_URL = "https://oficinajudicialvirtual.pjud.cl/home/"
USERNAME = REMOVED
PASSWORD = REMOVED

# Lista de pestañas para "Mis Causas" y "Mi Estado Diario"
MIS_CAUSAS_TABS = ["Corte Suprema", "Corte Apelaciones", "Civil", "Laboral", "Penal", "Cobranza", "Familia", "Disciplinario"]
MI_ESTADO_DIARIO_TABS = ["Corte Suprema", "Corte Apelaciones", "Civil", "Laboral", "Penal", "Cobranza", "Familia"]

# Diccionario de funciones JavaScript por pestaña
TAB_FUNCTIONS = {
    "Corte Suprema": "buscSup",
    "Corte Apelaciones": "buscApe",
    "Civil": "buscCiv",
    "Laboral": "buscLab",
    "Penal": "buscPen",
    "Cobranza": "buscCob",
    "Familia": "buscFam"
}

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

def navigate_to_mis_causas(driver):
    try:
        print("Navegando a 'Mis Causas'...")
        
        # Intentar hacer clic en el elemento mediante JavaScript
        try:
            driver.execute_script("misCausas();")
            print("Navegación a 'Mis Causas' mediante JS exitosa!")
        except Exception as js_error:
            print(f"Error al ejecutar JavaScript: {str(js_error)}")
            
            # Intento alternativo haciendo clic directamente en el elemento
            try:
                mis_causas_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Mis Causas')]")
                driver.execute_script("arguments[0].click();", mis_causas_link)
                print("Navegación a 'Mis Causas' mediante clic directo exitosa!")
            except Exception as click_error:
                print(f"Error al hacer clic directo: {str(click_error)}")
                return False
        
        # Dar tiempo para que cargue la página
        time.sleep(3)
        
        return True
        
    except Exception as e:
        print(f"Error al navegar a 'Mis Causas': {str(e)}")
        return False

def navigate_to_estado_diario(driver):
    try:
        print("Navegando a 'Mi Estado Diario'...")
        
        # Intentar hacer clic en el elemento mediante JavaScript
        try:
            driver.execute_script("miEstadoDiario();")
            print("Navegación a 'Mi Estado Diario' mediante JS exitosa!")
        except Exception as js_error:
            print(f"Error al ejecutar JavaScript: {str(js_error)}")
            
            # Intento alternativo haciendo clic directamente en el elemento
            try:
                estado_diario_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Mi Estado Diario')]")
                driver.execute_script("arguments[0].click();", estado_diario_link)
                print("Navegación a 'Mi Estado Diario' mediante clic directo exitosa!")
            except Exception as click_error:
                print(f"Error al hacer clic directo: {str(click_error)}")
                return False
        
        # Dar tiempo para que cargue la página
        time.sleep(3)
        
        return True
        
    except Exception as e:
        print(f"Error al navegar a 'Mi Estado Diario': {str(e)}")
        return False

def navigate_mis_causas_tabs(driver):
    """Navega por todas las pestañas en la sección Mis Causas"""
    print("\n--- Navegando por pestañas de Mis Causas ---")
    
    for tab_name in MIS_CAUSAS_TABS:
        try:
            print(f"  Navegando a pestaña '{tab_name}'...")
            
            # Intentar encontrar y hacer clic en la pestaña
            tab_xpath = f"//a[contains(text(), '{tab_name}')]"
            tab_element = None
            
            try:
                tab_element = driver.find_element(By.XPATH, tab_xpath)
            except:
                print(f"  No se encontró pestaña con ese nombre exacto. Intentando alternativas...")
            
            # Si no se encuentra, intentar con una búsqueda más flexible
            if not tab_element:
                try:
                    # Buscar por texto parcial
                    tab_element = driver.find_element(By.XPATH, f"//a[contains(., '{tab_name}')]")
                except:
                    print(f"  No se pudo encontrar la pestaña '{tab_name}'")
                    continue
            
            # Hacer clic en la pestaña
            driver.execute_script("arguments[0].click();", tab_element)
            print(f"  Clic exitoso en pestaña '{tab_name}'")
            
            # Ejecutar la función de búsqueda asociada a esta pestaña (si existe)
            if tab_name in TAB_FUNCTIONS:
                js_function = TAB_FUNCTIONS[tab_name]
                try:
                    driver.execute_script(f"buscar('{js_function}');")
                    print(f"  Ejecutada función de búsqueda '{js_function}'")
                except Exception as js_error:
                    print(f"  Error al ejecutar función de búsqueda: {str(js_error)}")
            
            # Esperar un momento para que cargue la pestaña
            time.sleep(2)
            
        except Exception as e:
            print(f"  Error navegando a pestaña '{tab_name}': {str(e)}")
    
    print("--- Finalizada navegación por pestañas de Mis Causas ---\n")

def navigate_estado_diario_tabs(driver):
    """Navega por todas las pestañas en la sección Mi Estado Diario"""
    print("\n--- Navegando por pestañas de Mi Estado Diario ---")
    
    for tab_name in MI_ESTADO_DIARIO_TABS:
        try:
            print(f"  Navegando a pestaña '{tab_name}'...")
            
            # Intentar encontrar y hacer clic en la pestaña
            tab_xpath = f"//a[contains(text(), '{tab_name}')]"
            tab_element = None
            
            try:
                tab_element = driver.find_element(By.XPATH, tab_xpath)
            except:
                print(f"  No se encontró pestaña con ese nombre exacto. Intentando alternativas...")
            
            # Si no se encuentra, intentar con una búsqueda más flexible
            if not tab_element:
                try:
                    # Buscar por texto parcial
                    tab_element = driver.find_element(By.XPATH, f"//a[contains(., '{tab_name}')]")
                except:
                    print(f"  No se pudo encontrar la pestaña '{tab_name}'")
                    continue
            
            # Hacer clic en la pestaña
            driver.execute_script("arguments[0].click();", tab_element)
            print(f"  Clic exitoso en pestaña '{tab_name}'")
            
            # Ejecutar la función de búsqueda asociada a esta pestaña (si existe)
            if tab_name in TAB_FUNCTIONS:
                js_function = TAB_FUNCTIONS[tab_name]
                try:
                    driver.execute_script(f"buscar('{js_function}');")
                    print(f"  Ejecutada función de búsqueda '{js_function}'")
                except Exception as js_error:
                    print(f"  Error al ejecutar función de búsqueda: {str(js_error)}")
            
            # Esperar un momento para que cargue la pestaña
            time.sleep(2)
            
        except Exception as e:
            print(f"  Error navegando a pestaña '{tab_name}': {str(e)}")
    
    print("--- Finalizada navegación por pestañas de Mi Estado Diario ---\n")

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
            
            # 1. Navegar a Mis Causas
            mis_causas_success = navigate_to_mis_causas(driver)
            
            if mis_causas_success:
                # Navegar por las pestañas de Mis Causas
                navigate_mis_causas_tabs(driver)
            
            # Regresar al menú principal antes de navegar a Mi Estado Diario
            # Esto dependerá de cómo esté estructurada la página
            # Puedes necesitar hacer clic en un botón de "Volver" o similar
            try:
                # Intento volver al menú principal (esto puede necesitar ajustes)
                print("Intentando volver al menú principal...")
                driver.find_element(By.XPATH, "//a[contains(text(), 'Volver') or contains(@class, 'home')]").click()
                time.sleep(2)
            except:
                print("No se pudo encontrar botón para volver. Intentando navegar directamente...")
            
            # 2. Navegar a Mi Estado Diario
            estado_diario_success = navigate_to_estado_diario(driver)
            
            if estado_diario_success:
                # Navegar por las pestañas de Mi Estado Diario
                navigate_estado_diario_tabs(driver)
            
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