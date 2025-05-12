from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import time, random, os
from datetime import datetime, timedelta
from pdf2image import convert_from_path
import re

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
        return False

def descargar_pdf_directo(pdf_url, pdf_filename, page):
    """
    Descarga un PDF desde una URL directa usando las cookies de sesión.
    """
    try:
        cookies_list = page.context.cookies()
        cookie_header = '; '.join([f"{c['name']}={c['value']}" for c in cookies_list])
        headers = {
            'Accept': 'application/pdf,application/x-pdf,application/octet-stream',
            'Accept-Language': 'es-ES,es;q=0.9',
            'Connection': 'keep-alive',
            'User-Agent': page.evaluate('navigator.userAgent'),
            'Cookie': cookie_header
        }
        response = page.context.request.get(
            pdf_url,
            headers=headers
        )
        if response.status == 200:
            with open(pdf_filename, 'wb') as f:
                f.write(response.body())
            print(f"[INFO] PDF descargado exitosamente: {pdf_filename}")
            return True
        else:
            print(f"[ERROR] Error al descargar PDF: Status code {response.status}")
            return False
    except Exception as e:
        print(f"[ERROR] Error general al descargar el PDF: {str(e)}")
        return False

def verificar_movimientos_nuevos(page, tab_name):
    try:
        print(f"[INFO] Verificando movimientos nuevos en pestaña '{tab_name}'...")
        page.wait_for_selector("table.table-titulos", timeout=10000)
        
        # reemplazar espacios con guiones bajos para el nombre de la carpeta
        pdf_dir = tab_name.replace(' ', '_')
        
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir)
        panel = page.query_selector("table.table-titulos")
        numero_causa = None
        if panel:
            panel.scroll_into_view_if_needed()
            random_sleep(1, 2)
            detalle_panel_path = f"{pdf_dir}/Detalle_causa_{numero_causa}.png" if numero_causa else f"{pdf_dir}/Detalle_causa.png"
            panel.screenshot(path=detalle_panel_path)
            print(f"[INFO] Captura del panel de información guardada: {detalle_panel_path}")
            try:
                libro_td = panel.query_selector("td:has-text('Libro')")
                if libro_td:
                    libro_text = libro_td.inner_text()
                    match = re.search(r"/\s*(\d+)", libro_text)
                    if match:
                        numero_causa = match.group(1)
                        print(f"[INFO] Número de causa extraído: {numero_causa}")
                fecha_causa = panel.query_selector("td:has-text('Fecha')").inner_text().split(":")[1].strip()
            except Exception as e:
                print(f"[WARN] No se pudo extraer toda la información del panel: {str(e)}")
        else:
            print("[WARN] No se encontró el panel de información")
        page.wait_for_selector("table.table-bordered", timeout=10000)

        # Fecha fija para pruebas
        fecha_actual_str = "01/12/2022" 

        print(f"[INFO] Verificando movimientos del día: {fecha_actual_str}")
        movimientos = page.query_selector_all("table.table-bordered tbody tr")
        print(f"[INFO] Se encontraron {len(movimientos)} movimientos")
        for movimiento in movimientos:
            try:
                folio = movimiento.query_selector("td:nth-child(1)").inner_text().strip()
                fecha_tramite_str = movimiento.query_selector("td:nth-child(5)").inner_text().strip()
                if fecha_tramite_str == fecha_actual_str:
                    print(f"[INFO] Movimiento nuevo encontrado - Folio: {folio}, Fecha: {fecha_tramite_str}")
                    pdf_form = movimiento.query_selector("form[name='frmPdf']")
                    if pdf_form:
                        # Extraer número de causa si no se ha hecho antes
                        if numero_causa is None:
                            libro_td = panel.query_selector("td:has-text('Libro')")
                            if libro_td:
                                libro_text = libro_td.inner_text()
                                match = re.search(r"/\s*(\d+)", libro_text)
                                if match:
                                    numero_causa = match.group(1)
                                    print(f"[INFO] Número de causa extraído: {numero_causa}")
                        print(f"[INFO] Captura del panel de información guardada: {detalle_panel_path}")
                        token = pdf_form.query_selector("input[name='valorFile']").get_attribute("value")
                        causa_str = f"Causa_{numero_causa}_" if numero_causa else ""
                        pdf_filename = f"{pdf_dir}/{causa_str}folio_{folio}_fecha_{fecha_tramite_str.replace('/', '_')}.pdf"
                        preview_path = pdf_filename.replace('.pdf', '_preview.png')
                        original_url = None
                        if token:
                            base_url = "https://oficinajudicialvirtual.pjud.cl/misCausas/suprema/documentos/docCausaSuprema.php?valorFile="
                            original_url = base_url + token
                        if original_url:
                            print(f"[INFO] Descargando PDF usando la URL extraída del HTML...")
                            pdf_descargado = descargar_pdf_directo(original_url, pdf_filename, page)
                            
                            # Generar una vista previa del PDF (primera página como imagen)
                            if pdf_descargado:
                                try:
                                    print(f"[INFO] Generando vista previa del PDF para {pdf_filename}...")
                                    # Convertir la primera página del PDF a imagen
                                    images = convert_from_path(pdf_filename, first_page=1, last_page=1)
                                    if images and len(images) > 0:
                                        # Guardar solo la primera página como imagen
                                        images[0].save(preview_path, 'PNG')
                                        print(f"[INFO] Vista previa guardada en: {preview_path}")
                                    else:
                                        print(f"[WARN] No se pudo generar la vista previa para {pdf_filename}")
                                except Exception as prev_error:
                                    print(f"[ERROR] Error al generar la vista previa del PDF: {str(prev_error)}")
                        
                    else:
                        print(f"[WARN] No hay PDF disponible para el movimiento {folio}")
            except Exception as e:
                print(f"[ERROR] Error procesando movimiento: {str(e)}")
                continue
        return True
    except Exception as e:
        print(f"[ERROR] Error al verificar movimientos nuevos: {str(e)}")
        return False

