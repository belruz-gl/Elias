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

#Configura y retorna un navegador con Playwright
def setup_browser():

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

#Espera un tiempo aleatorio entre min_seconds y max_seconds
def random_sleep(min_seconds=1, max_seconds=3):
    time.sleep(random.uniform(min_seconds, max_seconds))

#Simula varios comportamientos humanos aleatorios
def simulate_human_behavior(page):
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

#Realiza el proceso de login
def login(page, username, password):
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

#Navega a la sección Mis Causas
def navigate_to_mis_causas(page):
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

#Descarga un PDF desde una URL directa usando las cookies de sesión.
def descargar_pdf_directo(pdf_url, pdf_filename, page):
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

#Lupa es lo mismo que decir causa
class ControladorLupa:
    def __init__(self, page):
        self.page = page
        self.config = self.obtener_config()
    
    def obtener_config(self):
        raise NotImplementedError

    def _obtener_lupas(self):
        print("  Buscando todas las lupas en la tabla...")
        lupas = self.page.query_selector_all(self.config['lupa_selector'])
        print(f"  Se encontraron {len(lupas)} lupas.")
        return lupas

    def manejar(self, tab_name):
        try:
            print(f"  Procesando lupa tipo '{self.__class__.__name__}' en pestaña '{tab_name}'...")
            lupas = self._obtener_lupas()
            if not lupas:
                print("  No se encontraron lupas en la pestaña.")
                return False
            for idx, lupa_link in enumerate(lupas):
                try:
                    fila = lupa_link.evaluate_handle('el => el.closest("tr")')
                    tds = fila.query_selector_all('td')
                    if len(tds) < 3:
                        continue
                    caratulado = tds[2].inner_text().strip().replace('/', '_')
                    print(f"  Procesando lupa {idx+1} de {len(lupas)} (caratulado: {caratulado})")
                    lupa_link.scroll_into_view_if_needed()
                    random_sleep(0.5, 1)
                    lupa_link.click()
                    random_sleep(1, 2)
                    self._verificar_modal()
                    self._verificar_tabla()
                    movimientos_nuevos = self._procesar_contenido(tab_name, caratulado)
                    self._cambiar_pestana_modal(caratulado, tab_name)
                    self._cerrar_modal()
                    
                    #break para procesar solo la primera lupa por ahora
                    break
                    
                except Exception as e:
                    print(f"  Error procesando la lupa {idx+1}: {str(e)}")
                    self._manejar_error(e)
                    self._cerrar_modal()
                    continue
            return True
        except Exception as e:
            self._manejar_error(e)
            return False
    
    def _manejar_error(self, e):
        """Maneja errores durante el procesamiento"""
        print(f"  Error: {str(e)}")
        # Asegurarse de cerrar los modales si hay un error
        try:
            self._cerrar_ambos_modales()
        except Exception as close_error:
            print(f"  Error adicional al intentar cerrar modales: {str(close_error)}")
    
    def _cerrar_modal(self):
        """Cierra el modal principal"""
        try:
            print("  Cerrando modal principal...")
            self._cerrar_ambos_modales()
        except Exception as e:
            print(f"  Error al cerrar modal: {str(e)}")
    
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
    
    def _procesar_contenido(self, tab_name, caratulado):
        try:
            print(f"[INFO] Verificando movimientos nuevos en pestaña '{tab_name}'...")
            self.page.wait_for_selector("table.table-titulos", timeout=10000)
            panel = self.page.query_selector("table.table-titulos")
            numero_causa = None
            if panel:
                panel.scroll_into_view_if_needed()
                random_sleep(1, 2)
                try:
                    libro_td = panel.query_selector("td:has-text('Libro')")
                    if libro_td:
                        libro_text = libro_td.inner_text()
                        match = re.search(r"/\s*(\d+)", libro_text)
                        if match:
                            numero_causa = match.group(1)
                            print(f"[INFO] Número de causa extraído: {numero_causa}")
                except Exception as e:
                    print(f"[WARN] No se pudo extraer toda la información del panel: {str(e)}")
            else:
                print("[WARN] No se encontró el panel de información")
            self.page.wait_for_selector("table.table-bordered", timeout=10000)
            movimientos = self.page.query_selector_all("table.table-bordered tbody tr")
            print(f"[INFO] Se encontraron {len(movimientos)} movimientos")
            movimientos_nuevos = False
            for movimiento in movimientos:
                try:
                    folio = movimiento.query_selector("td:nth-child(1)").inner_text().strip()
                    fecha_tramite_str = movimiento.query_selector("td:nth-child(5)").inner_text().strip()
                    if fecha_tramite_str == "01/12/2022":
                        movimientos_nuevos = True
                        carpeta_general = tab_name.replace(' ', '_')
                        carpeta_caratulado = f"{carpeta_general}/{caratulado}"
                        if not os.path.exists(carpeta_caratulado):
                            os.makedirs(carpeta_caratulado)
                        detalle_panel_path = f"{carpeta_caratulado}/Detalle_causa.png"
                        if panel:
                            panel.screenshot(path=detalle_panel_path)
                            print(f"[INFO] Captura del panel de información guardada: {detalle_panel_path}")
                        pdf_form = movimiento.query_selector("form[name='frmPdf']")
                        if pdf_form:
                            token = pdf_form.query_selector("input[name='valorFile']").get_attribute("value")
                            causa_str = f"Causa_{numero_causa}_" if numero_causa else ""
                            pdf_filename = f"{carpeta_caratulado}/{causa_str}folio_{folio}_fecha_{fecha_tramite_str.replace('/', '_')}.pdf"
                            preview_path = pdf_filename.replace('.pdf', '_preview.png')
                            if token:
                                base_url = "https://oficinajudicialvirtual.pjud.cl/misCausas/suprema/documentos/docCausaSuprema.php?valorFile="
                                original_url = base_url + token
                                pdf_descargado = descargar_pdf_directo(original_url, pdf_filename, self.page)
                                if pdf_descargado:
                                    try:
                                        images = convert_from_path(pdf_filename, first_page=1, last_page=1)
                                        if images and len(images) > 0:
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
            return movimientos_nuevos
        except Exception as e:
            print(f"[ERROR] Error al verificar movimientos nuevos: {str(e)}")
            return False

    def _cambiar_pestana_modal(self, caratulado, tab_name):
        try:
            print("  Cambiando a la pestaña 'Expediente Corte Apelaciones'...")
            self.page.wait_for_selector(".nav-tabs li a[href='#corteApelaciones']", timeout=5000)
            self.page.evaluate("document.querySelector('.nav-tabs li a[href=\"#corteApelaciones\"]').click();")
            self.page.wait_for_selector("#corteApelaciones.active", timeout=5000)
            random_sleep(1, 2)
            print("  Cambio a pestaña 'Expediente Corte Apelaciones' exitoso")
            try:
                print("  Buscando la lupa en la pestaña Expediente Corte Apelaciones...")
                self.page.wait_for_selector("a[href='#modalDetalleApelaciones']", timeout=5000)
                self.page.evaluate("document.querySelector('a[href=\"#modalDetalleApelaciones\"]').click();")
                print("  Clic en lupa de Expediente Corte Apelaciones exitoso")
                self.page.wait_for_selector("h4.modal-title:has-text('Detalle Causa Apelaciones')", timeout=10000)
                random_sleep(1, 2)
                print("  Modal 'Detalle Causa Apelaciones' abierto correctamente")
                carpeta_general = tab_name.replace(' ', '_')
                carpeta_caratulado = f"{carpeta_general}/{caratulado}"
                subcarpeta = f"{carpeta_caratulado}/Detalle_causa_apelaciones"
                
                # Crear la subcarpeta si no existe
                if not os.path.exists(subcarpeta):
                    os.makedirs(subcarpeta)
                    
                movimientos_en_apelaciones = self._verificar_movimientos_apelaciones(subcarpeta)
                self._cerrar_ambos_modales()
            except Exception as e:
                print(f"  Error al procesar la lupa de Expediente Corte Apelaciones: {str(e)}")
                self._cerrar_ambos_modales()
        except Exception as e:
            print(f"  Error al cambiar a la pestaña 'Expediente Corte Apelaciones': {str(e)}")
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
                
            # Esperar un momento para asegurar que la UI se estabilice
            random_sleep(1, 2)
                
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
            
            # Fecha específica para la verificación de movimientos de apelaciones
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

    def _procesar_contenido(self, tab_name, caratulado):
        try:
            print(f"[INFO] Verificando movimientos nuevos en pestaña '{tab_name}'...")
            self.page.wait_for_selector("table.table-titulos", timeout=10000)
            panel = self.page.query_selector("table.table-titulos")
            numero_causa = None
            if panel:
                panel.scroll_into_view_if_needed()
                random_sleep(1, 2)
                try:
                    libro_td = panel.query_selector("td:has-text('Libro')")
                    if libro_td:
                        libro_text = libro_td.inner_text()
                        match = re.search(r"/\s*(\d+)", libro_text)
                        if match:
                            numero_causa = match.group(1)
                            print(f"[INFO] Número de causa extraído: {numero_causa}")
                except Exception as e:
                    print(f"[WARN] No se pudo extraer toda la información del panel: {str(e)}")
            else:
                print("[WARN] No se encontró el panel de información")
            self.page.wait_for_selector("table.table-bordered", timeout=10000)
            movimientos = self.page.query_selector_all("table.table-bordered tbody tr")
            print(f"[INFO] Se encontraron {len(movimientos)} movimientos")
            movimientos_nuevos = False
            for movimiento in movimientos:
                try:
                    folio = movimiento.query_selector("td:nth-child(1)").inner_text().strip()
                    fecha_tramite_str = movimiento.query_selector("td:nth-child(5)").inner_text().strip()
                    if fecha_tramite_str == "01/12/2022":
                        movimientos_nuevos = True
                        carpeta_general = tab_name.replace(' ', '_')
                        carpeta_caratulado = f"{carpeta_general}/{caratulado}"
                        if not os.path.exists(carpeta_caratulado):
                            os.makedirs(carpeta_caratulado)
                        detalle_panel_path = f"{carpeta_caratulado}/Detalle_causa.png"
                        if panel:
                            panel.screenshot(path=detalle_panel_path)
                            print(f"[INFO] Captura del panel de información guardada: {detalle_panel_path}")
                        pdf_form = movimiento.query_selector("form[name='frmPdf']")
                        if pdf_form:
                            token = pdf_form.query_selector("input[name='valorFile']").get_attribute("value")
                            causa_str = f"Causa_{numero_causa}_" if numero_causa else ""
                            pdf_filename = f"{carpeta_caratulado}/{causa_str}folio_{folio}_fecha_{fecha_tramite_str.replace('/', '_')}.pdf"
                            preview_path = pdf_filename.replace('.pdf', '_preview.png')
                            if token:
                                base_url = "https://oficinajudicialvirtual.pjud.cl/misCausas/suprema/documentos/docCausaSuprema.php?valorFile="
                                original_url = base_url + token
                                pdf_descargado = descargar_pdf_directo(original_url, pdf_filename, self.page)
                                if pdf_descargado:
                                    try:
                                        images = convert_from_path(pdf_filename, first_page=1, last_page=1)
                                        if images and len(images) > 0:
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
            return movimientos_nuevos
        except Exception as e:
            print(f"[ERROR] Error al verificar movimientos nuevos: {str(e)}")
            return False

    def _cambiar_pestana_modal(self, caratulado, tab_name):
        try:
            print("  Cambiando a la pestaña 'Expediente Corte Apelaciones'...")
            self.page.wait_for_selector(".nav-tabs li a[href='#corteApelaciones']", timeout=5000)
            self.page.evaluate("document.querySelector('.nav-tabs li a[href=\"#corteApelaciones\"]').click();")
            self.page.wait_for_selector("#corteApelaciones.active", timeout=5000)
            random_sleep(1, 2)
            print("  Cambio a pestaña 'Expediente Corte Apelaciones' exitoso")
            try:
                print("  Buscando la lupa en la pestaña Expediente Corte Apelaciones...")
                self.page.wait_for_selector("a[href='#modalDetalleApelaciones']", timeout=5000)
                self.page.evaluate("document.querySelector('a[href=\"#modalDetalleApelaciones\"]').click();")
                print("  Clic en lupa de Expediente Corte Apelaciones exitoso")
                self.page.wait_for_selector("h4.modal-title:has-text('Detalle Causa Apelaciones')", timeout=10000)
                random_sleep(1, 2)
                print("  Modal 'Detalle Causa Apelaciones' abierto correctamente")
                carpeta_general = tab_name.replace(' ', '_')
                carpeta_caratulado = f"{carpeta_general}/{caratulado}"
                subcarpeta = f"{carpeta_caratulado}/Detalle_causa_apelaciones"
                
                # Crear la subcarpeta si no existe
                if not os.path.exists(subcarpeta):
                    os.makedirs(subcarpeta)
                    
                movimientos_en_apelaciones = self._verificar_movimientos_apelaciones(subcarpeta)
                self._cerrar_ambos_modales()
            except Exception as e:
                print(f"  Error al procesar la lupa de Expediente Corte Apelaciones: {str(e)}")
                self._cerrar_ambos_modales()
        except Exception as e:
            print(f"  Error al cambiar a la pestaña 'Expediente Corte Apelaciones': {str(e)}")
            self._cerrar_ambos_modales()

