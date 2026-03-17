import pygame
import sys
import os
import random


def _walk_up_dirs(start_dir):
    cur = os.path.abspath(start_dir)
    while True:
        yield cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent


def _find_project_root():
    starts = [os.getcwd(), os.path.dirname(os.path.abspath(__file__))]
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        starts.append(meipass)
    for start in starts:
        for candidate in _walk_up_dirs(start):
            if os.path.isdir(os.path.join(candidate, "resources")):
                return candidate
    return os.path.dirname(os.path.abspath(__file__))


PROJECT_ROOT = _find_project_root()
RESOURCES_DIR = os.path.join(PROJECT_ROOT, "resources")


class BluePanda:
    # Developer note: keep all visual/audio assets under resources/assets.
    """
    Clase principal para la secuencia de introducción y carga de BluePanda Studios.
    Gestiona la transición entre el logo de la empresa y la pantalla de carga del juego.
    """
    
    # Constantes de configuración
    ANCHO = 1200
    ALTO = 780
    COLOR_FONDO = (255, 255, 255)
    COLOR_TEXTO = (30, 30, 35)
    COLOR_BARRA_VACIA = (235, 235, 235)
    VERSION_JUEGO = "V0.1.5" # Versión solicitada
    
    # Tiempos (milisegundos)
    DURACION_INTRO = 5000
    DURACION_CARGA = 4000
    FPS = 60

    def __init__(self, logo_path=None, preview_path=None, color_style="fire_and_ice"):
        """
        Inicializa el motor de Pygame y arranca la secuencia completa.
        """
        # Rutas por defecto: todo vive bajo resources/assets/
        if logo_path is None:
            logo_path = os.path.join(RESOURCES_DIR, "assets", "Intro", "Logo.png")
        if preview_path is None:
            preview_path = os.path.join(RESOURCES_DIR, "assets", "Intro", "GamePreview.png")

        pygame.display.init()
        pygame.font.init()
        
        # Configuración de ventana y rendimiento
        self.screen = pygame.display.set_mode((self.ANCHO, self.ALTO), pygame.DOUBLEBUF | pygame.HWSURFACE)
        pygame.display.set_caption("BluePanda Studios")
        self.clock = pygame.time.Clock()
        
        # Estilo de la barra
        self.color_config = self.Color.BluePanda(color_style)
        self.image_cache = {}

        # Inicialización de recursos
        self._inicializar_recursos(logo_path, preview_path)
        
        # Ejecución del flujo de la aplicación
        self._ejecutar_secuencia()

    class Color:
        """Subclase para gestionar los estilos de color y degradados de la barra."""
        @staticmethod
        def BluePanda(estilo):
            estilos = {
                "blue_gradient": [(0, 150, 255), (0, 80, 200)],
                "sunset": [(255, 94, 77), (255, 186, 144)],
                "emerald": [(80, 200, 120), (40, 150, 90)],
                "purple_night": [(142, 45, 226), (74, 0, 224)],
                "fire_and_ice": [(255, 45, 45), (45, 150, 255)],
                "solid_blue": (0, 150, 255)
            }
            return estilos.get(estilo, estilos["blue_gradient"])

    def _inicializar_recursos(self, logo_path, preview_path):
        """Carga y prepara imágenes, fuentes y superficies de texto."""
        self.logo = self._cargar_imagen_optimizada(logo_path, self.ANCHO * 0.5, self.ALTO * 0.5)
        self.game_preview = self._cargar_imagen_optimizada(preview_path, self.ANCHO * 0.7, self.ALTO * 0.4)
        
        self.font_titulo = pygame.font.SysFont("Verdana", 50, bold=True)
        self.font_info = pygame.font.SysFont("Verdana", 20)
        
        self.text_empresa = self.font_titulo.render("BluePanda Studios", True, self.COLOR_TEXTO).convert_alpha()

    def _cargar_imagen_optimizada(self, ruta, max_w, max_h):
        """Carga una imagen y la escala manteniendo la calidad."""
        cache_key = (os.path.abspath(ruta), int(max_w), int(max_h))
        if cache_key in self.image_cache:
            return self.image_cache[cache_key].copy()
        if not os.path.exists(ruta):
            font_err = pygame.font.SysFont("Verdana", 25)
            return font_err.render(f"Recurso no encontrado: {os.path.basename(ruta)}", True, (150, 150, 150))
        
        try:
            img = pygame.image.load(ruta).convert_alpha()
            rect = img.get_rect()
            factor = min(max_w / rect.width, max_h / rect.height)
            nueva_dim = (int(rect.width * factor), int(rect.height * factor))
            scaled = pygame.transform.smoothscale(img, nueva_dim)
            self.image_cache[cache_key] = scaled
            return scaled.copy()
        except:
            return None

    def _ejecutar_secuencia(self):
        """Controla el orden de las pantallas de la intro."""
        self._mostrar_intro_empresa()
        self._mostrar_pantalla_carga()

    def _mostrar_intro_empresa(self):
        """FASE 1: Animación secuencial del logo y nombre de la empresa."""
        start_time = pygame.time.get_ticks()
        cx, cy = self.ANCHO // 2, self.ALTO // 2
        
        logo_rect = self.logo.get_rect(center=(cx, cy - 60))
        text_rect = self.text_empresa.get_rect(center=(cx, cy + 140))
        
        ejecutando = True
        while ejecutando:
            elapsed = pygame.time.get_ticks() - start_time
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN): ejecutando = False 

            alpha_logo = self._calcular_fade(elapsed, self.DURACION_INTRO, 0.0, 0.4)
            alpha_text = self._calcular_fade(elapsed, self.DURACION_INTRO, 0.4, 0.7)

            self.screen.fill(self.COLOR_FONDO)
            self._dibujar_con_alpha(self.logo, logo_rect, alpha_logo)
            self._dibujar_con_alpha(self.text_empresa, text_rect, alpha_text)
            self._dibujar_lineas_scan()
            if elapsed >= self.DURACION_INTRO: ejecutando = False
            pygame.display.flip()
            self.clock.tick(self.FPS)

    def _mostrar_pantalla_carga(self):
        """FASE 2: Pantalla de carga con barra y versión del juego."""
        start_time = pygame.time.get_ticks()
        cx = self.ANCHO // 2
        
        # Configuración visual
        ancho_b, alto_b = 800, 15
        bx, by = cx - ancho_b // 2, 640
        preview_rect = self.game_preview.get_rect(center=(cx, 340))
        
        # Preparar texto de versión
        txt_version = self.font_info.render(self.VERSION_JUEGO, True, (100, 100, 105))
        version_rect = txt_version.get_rect(bottomright=(self.ANCHO - 20, self.ALTO - 20))

        ejecutando = True
        while ejecutando:
            elapsed = pygame.time.get_ticks() - start_time
            progreso = min(elapsed / self.DURACION_CARGA, 1.0)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()

            self.screen.fill(self.COLOR_FONDO)
            
            # 1. Preview del Juego
            if self.game_preview:
                self.screen.blit(self.game_preview, preview_rect)
            
            # 2. Texto de Progreso
            txt_progreso = self.font_info.render(f"Cargando... {int(progreso * 100)}%", True, self.COLOR_TEXTO)
            self.screen.blit(txt_progreso, (bx, by - 35))
            
            # 3. Barra de Carga
            pygame.draw.rect(self.screen, self.COLOR_BARRA_VACIA, (bx, by, ancho_b, alto_b))
            if progreso > 0:
                relleno_ancho = int(ancho_b * progreso)
                rect_relleno = pygame.Rect(bx, by, relleno_ancho, alto_b)
                if isinstance(self.color_config, list): 
                    self._dibujar_degradado(rect_relleno, self.color_config[0], self.color_config[1])
                else: 
                    pygame.draw.rect(self.screen, self.color_config, rect_relleno)
            
            # 4. Dibujar Versión (Inferior Derecha)
            self.screen.blit(txt_version, version_rect)
            self._dibujar_lineas_scan()
            if elapsed >= self.DURACION_CARGA: ejecutando = False
            pygame.display.flip()
            self.clock.tick(self.FPS)

    def _dibujar_degradado(self, rect, color_inicio, color_fin):
        """Dibuja un degradado horizontal dentro de un rectángulo."""
        surf = pygame.Surface((rect.width, rect.height))
        for x in range(rect.width):
            r = color_inicio[0] + (color_fin[0] - color_inicio[0]) * x / rect.width
            g = color_inicio[1] + (color_fin[1] - color_inicio[1]) * x / rect.width
            b = color_inicio[2] + (color_fin[2] - color_inicio[2]) * x / rect.width
            pygame.draw.line(surf, (int(r), int(g), int(b)), (x, 0), (x, rect.height))
        self.screen.blit(surf, rect)

    def _dibujar_lineas_scan(self):
        overlay = pygame.Surface((self.ANCHO, self.ALTO), pygame.SRCALPHA)
        for y in range(0, self.ALTO, 4):
            pygame.draw.line(overlay, (0, 0, 0, 32), (0, y), (self.ANCHO, y))
        self.screen.blit(overlay, (0, 0))

    def _calcular_fade(self, elapsed, total, start_perc, peak_perc):
        """Calcula el valor alpha (0-255) basado en tiempo real."""
        start_ms = total * start_perc
        peak_ms = total * peak_perc
        if elapsed < start_ms:
            return 0
        elif elapsed < peak_ms:
            return int(((elapsed - start_ms) / max(1, (peak_ms - start_ms))) * 255)
        elif elapsed < total * 0.85:
            return 255
        return int(max(0, 255 - ((elapsed - (total * 0.85)) / max(1, (total * 0.15))) * 255))

    def _dibujar_con_alpha(self, superficie, rect, alpha):

        #Dibuja con transparencia y efecto glitch aleatorio.
        if alpha <= 0 or not superficie: return
        
        glitch_x, glitch_y = 0, 0
        if random.random() < 0.06:
            glitch_x = random.randint(-8, 8)
            glitch_y = random.randint(-3, 3)
            
        temp = superficie.copy()
        temp.fill((255, 255, 255, max(0, min(255, alpha))), special_flags=pygame.BLEND_RGBA_MULT)
        
        dest_rect = rect.move(glitch_x, glitch_y)
        self.screen.blit(temp, dest_rect)


if __name__ == "__main__":
    BluePanda(color_style="fire_and_ice")
    pygame.quit()






