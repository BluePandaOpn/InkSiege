import pygame
import os

class GestorSkinsPro:
    def __init__(self):
        base = os.path.dirname(os.path.abspath(__file__))
        self.ruta = os.path.join(base, "tileset_32x32_gap10.png")

        try:
            self.sheet = pygame.image.load(self.ruta).convert_alpha()
            print("✅ Tileset cargado correctamente.")
        except Exception as e:
            self.sheet = None
            print("❌ ERROR cargando tileset:", e)
            return

        # ============================================================
        # CONFIGURACIÓN DEL TILESET
        # ============================================================
        self.TAM = 120
        self.GAP = 10

        # Coordenadas bien calculadas automáticamente
        self.coords = {
            "cyan":      (0, 0),
            "verde":     (1, 0),
            "gris":      (2, 0),

            "morado":    (0, 1),
            "rojo":      (1, 1),
            "celeste":   (2, 1),

            "amarillo":  (0, 2),
            "rosa":      (1, 2),
        }

        self.skins = {}
        self._generar_skins()

    # --------------------------------------------------------------

    def _generar_skins(self):
        for nombre, (col, fila) in self.coords.items():

            x = col * (self.TAM + self.GAP)
            y = fila * (self.TAM + self.GAP)

            rect = pygame.Rect(x, y, self.TAM, self.TAM)

            if not self.sheet.get_rect().contains(rect):
                print(f"⚠ Coordenadas fuera de rango: {nombre}")
                self.skins[nombre] = self._error()
                continue

            recorte = self.sheet.subsurface(rect)
            recorte = pygame.transform.smoothscale(recorte, (60, 60))

            self.skins[nombre] = recorte

        print("🎨 Skins generadas:", list(self.skins.keys()))

    # --------------------------------------------------------------

    def obtener(self, nombre):
        return self.skins.get(nombre, self._error())

    # --------------------------------------------------------------

    def _error(self):
        surf = pygame.Surface((60, 60))
        surf.fill((80, 200, 255))
        return surf


# ================================================================
# PROGRAMA DE PRUEBA
# ================================================================

if __name__ == "__main__":
    pygame.init()
    ventana = pygame.display.set_mode((400, 400))
    pygame.display.set_caption("verde")

    reloj = pygame.time.Clock()

    assets = GestorSkinsPro()

    lista_skins = list(assets.skins.keys())
    indice = 0
    skin = assets.obtener(lista_skins[indice])

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                exit()

            # Cambiar skin con teclas
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RIGHT:
                    indice = (indice + 1) % len(lista_skins)
                if e.key == pygame.K_LEFT:
                    indice = (indice - 1) % len(lista_skins)

                skin = assets.obtener(lista_skins[indice])
                print("➡ Skin actual:", lista_skins[indice])

        ventana.fill((240, 240, 235))

        # Líneas guía (debug visual)
        pygame.draw.line(ventana, (255, 0, 0), (200, 0), (200, 400), 1)
        pygame.draw.line(ventana, (255, 0, 0), (0, 200), (400, 200), 1)

        # Centrado perfecto
        rect = skin.get_rect(center=(200, 200))
        ventana.blit(skin, rect)

        pygame.display.flip()
        reloj.tick(60)