class ControladorLupaApelacionesPrincipal(ControladorLupa):
    def obtener_config(self):
        return {
            'lupa_selector': "#dtaTableDetalleMisCauApe a[href*='modalDetalleMisCauApelaciones']",
            'modal_selector': "#modalDetalleMisCauApelaciones",
            'modal_title': "Detalle Causa",
            'table_selector': ".modal-content table.table-bordered",
            'expected_headers': ['Folio', 'Doc.', 'Anexo', 'Trámite', 'Descripción', 'Fecha', 'Sala', 'Estado', 'Georeferencia'],
            'process_content': True
        }

    def manejar(self, tab_name):
        try:
            print(f"  Procesando lupa tipo '{self.__class__.__name__}' en pestaña '{tab_name}'...")
            lupas = self._obtener_lupas()
            if not lupas:
                print("  No se encontraron lupas en la pestaña.")
                return False
            
            for idx, lupa_link in enumerate(lupas):
                try:
                    fila = lupa_link.evaluate_handle('el => el.closest("tr")')
                    tds = fila.query_selector_all('td')
                    if len(tds) < 4:
                        continue
                    # Cambiar de columna 2 a columna 4 para el caratulado
                    caratulado = tds[3].inner_text().strip().replace('/', '_')
                    print(f"  Procesando lupa {idx+1} de {len(lupas)} (caratulado: {caratulado})")
                    
                    lupa_link.scroll_into_view_if_needed()
                    random_sleep(0.5, 1)
                    lupa_link.click()
                    random_sleep(1, 2)
                    self._verificar_modal()
                    self._verificar_tabla()
                    movimientos_nuevos = self._procesar_contenido(tab_name, caratulado)
                    self._cambiar_pestana_modal(caratulado, tab_name)
                    self._cerrar_modal()
                    
                    #break para procesar solo la primera lupa por ahora
                    break
                    
                except Exception as e:
                    print(f"  Error procesando la lupa {idx+1}: {str(e)}")
                    self._manejar_error(e)
                    self._cerrar_modal()
                    continue
            return True
        except Exception as e:
            self._manejar_error(e)
            return False

    def _procesar_contenido(self, tab_name, caratulado):
        try:
            print(f"[INFO] Procesando movimientos en Corte Apelaciones (principal)...")
            
            # Verificar si el modal está en estado usable
            modal_usable = self.page.evaluate(f"""
                () => {{
                    const modal = document.querySelector('{self.config["modal_selector"]}');
                    if (!modal) return false;
                    
                    // Verificar si hay contenido visible
                    const tables = modal.querySelectorAll('table');
                    if (!tables || tables.length === 0) return false;
                    
                    return true;
                }}
            """)
            
            if not modal_usable:
                print("[WARN] El modal parece estar en estado bloqueado o incompleto. Intentando recuperarlo...")
                
                # Intentar "reparar" el modal inyectando contenido básico si está vacío
                self.page.evaluate(f"""
                    () => {{
                        const modal = document.querySelector('{self.config["modal_selector"]}');
                        if (!modal) return false;
                        
                        // Si la estructura interna parece incompleta, intentamos reiniciarla
                        const modalBody = modal.querySelector('.modal-body');
                        if (!modalBody || !modalBody.children || modalBody.children.length === 0) {{
                            console.log('Intentando recuperar modal vacío...');
                            
                            // Asegurarse de que el modal está visible y accesible
                            modal.style.display = 'block';
                            modal.classList.add('in');
                            document.body.classList.add('modal-open');
                            
                            // Tomar una captura del estado actual para diagnóstico
                            return true;
                        }}
                    }}
                """)
                
                # Ya que el modal está en estado inestable, lo mejor es cerrar y continuar
                print("[INFO] Modal en estado inconsistente. Guardando captura y continuando...")
                
                # Guardar una captura de pantalla del estado actual
                carpeta_general = tab_name.replace(' ', '_')
                carpeta_caratulado = f"{carpeta_general}/{caratulado}"
                if not os.path.exists(carpeta_caratulado):
                    os.makedirs(carpeta_caratulado)
                    
                try:
                    # Intentar capturar el estado del modal para diagnóstico
                    modal = self.page.query_selector(self.config["modal_selector"])
                    if modal:
                        capture_path = f"{carpeta_caratulado}/modal_estado_bloqueado.png"
                        self.page.screenshot(path=capture_path)
                        print(f"[INFO] Captura del estado bloqueado guardada en: {capture_path}")
                except Exception as capture_error:
                    print(f"[WARN] No se pudo guardar captura: {str(capture_error)}")
                    
                # No seguir procesando, solo cerrar el modal
                return False
            
            # Asegurarse de que el tab-pane "movimientosApe" está activo
            print("[INFO] Verificando y activando el tab-pane de movimientos...")
            tab_activo = self.page.evaluate("""
                () => {
                    // Verificar si el tab movimientosApe ya está activo
                    const tabMovimientos = document.querySelector('#movimientosApe');
                    if (tabMovimientos && tabMovimientos.classList.contains('active')) {
                        return true;
                    }
                    
                    // Si no está activo, intentar activarlo
                    const tabLink = document.querySelector('a[href="#movimientosApe"]');
                    if (tabLink) {
                        tabLink.click();
                        return true;
                    }
                    
                    return false;
                }
            """)
            
            if not tab_activo:
                print("[WARN] No se pudo activar el tab-pane de movimientos, intentando de forma alternativa...")
                try:
                    # Intentar clic directo en el tab
                    self.page.click('a[href="#movimientosApe"]')
                    random_sleep(1, 2)
                    
                    # Verificar si se activó
                    tab_activado = self.page.evaluate('() => document.querySelector("#movimientosApe").classList.contains("active")')
                    if not tab_activado:
                        print("[WARN] No se pudo activar el tab después de múltiples intentos")
                except Exception as tab_error:
                    print(f"[ERROR] Error al intentar activar el tab: {str(tab_error)}")
            
            # Esperar brevemente para asegurar que el tab-pane esté visible
            random_sleep(1, 2)
            
            # Si llegamos aquí, el modal parece estar en buen estado
            # Continuar con el procesamiento normal
            panel = self.page.query_selector("table.table-titulos")
            numero_causa = None
            if panel:
                try:
                    panel.scroll_into_view_if_needed()
                    random_sleep(1, 2)
                    try:
                        libro_td = panel.query_selector("td:has-text('Libro')")
                        if libro_td:
                            libro_text = libro_td.inner_text()
                            # Modificar la expresión regular para extraer el número después del guion de Protección
                            match = re.search(r'Protección\s*-\s*(\d+)', libro_text)
                            if match:
                                numero_causa = match.group(1)
                                print(f"[INFO] Número de causa extraído: {numero_causa}")
                    except Exception as e:
                        print(f"[WARN] No se pudo extraer toda la información del panel: {str(e)}")
                except Exception as scroll_error:
                    print(f"[WARN] No se pudo hacer scroll al panel: {str(scroll_error)}")
                    # Crear una captura de pantalla del estado actual del modal
                    carpeta_general = tab_name.replace(' ', '_')
                    carpeta_caratulado = f"{carpeta_general}/{caratulado}"
                    if not os.path.exists(carpeta_caratulado):
                        os.makedirs(carpeta_caratulado)
                    captura_path = f"{carpeta_caratulado}/modal_error_scroll.png"
                    self.page.screenshot(path=captura_path)
                    print(f"[INFO] Captura del error de scroll guardada en: {captura_path}")
                    return False
            else:
                print("[WARN] No se encontró el panel de información")
                
            try:
                # Usar timeout más bajo para no esperar demasiado si la tabla no está disponible
                # Usar un selector más específico para la tabla correcta dentro del tab-pane activo
                self.page.wait_for_selector("#modalDetalleMisCauApelaciones #movimientosApe table.table-bordered", timeout=5000)
                movimientos = self.page.query_selector_all("#modalDetalleMisCauApelaciones #movimientosApe table.table-bordered tbody tr")
                print(f"[INFO] Se encontraron {len(movimientos)} movimientos")
            except Exception as table_error:
                print(f"[WARN] No se pudo encontrar la tabla de movimientos: {str(table_error)}")
                return False
                
            movimientos_nuevos = False
            for movimiento in movimientos:
                try:
                    folio = movimiento.query_selector("td:nth-child(1)").inner_text().strip()
                    fecha_tramite_str = movimiento.query_selector("td:nth-child(6)").inner_text().strip()  # Fecha
                    if fecha_tramite_str == "20/01/2023":
                        movimientos_nuevos = True
                        carpeta_general = tab_name.replace(' ', '_')
                        carpeta_caratulado = f"{carpeta_general}/{caratulado}"
                        if not os.path.exists(carpeta_caratulado):
                            os.makedirs(carpeta_caratulado)
                        detalle_panel_path = f"{carpeta_caratulado}/Detalle_causa.png"
                        if panel:
                            try:
                                panel.screenshot(path=detalle_panel_path)
                                print(f"[INFO] Captura del panel de información guardada: {detalle_panel_path}")
                            except Exception as panel_error:
                                print(f"[WARN] No se pudo capturar el panel: {str(panel_error)}")
                        pdf_form = movimiento.query_selector("form[name='frmDoc']")
                        if pdf_form:
                            token = pdf_form.query_selector("input[name='valorDoc']").get_attribute("value")
                            # Modificar el formato del nombre del archivo según lo solicitado
                            pdf_filename = f"{carpeta_caratulado}/Causa_{numero_causa}_folio_{folio}_fecha_{fecha_tramite_str.replace('/', '_')}.pdf"
                            preview_path = pdf_filename.replace('.pdf', '_preview.png')
                            if token:
                                base_url = "https://oficinajudicialvirtual.pjud.cl/misCausas/apelaciones/documentos/docCausaApelaciones.php?valorDoc="
                                original_url = base_url + token
                                pdf_descargado = descargar_pdf_directo(original_url, pdf_filename, self.page)
                                if pdf_descargado:
                                    try:
                                        images = convert_from_path(pdf_filename, first_page=1, last_page=1)
                                        if images and len(images) > 0:
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
            return movimientos_nuevos
        except Exception as e:
            print(f"[ERROR] Error al verificar movimientos nuevos: {str(e)}")
            return False

    def _cambiar_pestana_modal(self, caratulado, tab_name):
        # La pestaña de Apelaciones no tiene subpestañas, por lo que no hacemos nada
        pass