class ControladorLupa:
    def __init__(self, page):
        self.page = page
        self.config = self.obtener_config()
    
    def obtener_config(self):
        # Cada clase hija implementa su propia configuración
        raise NotImplementedError
    
    def manejar(self, tab_name):
        try:
            print(f"  Procesando lupa tipo '{self.__class__.__name__}' en pestaña '{tab_name}'...")
            self._hacer_clic_lupa()
            self._verificar_modal()
            self._verificar_tabla()
            self._procesar_contenido(tab_name)
            self._cambiar_pestana_modal()
            self._cerrar_modal()
            return True
        except Exception as e:
            self._manejar_error(e)
            return False

    
    def _hacer_clic_lupa(self):
        print("  Buscando enlace de lupa...")
        lupa_link = self.page.query_selector(self.config['lupa_selector'])
        
        if lupa_link:
            print("  Enlace de lupa encontrado")
            random_sleep(1, 2)
            try:
                print("  Intentando clic mediante JavaScript...")
                self.page.evaluate(f"""
                    (function() {{
                        const link = document.querySelector('{self.config['lupa_selector']}');
                        if (link) {{
                            link.click();
                            return true;
                        }}
                        return false;
                    }})();
                """)
                print("  Clic mediante JavaScript exitoso")
            except Exception as js_error:
                print(f"  Error al hacer clic con JavaScript: {str(js_error)}")
                print("  Intentando clic directo...")
                lupa_link.click()
                print("  Clic directo exitoso")
        else:
            print("  No se encontró el enlace de lupa")
            raise Exception("No se encontró el enlace de lupa")
    
    def _verificar_modal(self):
        print(f"  Esperando que el modal esté visible...")
        self.page.wait_for_selector(self.config['modal_selector'], timeout=10000)
        random_sleep(1, 2)
        
        modal_visible = self.page.evaluate(f"""
            () => {{
                const modal = document.querySelector('{self.config['modal_selector']}');
                if (!modal) return false;
                
                const style = window.getComputedStyle(modal);
                if (style.display === 'none' || style.visibility === 'hidden') return false;
                
                const title = modal.querySelector('.modal-title');
                return title && title.textContent.includes('{self.config['modal_title']}');
            }}
        """)
        
        if not modal_visible:
            print(f"  Modal no está visible o no tiene el título esperado")
            return False
            
        print(f"  Modal encontrado y verificado")
        return True
    
    def _verificar_tabla(self):
        if not self.config.get('table_selector'):
            return True
            
        try:
            self.page.wait_for_selector(self.config['table_selector'], timeout=10000)
            
            if self.config.get('expected_headers'):
                table_structure = self.page.evaluate(f"""
                    () => {{
                        const table = document.querySelector('{self.config['table_selector']}');
                        if (!table) return false;
                        
                        const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim());
                        const expectedHeaders = {self.config['expected_headers']};
                        
                        const rows = table.querySelectorAll('tbody tr');
                        return headers.length > 0 && rows.length > 0;
                    }}
                """)
                
                if not table_structure:
                    print(f"  Tabla encontrada pero no tiene la estructura esperada")
                    return False
                    
                print(f"  Tabla encontrada y verificada")
            return True
        except Exception as table_error:
            print(f"  Error esperando la tabla: {str(table_error)}")
            return False
    
    def _procesar_contenido(self, tab_name):
        if not self.config.get('process_content'):
            return True
        
        # Pasar directamente el nombre de la pestaña como parámetro
        return verificar_movimientos_nuevos(self.page, tab_name)
    
    def _cerrar_modal(self):
        try:
            self.page.evaluate(f"""
                () => {{
                    const closeBtn = document.querySelector('{self.config['modal_selector']} .modal-header button.close');
                    if (closeBtn) {{
                        closeBtn.click();
                        return true;
                    }}
                    return false;
                }}
            """)
            random_sleep(1, 2)
            return True
        except Exception as e:
            print(f"  Error al cerrar el modal: {str(e)}")
            return False
    
    def _manejar_error(self, error):
        print(f"  Error al manejar lupa: {str(error)}")


    def _cambiar_pestana_modal(self):
        try:
            print("  Cambiando a la pestaña 'Expediente Corte Apelaciones'...")
            self.page.wait_for_selector(".nav-tabs li a[href='#corteApelaciones']", timeout=5000)
            
             
            # Realizar el cambio usando JavaScript
            self.page.evaluate("""
                document.querySelector('.nav-tabs li a[href="#corteApelaciones"]').click();
            """)
            
            # Esperar a que la pestaña sea visible
            self.page.wait_for_selector("#corteApelaciones.active", timeout=5000)
            random_sleep(1, 2)
            
                
            print("  Cambio a pestaña 'Expediente Corte Apelaciones' exitoso")
            
            # Buscar y hacer clic en la lupa de Expediente Corte Apelaciones
            try:
                print("  Buscando la lupa en la pestaña Expediente Corte Apelaciones...")
                # Esperar a que el elemento de la lupa esté visible
                self.page.wait_for_selector("a[href='#modalDetalleApelaciones']", timeout=5000)
                
                # Hacer clic en la lupa usando JavaScript con el onclick
                self.page.evaluate("""
                    document.querySelector('a[href="#modalDetalleApelaciones"]').click();
                """)
                
                print("  Clic en lupa de Expediente Corte Apelaciones exitoso")
                
                # Esperar a que se abra el nuevo modal verificando el título
                print("  Esperando que aparezca el modal con título 'Detalle Causa Apelaciones'...")
                self.page.wait_for_selector("h4.modal-title:has-text('Detalle Causa Apelaciones')", timeout=10000)
                random_sleep(1, 2)
                
                print("  Modal 'Detalle Causa Apelaciones' abierto correctamente")
                
                # Crear la subcarpeta para guardar las capturas y PDFs
                pestaña_principal = "Corte_Suprema"  # Carpeta principal
                subcarpeta = f"{pestaña_principal}/Detalle_Causa_Apelaciones"
                if not os.path.exists(subcarpeta):
                    os.makedirs(subcarpeta)
                
                # Verificar movimientos en el nuevo modal
                self._verificar_movimientos_apelaciones(subcarpeta)
                
                # Cerrar AMBOS modales correctamente
                self._cerrar_ambos_modales()
                
            except Exception as e:
                print(f"  Error al procesar la lupa de Expediente Corte Apelaciones: {str(e)}")
                # Intentar cerrar los modales incluso si hay error
                self._cerrar_ambos_modales()

                
        except Exception as e:
            print(f"  Error al cambiar a la pestaña 'Expediente Corte Apelaciones': {str(e)}")
            # Intentar cerrar los modales incluso si hay error
            self._cerrar_ambos_modales()
    
    def _cerrar_ambos_modales(self):
        """Cierra correctamente ambos modales: Detalle Causa Apelaciones y Detalle Causa Suprema"""
        try:
            print("  Cerrando todos los modales abiertos...")
            
            # Método definitivo: Cierre directo de todos los modales mediante manipulación del DOM
            self.page.evaluate("""
                () => {
                    // Asegurar que no queden modales visibles
                    document.querySelectorAll('.modal.in, .modal[style*="display: block"]').forEach(modal => {
                        modal.style.display = 'none';
                        modal.classList.remove('in');
                    });
                    
                    // Asegurar que el body no tenga la clase modal-open
                    document.body.classList.remove('modal-open');
                    
                    // Eliminar todos los backdrops
                    document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
                        if (backdrop.parentNode) {
                            backdrop.parentNode.removeChild(backdrop);
                        }
                    });
                    
                    return true;
                }
            """)
            
            # Verificar el estado de los modales después de la limpieza
            any_modal_open = self.page.evaluate("""
                () => {
                    return !!document.querySelector('.modal.in, .modal[style*="display: block"]') || 
                           !!document.querySelector('.modal-backdrop') ||
                           document.body.classList.contains('modal-open');
                }
            """)
            
            if not any_modal_open:
                print("  Todos los modales cerrados correctamente")
            else:
                print("  ALERTA: Puede que algunos modales sigan abiertos")
                
        except Exception as e:
            print(f"  Error al cerrar los modales: {str(e)}")

    def _verificar_movimientos_apelaciones(self, subcarpeta):
        """Verifica los movimientos en el modal de Apelaciones y guarda los resultados"""
        try:
            print(f"  Verificando movimientos en modal de Apelaciones...")
            
            # Obtener el número de causa
            numero_causa = None
            try:
                panel_titulos = self.page.query_selector("#modalDetalleApelaciones table.table-titulos")
                if panel_titulos:
                    libro_td = panel_titulos.query_selector("td:has-text('Libro')")
                    if libro_td:
                        libro_text = libro_td.inner_text()
                        match = re.search(r"/\s*(\d+)", libro_text)
                        if match:
                            numero_causa = match.group(1)
                            print(f"  Número de causa extraído: {numero_causa}")
            except Exception as e:
                print(f"  No se pudo extraer el número de causa: {str(e)}")
            
            # Tomar captura de la sección de información de la causa
            try:
                # Identificar la sección superior del modal con la información general de la causa
                info_panel = self.page.query_selector("#modalDetalleApelaciones .modal-body > div:first-child")
                
                # Si no se encuentra con ese selector, intentar con otro selector más específico
                if not info_panel:
                    info_panel = self.page.query_selector("#modalDetalleApelaciones table.table-titulos")
                
                if info_panel:
                    # Asegurar que exista la carpeta
                    if not os.path.exists(subcarpeta):
                        os.makedirs(subcarpeta)
                    
                    # Hacer scroll para asegurar que el elemento es visible
                    info_panel.scroll_into_view_if_needed()
                    random_sleep(0.5, 1)
                    
                    # Guardar la captura de la sección de información
                    panel_screenshot_path = f"{subcarpeta}/Detalle_Causa_Apelaciones.png"
                    info_panel.screenshot(path=panel_screenshot_path)
                    print(f"  Captura de la información de la causa guardada en: {panel_screenshot_path}")
                else:
                    print("  No se pudo encontrar la sección de información para capturar")
            except Exception as capture_error:
                print(f"  Error al capturar la sección de información: {str(capture_error)}")

            # Asegurarse de que el tab "movimientosApe" esté activo
            print("  Activando la pestaña de movimientos...")
            try:
                # Verificar si ya hay alguna pestaña activa
                active_tab = self.page.query_selector("#modalDetalleApelaciones .tab-pane.active")
                if active_tab:
                    active_id = self.page.evaluate("el => el.id", active_tab)
                    print(f"  Pestaña activa actualmente: {active_id}")
                
                # Hacer clic en la pestaña de movimientos para activarla
                self.page.evaluate("""
                    () => {
                        // Buscar el enlace que apunta al tab movimientosApe
                        const tabLink = document.querySelector('#modalDetalleApelaciones .nav-tabs a[href="#movimientosApe"]');
                        if (tabLink) {
                            console.log('Enlace a pestaña encontrado, haciendo clic...');
                            tabLink.click();
                            return true;
                        } else {
                            console.log('No se encontró el enlace a la pestaña');
                            return false;
                        }
                    }
                """)
                
                # Esperar a que la pestaña esté activa
                self.page.wait_for_selector("#modalDetalleApelaciones #movimientosApe.active", timeout=5000)
                print("  Pestaña de movimientos activada correctamente")
                
                # Pequeña pausa para asegurar que todo cargue correctamente
                random_sleep(1, 2)
            except Exception as tab_error:
                print(f"  Error al activar la pestaña de movimientos: {str(tab_error)}")
                # Si hay un error, intentamos continuar de todos modos
            
            # Esperar a que la tabla de movimientos esté visible usando el nuevo selector
            print("  Esperando por la tabla de movimientos en el tab activo...")
            self.page.wait_for_selector("#movimientosApe table.table-bordered", timeout=10000)
            
            # Fecha específica para la verificación de movimientos de apelaciones: 20/01/2023
            fecha_actual_str = "20/01/2023"
            
            print(f"  Verificando movimientos del día: {fecha_actual_str}")
            
            # Obtener todos los movimientos usando el selector correcto para la pestaña activa
            movimientos = self.page.query_selector_all("#movimientosApe table.table-bordered tbody tr")
            print(f"  Se encontraron {len(movimientos)} movimientos")
            
            # Revisar cada movimiento
            for movimiento in movimientos:
                try:
                    folio = movimiento.query_selector("td:nth-child(1)").inner_text().strip()
                    fecha_tramite_str = movimiento.query_selector("td:nth-child(6)").inner_text().strip()  # Cambiamos el índice de 5 a 6 según el HTML
                    
                    # Verificar si el movimiento es de la fecha especificada
                    if fecha_tramite_str == fecha_actual_str:
                        print(f"  Movimiento nuevo encontrado - Folio: {folio}, Fecha: {fecha_tramite_str}")
                        
                        # Verificar si hay PDF disponible
                        pdf_form = movimiento.query_selector("form[name='frmDoc']")  # Cambiamos de frmPdf a frmDoc
                        if pdf_form:
                            # Obtener el token para descargar el PDF (también se cambió valorFile por valorDoc)
                            token = pdf_form.query_selector("input[name='valorDoc']").get_attribute("value")
                            causa_str = f"Causa_{numero_causa}_" if numero_causa else ""
                            pdf_filename = f"{subcarpeta}/{causa_str}folio_{folio}_fecha_{fecha_tramite_str.replace('/', '_')}.pdf"
                            preview_path = pdf_filename.replace('.pdf', '_preview.png')
                            
                            # Construir la URL para descargar el PDF
                            if token:
                                # URL para la descarga de PDF en Corte Apelaciones (modificada para usar valorDoc)
                                base_url = "https://oficinajudicialvirtual.pjud.cl/misCausas/apelaciones/documentos/docCausaApelaciones.php?valorDoc="
                                original_url = base_url + token
                                
                                # Descargar el PDF
                                print(f"  Descargando PDF de Apelaciones...")
                                pdf_descargado = descargar_pdf_directo(original_url, pdf_filename, self.page)
                                
                                # Generar una vista previa del PDF (primera página como imagen)
                                if pdf_descargado:
                                    try:
                                        print(f"  Generando vista previa del PDF para {pdf_filename}...")
                                        # Convertir la primera página del PDF a imagen
                                        images = convert_from_path(pdf_filename, first_page=1, last_page=1)
                                        if images and len(images) > 0:
                                            # Guardar solo la primera página como imagen
                                            images[0].save(preview_path, 'PNG')
                                            print(f"  Vista previa guardada en: {preview_path}")
                                        else:
                                            print(f"  No se pudo generar la vista previa para {pdf_filename}")
                                    except Exception as prev_error:
                                        print(f"  Error al generar la vista previa del PDF: {str(prev_error)}")
                        else:
                            print(f"  No hay PDF disponible para el movimiento {folio}")
                except Exception as e:
                    print(f"  Error procesando movimiento de Apelaciones: {str(e)}")
                    continue
            
            return True
            
        except Exception as e:
            print(f"  Error al verificar movimientos en modal de Apelaciones: {str(e)}")
            return False

