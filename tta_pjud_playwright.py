from playwright.sync_api import sync_playwright
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

# Lista de user agents
USER_AGENTS = [
    # Navegadores de escritorio
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.78 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.78 Safari/537.36",
    # Navegadores móviles
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.78 Mobile Safari/537.36"
]

def setup_browser():
    """Configura y retorna un navegador con Playwright"""
    playwright = sync_playwright().start()
    
    # Seleccionar un user agent aleatorio
    selected_user_agent = random.choice(USER_AGENTS)
    print(f"User-Agent seleccionado: {selected_user_agent}")
    
    browser = playwright.chromium.launch(
        headless=False,  # Cambiar a True para modo headless
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-gpu',
            '--disable-infobars',
            '--window-size=1366,768',
            '--start-maximized',
            '--disable-web-security',
            '--allow-running-insecure-content',
            '--disable-extensions',
            '--disable-notifications',
            '--disable-popup-blocking',
            '--lang=es-ES',
            '--timezone=America/Santiago'
        ]
    )
    
    # Crear el contexto con las configuraciones básicas
    context = browser.new_context(
        viewport={'width': 1366, 'height': 768},
        user_agent=selected_user_agent,
        locale='es-ES',
        timezone_id='America/Santiago',
        geolocation={'latitude': -33.4489, 'longitude': -70.6693},  # Santiago, Chile
        permissions=['geolocation'],
        extra_http_headers={
            'Accept-Language': 'es-ES,es;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }
    )
    
    # Configurar el contexto para evitar la detección de automatización
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        Object.defineProperty(navigator, 'languages', {
            get: () => ['es-ES', 'es']
        });
    """)
    
    # Crear la página
    page = context.new_page()
    
    # Configurar timeouts
    page.set_default_timeout(30000)  # 30 segundos
    page.set_default_navigation_timeout(30000)
    
    return playwright, browser, page

def random_sleep(min_seconds=1, max_seconds=3):
    """Espera un tiempo aleatorio entre min_seconds y max_seconds"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def human_like_typing(page, selector, text):
    """Simula la escritura humana con tiempos aleatorios entre caracteres"""
    for char in text:
        page.type(selector, char, delay=random.uniform(100, 300))

def simulate_human_behavior(page):
    """Simula varios comportamientos humanos aleatorios"""
    # Scroll aleatorio
    if random.random() < 0.3:  # 30% de probabilidad
        page.mouse.wheel(0, random.randint(100, 500))
        random_sleep(0.5, 1.5)
    
    # Movimiento del mouse aleatorio
    if random.random() < 0.2:  # 20% de probabilidad
        x = random.randint(100, 800)
        y = random.randint(100, 600)
        page.mouse.move(x, y)
        random_sleep(0.5, 1.5)

def login(page, username, password):
    """Realiza el proceso de login"""
    try:
        print("Esperando página de Clave Única...")
        random_sleep(2, 4)
        
        # Simular comportamiento humano antes de interactuar
        simulate_human_behavior(page)

        print("Ingresando usuario...")
        page.fill('#uname', username)
        
        random_sleep(1, 2)
        
        print("Ingresando contraseña...")
        page.fill('#pword', password)
        
        random_sleep(1, 2)
        
        # Simular la pulsación de Enter para enviar el formulario
        page.keyboard.press('Enter')
        page.keyboard.press('Enter')
        
        # Simular comportamiento humano después del login
        random_sleep(2, 4)
        simulate_human_behavior(page)
        
        # Verificar que el login fue exitoso
        print("Verificando inicio de sesión...")
        page.wait_for_selector('text=Oficina Judicial Virtual', timeout=30000)
        
        print("Inicio de sesión exitoso!")
        return True
        
    except Exception as e:
        print(f"Error durante el proceso de login: {str(e)}")
        try:
            page.screenshot(path="error_login.png")
            print("Captura de pantalla guardada: error_login.png")
        except Exception as ss_e:
            print(f"No se pudo guardar la captura de pantalla: {str(ss_e)}")
        return False

def navigate_to_mis_causas(page):
    """Navega a la sección Mis Causas"""
    try:
        print("Navegando a 'Mis Causas'...")
        
        # Intentar hacer clic mediante JavaScript
        try:
            page.evaluate("misCausas();")
            print("Navegación a 'Mis Causas' mediante JS exitosa!")
        except Exception as js_error:
            print(f"Error al ejecutar JavaScript: {str(js_error)}")
            
            # Intento alternativo haciendo clic directamente en el elemento
            try:
                page.click("a:has-text('Mis Causas')")
                print("Navegación a 'Mis Causas' mediante clic directo exitosa!")
            except Exception as click_error:
                print(f"Error al hacer clic directo: {str(click_error)}")
                return False
        
        # Dar tiempo para que cargue la página
        random_sleep(1, 4)
        
        return True
        
    except Exception as e:
        print(f"Error al navegar a 'Mis Causas': {str(e)}")
        try:
            page.screenshot(path="error_mis_causas.png")
            print("Captura de pantalla guardada: error_mis_causas.png")
        except Exception as ss_e:
            print(f"No se pudo guardar la captura de pantalla: {str(ss_e)}")
        return False

def navigate_mis_causas_tabs(page):
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
            try:
                # Primero intentar con el texto exacto
                page.click(f"a:has-text('{tab_name}')")
            except:
                try:
                    # Si falla, intentar con una coincidencia más flexible
                    page.click(f"a:has-text('{tab_name}', 'i')")
                except:
                    print(f"  No se pudo encontrar la pestaña '{tab_name}'. Continuando...")
                    continue
            
            print(f"  Clic exitoso en pestaña '{tab_name}'")
            
            # Registrar que hemos visitado esta pestaña
            visited_tabs.add(tab_name)
            
            # Esperar un momento para que cargue la pestaña
            random_sleep(2, 4)
            
        except Exception as e:
            print(f"  Error navegando a pestaña '{tab_name}': {str(e)}")
            try:
                page.screenshot(path=f"error_mis_causas_tab_{tab_name}.png")
                print(f"Captura de pantalla guardada: error_mis_causas_tab_{tab_name}.png")
            except Exception as ss_e:
                print(f"No se pudo guardar la captura de pantalla: {str(ss_e)}")
    
    print("--- Finalizada navegación por pestañas de Mis Causas ---\n")

def navigate_to_estado_diario(page):
    """Navega a la sección Mi Estado Diario"""
    try:
        print("Navegando a 'Mi Estado Diario'...")
        
        # Intentar hacer clic mediante JavaScript
        try:
            page.evaluate("miEstadoDiario();")
            print("Navegación a 'Mi Estado Diario' mediante JS exitosa!")
        except Exception as js_error:
            print(f"Error al ejecutar JavaScript: {str(js_error)}")
            
            # Intento alternativo haciendo clic directamente en el elemento
            try:
                page.click("a:has-text('Mi Estado Diario')")
                print("Navegación a 'Mi Estado Diario' mediante clic directo exitosa!")
            except Exception as click_error:
                print(f"Error al hacer clic directo: {str(click_error)}")
                return False
        
        # Dar tiempo para que cargue la página
        random_sleep(2, 4)
        
        return True
        
    except Exception as e:
        print(f"Error al navegar a 'Mi Estado Diario': {str(e)}")
        try:
            page.screenshot(path="error_estado_diario.png")
            print("Captura de pantalla guardada: error_estado_diario.png")
        except Exception as ss_e:
            print(f"No se pudo guardar la captura de pantalla: {str(ss_e)}")
        return False

def navigate_estado_diario_tabs(page):
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
            try:
                # Primero intentar con el texto exacto
                page.click(f"a:has-text('{tab_name}')")
            except:
                try:
                    # Si falla, intentar con una coincidencia más flexible
                    page.click(f"a:has-text('{tab_name}', 'i')")
                except:
                    print(f"  No se pudo encontrar la pestaña '{tab_name}'. Continuando...")
                    continue
            
            print(f"  Clic exitoso en pestaña '{tab_name}'")
            
            # Registrar que hemos visitado esta pestaña
            visited_tabs.add(tab_name)
            
            # Manejo especial para Civil por error de DataTable
            if tab_name == "Civil" and not civil_error_handled:
                random_sleep(3, 5)
                civil_error_handled = True
                continue
            
            # Para otras pestañas, ejecutar la función de búsqueda si está definida
            if tab_name in TAB_FUNCTIONS:
                js_function = TAB_FUNCTIONS[tab_name]
                try:
                    # Usar la función buscar directamente como se muestra en el HTML de la pagina
                    page.evaluate(f"buscar('{js_function}');")
                    print(f"  Ejecutada función de búsqueda '{js_function}'")
                except Exception as js_error:
                    print(f"  Error al ejecutar función de búsqueda: {str(js_error)}")
                    # Intento alternativo: buscar el botón específico y hacer clic
                    try:
                        page.click(f"button[onclick*='{js_function}'], button#buscar")
                        print(f"  Clic exitoso en botón de búsqueda alternativo")
                    except:
                        print(f"  No se pudo encontrar botón de búsqueda alternativo")
            
            # Esperar un momento para que cargue la pestaña
            random_sleep(2, 4)
            
        except Exception as e:
            print(f"  Error navegando a pestaña '{tab_name}': {str(e)}")
            try:
                page.screenshot(path=f"error_estado_diario_tab_{tab_name}.png")
                print(f"Captura de pantalla guardada: error_estado_diario_tab_{tab_name}.png")
            except Exception as ss_e:
                print(f"No se pudo guardar la captura de pantalla: {str(ss_e)}")
    
    print("--- Finalizada navegación por pestañas de Mi Estado Diario ---\n")

def automatizar_poder_judicial(page, username, password):
    """Función principal para automatizar PJUD"""
    try:
        print("\n=== INICIANDO AUTOMATIZACIÓN DEL PODER JUDICIAL ===\n")
        
        # Abrir la página principal
        print("Accediendo a la página principal de PJUD...")
        page.goto(BASE_URL_PJUD)
        
        # Esperar y hacer clic en "Todos los servicios"
        print("Buscando botón 'Todos los servicios'...")
        page.click("button:has-text('Todos los servicios')")
        
        # Esperar y hacer clic en "Clave Única"
        print("Buscando opción 'Clave Única'...")
        page.click("a:has-text('Clave Única')")
        
        # Llama a la función de login
        login_success = login(page, username, password)
    
        if login_success:
            print("Login completado con éxito")
            
            # Dar un tiempo para que la página principal se cargue completamente
            random_sleep(2, 4)
            
            # 1. Navegar a Mis Causas
            mis_causas_success = navigate_to_mis_causas(page)
            
            if mis_causas_success:
                # Navegar por las pestañas de Mis Causas
                navigate_mis_causas_tabs(page)        
            
            # 2. Navegar a Mi Estado Diario
            estado_diario_success = navigate_to_estado_diario(page)
            
            if estado_diario_success:
                # Navegar por las pestañas de Mi Estado Diario
                navigate_estado_diario_tabs(page)
            
            print("\n=== AUTOMATIZACIÓN DEL PODER JUDICIAL COMPLETADA ===\n")
            return True
        else:
            print("No se pudo completar el proceso de login")
            return False
            
    except Exception as e:
        print(f"Error en la automatización del Poder Judicial: {str(e)}")
        try:
            page.screenshot(path="error_automatizacion_pjud.png")
            print("Captura de pantalla guardada: error_automatizacion_pjud.png")
        except Exception as ss_e:
            print(f"No se pudo guardar la captura de pantalla: {str(ss_e)}")
        return False

def automatizar_tta(page, username, password):
    """Función principal para automatizar TTA"""
    try:
        print("\n=== INICIANDO AUTOMATIZACIÓN DE TTA ===\n")
        
        # Abrir la página principal de TTA
        print("Accediendo a la página principal de TTA...")
        page.goto(BASE_URL_TTA)
        random_sleep(3, 5)
        
        # Esperar y hacer clic en "oficina judicial virtual tta"
        print("Buscando botón 'oficina judicial virtual tta'...")
        page.click("a[href*='ojv.tta.cl']")
        random_sleep(3, 5)
        
        # Cambiar a la nueva pestaña abierta
        all_pages = page.context.pages
        new_page = all_pages[-1]  # La última página abierta
        page = new_page  # Cambiamos el contexto a la nueva página
        print(f"Navegando en la nueva pestaña: {page.url}")

        # Clickear en opcion clave unica para iniciar sesion
        print("Buscando y haciendo clic en 'Clave Única'...")
        try:
            page.click("a[href*='AccesoClaveUnica'] span.icon-clave-unica", timeout=8000)
            print("Botón 'Clave Única' encontrado y clicado mediante selector específico")
        except:
            try:
                page.click("a:has-text('Clave Única')", timeout=8000)
                print("Botón 'Clave Única' encontrado y clicado mediante texto")
            except Exception as e:
                print(f"Error al hacer clic en 'Clave Única': {str(e)}")
                return False
            
        random_sleep(2, 4)
        
        # 1. Login
        login_success = login(page, username, password)
        if login_success:
            print("Login completado con éxito")
            
            # Dar un tiempo para que la página principal se cargue 
            random_sleep(2, 4)
            
            # Aquí irá la navegación por secciones y extracción de datos
            # TODO: Implementar la navegación específica de TTA
            
            print("\n=== AUTOMATIZACIÓN DE TTA COMPLETADA ===\n")
            return True 

        else:
            print("No se pudo completar el proceso de login")
            return False  
   
    except Exception as e:
        print(f"Error en la automatización de TTA: {str(e)}")
        try:
            page.screenshot(path="error_automatizacion_tta.png")
            print("Captura de pantalla guardada: error_automatizacion_tta.png")
        except Exception as ss_e:
            print(f"No se pudo guardar la captura de pantalla: {str(ss_e)}")
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

    playwright = None
    browser = None
    try:
        print("Iniciando navegador...")
        playwright, browser, page = setup_browser()
        
        # Ejecutar la automatización de PJUD
        automatizar_poder_judicial(page, USERNAME, PASSWORD)
        
        # Ejecutar la automatización de TTA
        #automatizar_tta(page, USERNAME, PASSWORD)
        
    except Exception as e:
        print(f"Error en la ejecución principal: {str(e)}")
        try:
            page.screenshot(path="error_main.png")
            print("Captura de pantalla guardada: error_main.png")
        except Exception as ss_e:
            print(f"No se pudo guardar la captura de pantalla: {str(ss_e)}")

    finally:
        if browser:
            print("Cerrando el navegador...")
            browser.close()
        if playwright:
            playwright.stop()

if __name__ == "__main__":
    main()