class ControladorLupaCivil(ControladorLupa):
    def obtener_config(self):
        return {
            'lupa_selector': "#dtaTableDetalleMisCauCiv a[href*='modalAnexoCausaCivil']",
            'modal_selector': "#modalDetalleMisCauCivil",
            'modal_title': "Detalle Causa",
            'table_selector': ".modal-content table.table-bordered",
            'expected_headers': ['Folio', 'Doc.', 'Anexo', 'Etapa', 'Trámite', 'Desc. Trámite', 'Fec. Trámite', 'Foja', 'Georeferencia'],
            'process_content': True
        }

    def manejar(self, tab_name):
        try:
            print(f"  Procesando lupa tipo '{self.__class__.__name__}' en pestaña '{tab_name}'...")
            lupas = self._obtener_lupas()
            if not lupas:
                print("  No se encontraron lupas en la pestaña.")
                return False
            
            # Mejorar el manejo de lupas para Civil
            for idx, lupa_link in enumerate(lupas):
                try:
                    fila = lupa_link.evaluate_handle('el => el.closest("tr")')
                    tds = fila.query_selector_all('td')
                    if len(tds) < 4:
                        continue
                    caratulado = tds[3].inner_text().strip().replace('/', '_')
                    print(f"  Procesando lupa {idx+1} de {len(lupas)} (caratulado: {caratulado})")
                    
                    lupa_link.scroll_into_view_if_needed()
                    random_sleep(0.5, 1)
                    
                    # Hacer clic en la lupa usando JavaScript
                    self.page.evaluate("""
                        (link) => {
                            if (link && typeof link.click === 'function') {
                                link.click();
                                return true;
                            } else {
                                return false;
                            }
                        }
                    """, lupa_link)
                    
                    random_sleep(2, 3)
                    
                    # Verificar si el modal está visible
                    try:
                        self._verificar_modal()
                        print("  Modal abierto correctamente")
                        
                        # Verificar tabla y procesar contenido
                        tabla_visible = self.page.evaluate("""
                            () => {
                                const tabla = document.querySelector("#modalDetalleMisCauCivil .modal-body table.table-bordered");
                                return !!tabla && (tabla.offsetWidth > 0 && tabla.offsetHeight > 0);
                            }
                        """)
                        
                        if tabla_visible:
                            print("  Tabla encontrada, procesando contenido...")
                            movimientos_nuevos = self._procesar_contenido(tab_name, caratulado)
                        else:
                            print("  No se encontró la tabla visible")
                    except Exception as modal_error:
                        print(f"  Error al verificar modal o tabla: {str(modal_error)}")
                        
                    # Cerrar el modal
                    self._cerrar_modal()
                    
                    # Solo procesar la primera lupa
                    break
                    
                except Exception as e:
                    print(f"  Error procesando la lupa {idx+1}: {str(e)}")
                    self._manejar_error(e)
                    continue
                    
            return True
        except Exception as e:
            self._manejar_error(e)
            return False

    def _procesar_contenido(self, tab_name, caratulado):
        try:
            print(f"[INFO] Procesando movimientos en Civil...")
            
            # Intentar usar JavaScript para acceder directamente a la información
            info_data = self.page.evaluate("""
                () => {
                    const resultado = {
                        movimientos: [],
                        numero_causa: null
                    };
                    
                    // Intentar extraer el número de causa
                    const panelInfo = document.querySelector("#modalDetalleMisCauCivil .modal-body table.table-titulos");
                    if (panelInfo) {
                        const libroCelda = Array.from(panelInfo.querySelectorAll('td')).find(td => td.textContent.includes('Libro'));
                        if (libroCelda) {
                            const libroText = libroCelda.textContent;
                            const match = libroText.match(/\\/\\s*(\\d+)/);
                            if (match) {
                                resultado.numero_causa = match[1];
                            }
                        }
                    }
                    
                    // Obtener movimientos
                    const tabla = document.querySelector("#modalDetalleMisCauCivil .modal-body table.table-bordered");
                    if (tabla) {
                        const filas = tabla.querySelectorAll('tbody tr');
                        filas.forEach(fila => {
                            const celdas = fila.querySelectorAll('td');
                            if (celdas.length >= 8) { // Asegurando que tiene suficientes columnas
                                const movimiento = {
                                    folio: celdas[0].textContent.trim(),
                                    fecha: celdas[6].textContent.trim(), // Índice 6 para Fec. Trámite
                                    tiene_pdf: !!fila.querySelector('form[name="form"]'),
                                    token: fila.querySelector('form[name="form"] input[name="dtaDoc"]')?.value || null
                                };
                                resultado.movimientos.push(movimiento);
                            }
                        });
                    }
                    
                    return resultado;
                }
            """)
            
            if info_data and 'numero_causa' in info_data:
                numero_causa = info_data['numero_causa']
                if numero_causa:
                    print(f"[INFO] Número de causa extraído: {numero_causa}")
                    
                movimientos = info_data.get('movimientos', [])
                print(f"[INFO] Se encontraron {len(movimientos)} movimientos mediante JavaScript")
                
                movimientos_nuevos = False
                carpeta_general = tab_name.replace(' ', '_')
                carpeta_caratulado = f"{carpeta_general}/{caratulado}"
                
                # Asegurar que la carpeta existe
                if not os.path.exists(carpeta_caratulado):
                    os.makedirs(carpeta_caratulado)
                
                # Capturar la información visible del modal
                try:
                    panel_principal = self.page.query_selector("#modalDetalleMisCauCivil .modal-body .panel.panel-default")
                    if panel_principal:
                        detalle_panel_path = f"{carpeta_caratulado}/Detalle_causa.png"
                        panel_principal.screenshot(path=detalle_panel_path)
                        print(f"[INFO] Captura del panel principal guardada: {detalle_panel_path}")
                    else:
                        print("[WARN] No se encontró el panel principal para capturar")
                except Exception as screenshot_error:
                    print(f"[ERROR] Error al capturar el panel principal: {str(screenshot_error)}")
                
                for movimiento in movimientos:
                    try:
                        fecha_tramite_str = movimiento.get('fecha', '')
                        folio = movimiento.get('folio', '')
                        
                        if fecha_tramite_str == "07/10/2024":
                            movimientos_nuevos = True
                            print(f"[INFO] Movimiento nuevo encontrado - Folio: {folio}, Fecha: {fecha_tramite_str}")
                            
                            if movimiento.get('tiene_pdf') and movimiento.get('token'):
                                causa_str = f"Causa_{numero_causa}_" if numero_causa else ""
                                pdf_filename = f"{carpeta_caratulado}/{causa_str}folio_{folio}_fecha_{fecha_tramite_str.replace('/', '_')}.pdf"
                                preview_path = pdf_filename.replace('.pdf', '_preview.png')
                                
                                token = movimiento.get('token')
                                base_url = "https://oficinajudicialvirtual.pjud.cl/misCausas/civil/documentos/docuS.php?dtaDoc="
                                original_url = base_url + token
                                
                                pdf_descargado = descargar_pdf_directo(original_url, pdf_filename, self.page)
                                if pdf_descargado:
                                    try:
                                        images = convert_from_path(pdf_filename, first_page=1, last_page=1)
                                        if images and len(images) > 0:
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
                        
                return movimientos_nuevos
            else:
                print("[WARN] No se pudo extraer información mediante JavaScript")
                return False
        except Exception as e:
            print(f"[ERROR] Error al verificar movimientos nuevos: {str(e)}")
            return False

    def _cambiar_pestana_modal(self, caratulado, tab_name):
        # Civil no tiene subpestañas, por lo que no hacemos nada
        pass