class ControladorLupaSuprema(ControladorLupa):
    def obtener_config(self):
        return {
            'lupa_selector': "#dtaTableDetalleMisCauSup tbody tr td a[href*='modalDetalleMisCauSuprema']",
            'modal_selector': "#modalDetalleMisCauSuprema",
            'modal_title': "Detalle Causa",
            'table_selector': ".modal-content table.table-bordered",
            'expected_headers': ['Folio', 'Tipo', 'Descripción', 'Fecha', 'Documento'],
            'process_content': True
        }
        
    def _verificar_movimientos_apelaciones(self, subcarpeta):
        """Verifica los movimientos en el modal de Apelaciones y guarda los resultados"""
        try:
            print(f"  Verificando movimientos en modal de Apelaciones...")
            
            # Obtener el número de causa
            numero_causa = None
            try:
                panel_titulos = self.page.query_selector("#modalDetalleApelaciones table.table-titulos")
                if panel_titulos:
                    libro_td = panel_titulos.query_selector("td:has-text('Libro')")
                    if libro_td:
                        libro_text = libro_td.inner_text()
                        match = re.search(r"/\s*(\d+)", libro_text)
                        if match:
                            numero_causa = match.group(1)
                            print(f"  Número de causa extraído: {numero_causa}")
            except Exception as e:
                print(f"  No se pudo extraer el número de causa: {str(e)}")
            
            # Tomar captura de la sección de información de la causa
            try:
                # Identificar la sección superior del modal con la información general de la causa
                info_panel = self.page.query_selector("#modalDetalleApelaciones .modal-body > div:first-child")
                
                # Si no se encuentra con ese selector, intentar con otro selector más específico
                if not info_panel:
                    info_panel = self.page.query_selector("#modalDetalleApelaciones table.table-titulos")
                
                if info_panel:
                    # Asegurar que exista la carpeta
                    if not os.path.exists(subcarpeta):
                        os.makedirs(subcarpeta)
                    
                    # Hacer scroll para asegurar que el elemento es visible
                    info_panel.scroll_into_view_if_needed()
                    random_sleep(0.5, 1)
                    
                    # Guardar la captura de la sección de información
                    panel_screenshot_path = f"{subcarpeta}/Info_Causa_{numero_causa if numero_causa else 'sin_numero'}.png"
                    info_panel.screenshot(path=panel_screenshot_path)
                    print(f"  Captura de la información de la causa guardada en: {panel_screenshot_path}")
                else:
                    print("  No se pudo encontrar la sección de información para capturar")
            except Exception as capture_error:
                print(f"  Error al capturar la sección de información: {str(capture_error)}")

            # Asegurarse de que el tab "movimientosApe" esté activo
            print("  Activando la pestaña de movimientos...")
            try:
                # Verificar si ya hay alguna pestaña activa
                active_tab = self.page.query_selector("#modalDetalleApelaciones .tab-pane.active")
                if active_tab:
                    active_id = self.page.evaluate("el => el.id", active_tab)
                    print(f"  Pestaña activa actualmente: {active_id}")
                
                # Hacer clic en la pestaña de movimientos para activarla
                self.page.evaluate("""
                    () => {
                        // Buscar el enlace que apunta al tab movimientosApe
                        const tabLink = document.querySelector('#modalDetalleApelaciones .nav-tabs a[href="#movimientosApe"]');
                        if (tabLink) {
                            console.log('Enlace a pestaña encontrado, haciendo clic...');
                            tabLink.click();
                            return true;
                        } else {
                            console.log('No se encontró el enlace a la pestaña');
                            return false;
                        }
                    }
                """)
                
                # Esperar a que la pestaña esté activa
                self.page.wait_for_selector("#modalDetalleApelaciones #movimientosApe.active", timeout=5000)
                print("  Pestaña de movimientos activada correctamente")
                
                #  pausa para asegurar que todo cargue correctamente
                random_sleep(1, 2)
            except Exception as tab_error:
                print(f"  Error al activar la pestaña de movimientos: {str(tab_error)}")
                # Si hay un error, intentamos continuar de todos modos
            
            # Esperar a que la tabla de movimientos esté visible usando el nuevo selector
            print("  Esperando por la tabla de movimientos en el tab activo...")
            self.page.wait_for_selector("#movimientosApe table.table-bordered", timeout=10000)
            
            # Fecha prueba específica para la verificación de movimientos de apelaciones: 20/01/2023
            fecha_actual_str = "20/01/2023"
            
            print(f"  Verificando movimientos del día: {fecha_actual_str}")
            
            # Obtener todos los movimientos usando el selector correcto para la pestaña activa
            movimientos = self.page.query_selector_all("#movimientosApe table.table-bordered tbody tr")
            print(f"  Se encontraron {len(movimientos)} movimientos")
            
            # Revisar cada movimiento
            for movimiento in movimientos:
                try:
                    folio = movimiento.query_selector("td:nth-child(1)").inner_text().strip()
                    fecha_tramite_str = movimiento.query_selector("td:nth-child(6)").inner_text().strip()  # Cambiamos el índice de 5 a 6 según el HTML
                    
                    # Verificar si el movimiento es de la fecha especificada
                    if fecha_tramite_str == fecha_actual_str:
                        print(f"  Movimiento nuevo encontrado - Folio: {folio}, Fecha: {fecha_tramite_str}")
                        
                        # Verificar si hay PDF disponible
                        pdf_form = movimiento.query_selector("form[name='frmDoc']")  # Cambiamos de frmPdf a frmDoc
                        if pdf_form:
                            # Obtener el token para descargar el PDF (también se cambió valorFile por valorDoc)
                            token = pdf_form.query_selector("input[name='valorDoc']").get_attribute("value")
                            causa_str = f"Causa_{numero_causa}_" if numero_causa else ""
                            pdf_filename = f"{subcarpeta}/{causa_str}folio_{folio}_fecha_{fecha_tramite_str.replace('/', '_')}.pdf"
                            preview_path = pdf_filename.replace('.pdf', '_preview.png')
                            
                            # Construir la URL para descargar el PDF
                            if token:
                                # URL para la descarga de PDF en Corte Apelaciones (modificada para usar valorDoc)
                                base_url = "https://oficinajudicialvirtual.pjud.cl/misCausas/apelaciones/documentos/docCausaApelaciones.php?valorDoc="
                                original_url = base_url + token
                                
                                # Descargar el PDF
                                print(f"  Descargando PDF de Apelaciones...")
                                pdf_descargado = descargar_pdf_directo(original_url, pdf_filename, self.page)
                                
                                # Generar una vista previa del PDF (primera página como imagen)
                                if pdf_descargado:
                                    try:
                                        print(f"  Generando vista previa del PDF para {pdf_filename}...")
                                        # Convertir la primera página del PDF a imagen
                                        images = convert_from_path(pdf_filename, first_page=1, last_page=1)
                                        if images and len(images) > 0:
                                            # Guardar solo la primera página como imagen
                                            images[0].save(preview_path, 'PNG')
                                            print(f"  Vista previa guardada en: {preview_path}")
                                        else:
                                            print(f"  No se pudo generar la vista previa para {pdf_filename}")
                                    except Exception as prev_error:
                                        print(f"  Error al generar la vista previa del PDF: {str(prev_error)}")
                        else:
                            print(f"  No hay PDF disponible para el movimiento {folio}")
                except Exception as e:
                    print(f"  Error procesando movimiento de Apelaciones: {str(e)}")
                    continue
            
            return True
            
        except Exception as e:
            print(f"  Error al verificar movimientos en modal de Apelaciones: {str(e)}")
            return False

