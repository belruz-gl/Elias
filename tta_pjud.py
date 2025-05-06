from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
from dotenv import load_dotenv
import time, random, os

# Variables globales
BASE_URL_PJUD = "https://oficinajudicialvirtual.pjud.cl/home/"
BASE_URL_TTA = "https://www.tta.cl/"

# Listas y diccionarios para la navegación en PJUD
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

# Funciones de utilidad
def setup_driver():
    options = uc.ChromeOptions()

    # Lista de user agents
    user_agents = [
        # Navegadores de escritorio
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.78 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.78 Safari/537.36",
        # Navegadores móviles
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.78 Mobile Safari/537.36"
    ]

    # se elige uno al azar
    selected_user_agent = random.choice(user_agents)
    options.add_argument(f'user-agent={selected_user_agent}')
    print(f"User-Agent seleccionado: {selected_user_agent}")
    
    # Configuración básica para entorno sin interfaz gráfica
    #options.add_argument('--headless=new')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Configuraciones para evitar la detección
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Configuraciones de idioma y zona horaria
    options.add_argument('--lang=es-ES')
    options.add_argument('--timezone=America/Santiago')
    
    # Configuraciones de red y rendimiento
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-popup-blocking')
    
    # Crear el driver 
    driver = uc.Chrome(options=options)
    
    # Modificar las propiedades del navegador para evitar la detección
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['es-ES', 'es']
            });
        '''
    })
    
    # Configurar timeouts
    driver.set_page_load_timeout(30)
    driver.set_script_timeout(30)
    
    return driver

def wait_for_element(driver, locator, timeout=30):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located(locator)
    )

def wait_for_clickable(driver, locator, timeout=30):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable(locator)
    )

def random_sleep(min_seconds=1, max_seconds=3):
    """Espera un tiempo aleatorio entre min_seconds y max_seconds"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def human_like_typing(element, text):
    """Simula la escritura humana con tiempos aleatorios entre caracteres"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))

def human_like_mouse_movement(driver, element):
    """Simula el movimiento del mouse de forma más natural usando ActionChains"""
    action = ActionChains(driver)
    action.move_to_element(element)
    action.perform()
    random_sleep(0.5, 1.5)

def random_scroll(driver):
    """Realiza un scroll aleatorio en la página"""
    scroll_amount = random.randint(100, 500)
    driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
    random_sleep(0.5, 1.5)

def simulate_human_behavior(driver):
    """Simula varios comportamientos humanos aleatorios"""
    # Scroll aleatorio
    if random.random() < 0.3:  # 30% de probabilidad
        random_scroll(driver)
    
    # Movimiento del mouse aleatorio usando ActionChains
    if random.random() < 0.2:  # 20% de probabilidad
        # Mover a una posición aleatoria en la página
        x = random.randint(100, 800)
        y = random.randint(100, 600)
        driver.execute_script(f"window.scrollTo({x}, {y});")
        random_sleep(0.5, 1.5)

# Funciones específicas para PJUD
def login(driver, username, password):
    try:
        print("Esperando página de Clave Única...")
        random_sleep(2, 4)
        
        # Simular comportamiento humano antes de interactuar
        simulate_human_behavior(driver)

        print("Ingresando usuario...")
        username_field = wait_for_element(driver, (By.ID, 'uname'))
        human_like_mouse_movement(driver, username_field)
        human_like_typing(username_field, username)
        
        random_sleep(1, 2)
        
        print("Ingresando contraseña...")
        password_field = wait_for_element(driver, (By.ID, 'pword'))
        human_like_mouse_movement(driver, password_field)
        human_like_typing(password_field, password)
        
        random_sleep(1, 2)
        
        # Hacer clic en el botón de ingreso
        login_button = wait_for_element(driver, (By.XPATH, '//button[contains(text(), "INGRESA")]'))
        human_like_mouse_movement(driver, login_button)
        driver.execute_script("arguments[0].click();", login_button)
        
        # Simular comportamiento humano después del login
        random_sleep(2, 4)
        simulate_human_behavior(driver)
        
        # Verificar que el login fue exitoso
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
        
        # Intentar hacer clic en el elemento mediante JS
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
        random_sleep(1, 4)
        
        return True
        
    except Exception as e:
        print(f"Error al navegar a 'Mis Causas': {str(e)}")
        return False

def navigate_to_estado_diario(driver):
    try:
        print("Navegando a 'Mi Estado Diario'...")
        
        # Intentar hacer clic en el elemento mediante JS
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
        random_sleep(2, 4)
        
        return True
        
    except Exception as e:
        print(f"Error al navegar a 'Mi Estado Diario': {str(e)}")
        return False

def navigate_mis_causas_tabs(driver):
    """Navega por todas las pestañas en la sección Mis Causas"""
    print("\n--- Navegando por pestañas de Mis Causas ---")
    
    # Llevar un registro de las pestañas ya visitadas
    visited_tabs = set()
    
    for tab_name in MIS_CAUSAS_TABS:
        try:
            print(f"  Navegando a pestaña '{tab_name}'...")
            
            # si ya se visitó la pagina se evita hacerlo de nuevo
            if tab_name in visited_tabs:
                print(f"  Pestaña '{tab_name}' ya fue visitada. Continuando...")
                continue
                
            # Intentar encontrar y hacer clic en la pestaña
            tab_elements = driver.find_elements(By.XPATH, f"//a[contains(text(), '{tab_name}')]")
            
            if not tab_elements:
                print(f"  No se encontró pestaña con ese nombre exacto. Intentando alternativas...")
                # Buscar con una coincidencia más flexible
                tab_elements = driver.find_elements(By.XPATH, f"//a[contains(., '{tab_name}')]")
            
            if not tab_elements:
                print(f"  No se pudo encontrar la pestaña '{tab_name}'. Continuando...")
                continue
                
            # Hacer clic en la pestaña
            tab_element = tab_elements[0]  # Tomar el primer elemento que coincida
            driver.execute_script("arguments[0].click();", tab_element)
            print(f"  Clic exitoso en pestaña '{tab_name}'")
            
            # Registrar que hemos visitado esta pestaña
            visited_tabs.add(tab_name)
            
            # Esperar un momento para que cargue la pestaña
            time.sleep(2)
            
        except Exception as e:
            print(f"  Error navegando a pestaña '{tab_name}': {str(e)}")
    
    print("--- Finalizada navegación por pestañas de Mis Causas ---\n")

def navigate_estado_diario_tabs(driver):
    """Navega por todas las pestañas en la sección Mi Estado Diario"""
    print("\n--- Navegando por pestañas de Mi Estado Diario ---")
    
    # Llevar un registro de las pestañas ya visitadas
    visited_tabs = set()
    
    # Variable para controlar si ya se ha manejado el error de DataTable en Civil
    civil_error_handled = False
    
    for tab_name in MI_ESTADO_DIARIO_TABS:
        try:
            print(f"  Navegando a pestaña '{tab_name}'...")
            
            # si ya se visitó la pagina se evita hacerlo de nuevo
            if tab_name in visited_tabs:
                print(f"  Pestaña '{tab_name}' ya fue visitada. Continuando...")
                continue
                
            # Intentar encontrar y hacer clic en la pestaña
            tab_elements = driver.find_elements(By.XPATH, f"//a[contains(text(), '{tab_name}')]")
            
            if not tab_elements:
                print(f"  No se encontró pestaña con ese nombre exacto. Intentando alternativas...")
                # Buscar con una coincidencia más flexible
                tab_elements = driver.find_elements(By.XPATH, f"//a[contains(., '{tab_name}')]")
            
            if not tab_elements:
                print(f"  No se pudo encontrar la pestaña '{tab_name}'. Continuando...")
                continue
                
            # Hacer clic en la pestaña
            tab_element = tab_elements[0]  # Tomar el primer elemento que coincida
            driver.execute_script("arguments[0].click();", tab_element)
            print(f"  Clic exitoso en pestaña '{tab_name}'")
            
            # Registrar que hemos visitado esta pestaña
            visited_tabs.add(tab_name)
            
            # Manejo especial para Civil por error de DataTable
            if tab_name == "Civil" and not civil_error_handled:
                time.sleep(3)
                civil_error_handled = True
                continue
            
            # Para otras pestañas, ejecutar la función de búsqueda si está definida
            if tab_name in TAB_FUNCTIONS:
                js_function = TAB_FUNCTIONS[tab_name]
                try:
                    # Usar la función buscar directamente como se muestra en el HTML de la pagina
                    driver.execute_script(f"buscar('{js_function}');")
                    print(f"  Ejecutada función de búsqueda '{js_function}'")
                except Exception as js_error:
                    print(f"  Error al ejecutar función de búsqueda: {str(js_error)}")
                    # Intento alternativo: buscar el botón específico y hacer clic
                    try:
                        buscar_btn = driver.find_element(By.XPATH, f"//button[contains(@onclick, '{js_function}') or contains(@id, 'buscar')]")
                        driver.execute_script("arguments[0].click();", buscar_btn)
                        print(f"  Clic exitoso en botón de búsqueda alternativo")
                    except:
                        print(f"  No se pudo encontrar botón de búsqueda alternativo")
            
            # Esperar un momento para que cargue la pestaña
            time.sleep(3)
            
        except Exception as e:
            print(f"  Error navegando a pestaña '{tab_name}': {str(e)}")
    
    print("--- Finalizada navegación por pestañas de Mi Estado Diario ---\n")

# Función principal para automatizar PJUD
def automatizar_poder_judicial(driver, username, password):

    try:
        print("\n=== INICIANDO AUTOMATIZACIÓN DEL PODER JUDICIAL ===\n")
        
        # Abrir la página principal
        print("Accediendo a la página principal de PJUD...")
        driver.get(BASE_URL_PJUD)
        
        # Esperar y hacer clic en "Todos los servicios"
        print("Buscando botón 'Todos los servicios'...")
        todos_servicios_btn = wait_for_clickable(driver, (By.XPATH, "//button[contains(text(), 'Todos los servicios') or contains(@class, 'todos-servicios')]"))
        todos_servicios_btn.click()
        
        # Esperar y hacer clic en "Clave Única"
        print("Buscando opción 'Clave Única'...")
        clave_unica_btn = wait_for_clickable(driver, (By.XPATH, "//a[contains(text(), 'Clave Única')]"))
        clave_unica_btn.click()
        
        # Llama a la función de login
        login_success = login(driver, username, password)
    
        if login_success:
            print("Login completado con éxito")
            
            # Dar un tiempo para que la página principal se cargue completamente
            random_sleep(2, 4)
            
            # 1. Navegar a Mis Causas
            mis_causas_success = navigate_to_mis_causas(driver)
            
            if mis_causas_success:
                # Navegar por las pestañas de Mis Causas
                navigate_mis_causas_tabs(driver)        
            
            # 2. Navegar a Mi Estado Diario
            estado_diario_success = navigate_to_estado_diario(driver)
            
            if estado_diario_success:
                # Navegar por las pestañas de Mi Estado Diario
                navigate_estado_diario_tabs(driver)
            
            print("\n=== AUTOMATIZACIÓN DEL PODER JUDICIAL COMPLETADA ===\n")
            return True
        else:
            print("No se pudo completar el proceso de login")
            return False
            
    except Exception as e:
        print(f"Error en la automatización del Poder Judicial: {str(e)}")
        return False

# Función para automatizar TTA
def automatizar_tta(driver, username, password):
   
    try:
        print("\n=== INICIANDO AUTOMATIZACIÓN DE TTA ===\n")
        
        # Abrir la página principal de TTA
        print("Accediendo a la página principal de TTA...")
        driver.get(BASE_URL_TTA)
        random_sleep(3, 5)
        
        # Esperar y hacer clic en "oficina judicial virtual tta"
        print("Buscando botón 'oficina judicial virtual tta'...")
        ojv_tta_btn = wait_for_clickable(driver, (By.XPATH, "//a[contains(@href, 'ojv.tta.cl')]"))
        ojv_tta_btn.click()                                            

        random_sleep(3, 5)
        
        # Cambiar a la nueva pestaña abierta
        all_handles = driver.window_handles
        driver.switch_to.window(all_handles[-1])
        print(f"Navegando en la nueva pestaña: {driver.current_url}")

        # Clickear en opcion clave unica para iniciar sesion
        print("Buscando y haciendo clic en 'Clave Única'...")
        
        clave_unica_btn = wait_for_clickable(
            driver, 
            (By.XPATH, "//a[contains(@href, 'AccesoClaveUnica')][.//span[contains(@class, 'icon-clave-unica')]]"),
            timeout=8
        )
        clave_unica_btn.click()
        print("Botón 'Clave Única' encontrado y clicado mediante XPath")
            
        random_sleep(2, 4)
        
        # 1. Login
        login_success = login(driver, username, password)
        if login_success:
            print("Login completado con éxito")
            
            # Dar un tiempo para que la página principal se cargue 
            random_sleep(2, 4)
            
            # 2. Navegación por secciones
            
            # 3. Extracción de datos
            
            
            print("\n=== AUTOMATIZACIÓN DE TTA COMPLETADA ===\n")
            return True 

        else:
            print("No se pudo completar el proceso de login")
            return False  
   
    except Exception as e:
        print(f"Error en la automatización de TTA: {str(e)}")
        driver.save_screenshot("error_automatizacion.png")
        print("Se guardó captura de pantalla del error")
        return False

def main():
    # Carga el archivo .env
    load_dotenv()

    # Obtiene las variables de entorno
    USERNAME = os.getenv("RUT")
    PASSWORD = os.getenv("CLAVE")
    
    # Verifica si se cargaron las variables de entorno
    if USERNAME and PASSWORD:
        print("Las claves se han cargado correctamente.")
    else:
        print("Faltan claves en el archivo .env.")
        return

    driver = None
    try:
        print("Iniciando navegador...")
        driver = setup_driver()
        
        # Poder Judicial
        automatizar_poder_judicial(driver, USERNAME, PASSWORD)
        
        # TTA
        #automatizar_tta(driver, USERNAME, PASSWORD)
        
    except Exception as e:
        print(f"Error en la ejecución principal: {str(e)}")

    finally:
        if driver:
            print("Cerrando el navegador automáticamente...")
            driver.quit()
 
if __name__ == "__main__":
    main()