class ControladorLupaCobranza(ControladorLupa):
    def obtener_config(self):
        return {
            'lupa_selector': "#dtaTableDetalleMisCauCob a[href*='modalAnexoCausaCobranza']",
            'modal_selector': "#modalDetalleMisCauCobranza",
            'modal_title': "Detalle Causa",
            'table_selector': ".modal-content table.table-bordered",
            'expected_headers': ['Folio', 'Doc.', 'Anexo', 'Etapa', 'Trámite', 'Desc. Trámite', 'Estado Firma', 'Fec. Trámite', 'Georeferencia'],
            'process_content': True
        }

    def manejar(self, tab_name):
        try:
            print(f"  Procesando lupa tipo '{self.__class__.__name__}' en pestaña '{tab_name}'...")
            lupas = self._obtener_lupas()
            if not lupas:
                print("  No se encontraron lupas en la pestaña.")
                return False
            
            for idx, lupa_link in enumerate(lupas):
                try:
                    fila = lupa_link.evaluate_handle('el => el.closest("tr")')
                    tds = fila.query_selector_all('td')
                    if len(tds) < 4:
                        continue
                    # Cambiar a columna 4 (índice 3) para el caratulado
                    caratulado = tds[3].inner_text().strip().replace('/', '_')
                    print(f"  Procesando lupa {idx+1} de {len(lupas)} (caratulado: {caratulado})")
                    
                    lupa_link.scroll_into_view_if_needed()
                    random_sleep(0.5, 1)
                    lupa_link.click()
                    random_sleep(1, 2)
                    self._verificar_modal()
                    self._verificar_tabla()
                    movimientos_nuevos = self._procesar_contenido(tab_name, caratulado)
                    self._cambiar_pestana_modal(caratulado, tab_name)
                    self._cerrar_modal()
                    
                    #break para procesar solo la primera lupa por ahora
                    break
                    
                except Exception as e:
                    print(f"  Error procesando la lupa {idx+1}: {str(e)}")
                    self._manejar_error(e)
                    self._cerrar_modal()
                    continue
            return True
        except Exception as e:
            self._manejar_error(e)
            return False

    def _procesar_contenido(self, tab_name, caratulado):
        try:
            print(f"[INFO] Procesando movimientos en Cobranza...")
            
            # Intentar usar JavaScript para acceder directamente a la información
            info_data = self.page.evaluate("""
                () => {
                    const resultado = {
                        movimientos: [],
                        numero_causa: null
                    };
                    
                    // Intentar extraer el número de causa del formato D-<número>-<año>
                    const panelInfo = document.querySelector("#modalDetalleMisCauCobranza .modal-body table.table-titulos");
                    if (panelInfo) {
                        const ritCelda = Array.from(panelInfo.querySelectorAll('td')).find(td => td.textContent.includes('RIT'));
                        if (ritCelda) {
                            const ritText = ritCelda.textContent;
                            const match = ritText.match(/D-(\\d+)-/);
                            if (match) {
                                resultado.numero_causa = match[1];
                            }
                        }
                    }
                    
                    // Obtener movimientos
                    const tabla = document.querySelector("#modalDetalleMisCauCobranza .modal-body table.table-bordered");
                    if (tabla) {
                        const filas = tabla.querySelectorAll('tbody tr');
                        filas.forEach(fila => {
                            const celdas = fila.querySelectorAll('td');
                            if (celdas.length >= 8) { // Asegurando que tiene suficientes columnas
                                const movimiento = {
                                    folio: celdas[0].textContent.trim(),
                                    fecha: celdas[7].textContent.trim(), // Índice 7 para Fec. Trámite
                                    tiene_pdf: !!fila.querySelector('form[name="frmDocH"]'),
                                    token: fila.querySelector('form[name="frmDocH"] input[name="dtaDoc"]')?.value || null
                                };
                                resultado.movimientos.push(movimiento);
                            }
                        });
                    }
                    
                    return resultado;
                }
            """)
            
            if info_data and 'numero_causa' in info_data:
                numero_causa = info_data['numero_causa']
                if numero_causa:
                    print(f"[INFO] Número de causa extraído: {numero_causa}")
                    
                movimientos = info_data.get('movimientos', [])
                print(f"[INFO] Se encontraron {len(movimientos)} movimientos mediante JavaScript")
                
                movimientos_nuevos = False
                carpeta_general = tab_name.replace(' ', '_')
                carpeta_caratulado = f"{carpeta_general}/{caratulado}"
                
                # Asegurar que la carpeta existe
                if not os.path.exists(carpeta_caratulado):
                    os.makedirs(carpeta_caratulado)
                
                # Capturar la información visible del modal
                try:
                    panel_principal = self.page.query_selector("#modalDetalleMisCauCobranza .modal-body table.table-titulos")
                    if panel_principal:
                        detalle_panel_path = f"{carpeta_caratulado}/Detalle_causa.png"
                        panel_principal.screenshot(path=detalle_panel_path)
                        print(f"[INFO] Captura del panel principal guardada: {detalle_panel_path}")
                    else:
                        print("[WARN] No se encontró el panel principal para capturar")
                except Exception as screenshot_error:
                    print(f"[ERROR] Error al capturar el panel principal: {str(screenshot_error)}")
                
                for movimiento in movimientos:
                    try:
                        fecha_tramite_str = movimiento.get('fecha', '')
                        folio = movimiento.get('folio', '')
                        
                        if fecha_tramite_str == "13/12/2024":
                            movimientos_nuevos = True
                            print(f"[INFO] Movimiento nuevo encontrado - Folio: {folio}, Fecha: {fecha_tramite_str}")
                            
                            if movimiento.get('tiene_pdf') and movimiento.get('token'):
                                pdf_filename = f"{carpeta_caratulado}/Causa_{numero_causa}_folio_{folio}_fecha_{fecha_tramite_str.replace('/', '_')}.pdf"
                                preview_path = pdf_filename.replace('.pdf', '_preview.png')
                                
                                token = movimiento.get('token')
                                base_url = "https://oficinajudicialvirtual.pjud.cl/misCausas/cobranza/documentos/docuCobranza.php?dtaDoc="
                                original_url = base_url + token
                                
                                pdf_descargado = descargar_pdf_directo(original_url, pdf_filename, self.page)
                                if pdf_descargado:
                                    try:
                                        images = convert_from_path(pdf_filename, first_page=1, last_page=1)
                                        if images and len(images) > 0:
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
                        
                return movimientos_nuevos
            else:
                print("[WARN] No se pudo extraer información mediante JavaScript")
                return False
        except Exception as e:
            print(f"[ERROR] Error al verificar movimientos nuevos: {str(e)}")
            return False

    def _cambiar_pestana_modal(self, caratulado, tab_name):
        # Cobranza no tiene subpestañas, por lo que no hacemos nada
        pass