class ControladorLupaApelaciones(ControladorLupa):
    def obtener_config(self):
        return {
            'lupa_selector': "a[href='#modalDetalleApelaciones']",
            'modal_selector': "#modalDetalleApelaciones",
            'modal_title': "Detalle Causa",
            'table_selector': ".modal-content table.table-bordered",
            'expected_headers': ['Folio', 'Tipo', 'Descripción', 'Fecha', 'Documento'],
            'process_content': True
        }

def obtener_controlador_lupa(tipo, page):
    controladores = {
        'suprema': ControladorLupaSuprema,
        'apelaciones': ControladorLupaApelaciones
    }
    controlador_clase = controladores.get(tipo)
    if not controlador_clase:
        raise ValueError(f"Tipo de lupa '{tipo}' no reconocido")
    return controlador_clase(page)

def lupa(page, config):
    """
    Función genérica para manejar clics en lupa y sus modales asociados
    
    Args:
        page: La página de Playwright
        config: Diccionario con la configuración específica:
            - tipo: Tipo de lupa ('suprema', 'apelaciones', etc.)
            - tab_name: Nombre de la pestaña actual
    """
    controlador = obtener_controlador_lupa(config['tipo'], page)
    return controlador.manejar(config['tab_name'])

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
            
            # Pausa antes de cambiar de pestaña
            random_sleep(3, 5)
                
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
            
            # Esperar a que cargue la pestaña
            random_sleep(2, 4)
            
            # Ejecutar la función de búsqueda si está definida para esta pestaña
            if tab_name in TAB_FUNCTIONS:
                try:
                    # Manejar la lupa de Corte Suprema pasando el nombre exacto de la pestaña
                    if not lupa(page, {'tipo': 'suprema', 'tab_name': tab_name}):
                        print(f"  Error al manejar la lupa de Corte Suprema en pestaña '{tab_name}'")
                        continue

                    # Si estamos en Corte Suprema, también procesamos la segunda pestaña
                    if tab_name == "Corte Suprema":
                        # Cambiar a la pestaña "Expediente Corte Apelaciones"
                        print("  Cambiando a la pestaña 'Expediente Corte Apelaciones'...")
                        try:
                            page.wait_for_selector(".nav-tabs li a[href='#corteApelaciones']", timeout=5000)
                            page.evaluate("document.querySelector('.nav-tabs li a[href=\"#corteApelaciones\"]').click();")
                            page.wait_for_selector("#corteApelaciones", timeout=5000)
                            random_sleep(1, 2)
                            
                            # Manejar la lupa de Corte Apelaciones
                            if not lupa(page, {'tipo': 'apelaciones', 'tab_name': tab_name}):
                                print(f"  Error al manejar la lupa de apelaciones en pestaña '{tab_name}'")
                                continue
                            
                        except Exception as tab_error:
                            print(f"  Error al cambiar a la pestaña 'Expediente Corte Apelaciones': {str(tab_error)}")
                            continue
                    
                except Exception as e:
                    print(f"  Error al hacer clic en ícono de lupa: {str(e)}")
 
            
            # Pausa después de procesar cada pestaña
            random_sleep(3, 5)
            
        except Exception as e:
            print(f"  Error navegando a pestaña '{tab_name}': {str(e)}")

    
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


    finally:
        if browser:
            print("Cerrando el navegador...")
            browser.close()
        if playwright:
            playwright.stop()

if __name__ == "__main__":
    main()