def obtener_controlador_lupa(tipo, page):
    controladores = {
        'suprema': ControladorLupaSuprema,
        'apelaciones': ControladorLupaApelacionesPrincipal,
        'apelaciones_principal': ControladorLupaApelacionesPrincipal,
        'civil': ControladorLupaCivil,
        'cobranza': ControladorLupaCobranza
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

# Mapeo de pestañas a tipo de lupa
TIPO_LUPA_MAP = {
    "Corte Suprema": "suprema",
    "Corte Apelaciones": "apelaciones_principal",
    "Civil": "civil",
    "Cobranza": "cobranza"
}

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
            
            # Tratamiento especial para la pestaña "Corte Apelaciones"
            if tab_name == "Corte Apelaciones":
                print("  Implementando estrategia especial para Corte Apelaciones...")
                
                # Refrescar la página para asegurar un estado limpio
                print("  Refrescando la página...")
                page.reload()
                random_sleep(3, 5)
                
                # Volver a navegar a Mis Causas
                print("  Navegando de nuevo a 'Mis Causas'...")
                try:
                    # Intentar hacer clic mediante JavaScript
                    page.evaluate("misCausas();")
                    print("  Navegación a 'Mis Causas' mediante JS exitosa!")
                except Exception as js_error:
                    print(f"  Error al ejecutar JavaScript: {str(js_error)}")
                    
                    # Intento alternativo haciendo clic directamente en el elemento
                    try:
                        page.click("a:has-text('Mis Causas')")
                        print("  Navegación a 'Mis Causas' mediante clic directo exitosa!")
                    except Exception as click_error:
                        print(f"  Error al hacer clic directo: {str(click_error)}")
                        continue
                
                # Esperar a que cargue la página
                random_sleep(3, 5)
            
            # Antes de cambiar de pestaña, verificamos si hay modales abiertos y los cerramos
            try:
                any_modal_open = page.evaluate("""
                    () => {
                        return !!document.querySelector('.modal.in, .modal[style*="display: block"]') || 
                               !!document.querySelector('.modal-backdrop') ||
                               document.body.classList.contains('modal-open');
                    }
                """)
                
                if any_modal_open:
                    print("  Se detectaron modales abiertos. Intentando cerrarlos antes de cambiar de pestaña...")
                    page.evaluate("""
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
                    # Esperar a que terminen de cerrarse los modales
                    random_sleep(2, 3)
            except Exception as modal_error:
                print(f"  Error al intentar cerrar modales antes del cambio de pestaña: {str(modal_error)}")
            
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
            tipo_lupa = TIPO_LUPA_MAP.get(tab_name)
            if tipo_lupa:
                if not lupa(page, {'tipo': tipo_lupa, 'tab_name': tab_name}):
                    print(f"  Error al manejar la lupa de {tab_name}")
                    
                # Esperamos un tiempo adicional después de procesar las lupas
                # para asegurarnos de que todo está cerrado correctamente
                random_sleep(3, 5)
                    
                # Verificar si quedaron modales abiertos
                try:
                    any_modal_open = page.evaluate("""
                        () => {
                            return !!document.querySelector('.modal.in, .modal[style*="display: block"]') || 
                                   !!document.querySelector('.modal-backdrop') ||
                                   document.body.classList.contains('modal-open');
                        }
                    """)
                    
                    if any_modal_open:
                        print("  ALERTA: Quedaron modales abiertos después de procesar lupas. Intentando cerrarlos...")
                        page.evaluate("""
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
                        # Esperar a que terminen de cerrarse los modales
                        random_sleep(2, 3)
                except Exception as modal_check_error:
                    print(f"  Error al verificar modales abiertos: {str(modal_check_error)}")
                
            # Pausa después de procesar cada pestaña
            random_sleep(3, 5)
            
        except Exception as e:
            print(f"  Error navegando a pestaña '{tab_name}': {str(e)}")
            # Si ocurre un error, intentamos seguir con la siguiente pestaña
            continue

    
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
           # estado_diario_success = navigate_to_estado_diario(page)
            
            #if estado_diario_success:
                # Navegar por las pestañas de Mi Estado Diario
             #   navigate_estado_diario_tabs(page)
            
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
