# Instalacion y Ejecucion

## Requisitos
- Python 3.10+ (recomendado 3.11+)
- pip actualizado
- Sistema Windows, Linux o macOS con soporte para Pygame

## Dependencias
Instala dependencias principales:

```bash
pip install pygame imageio
```

## Ejecutar en desarrollo
Desde la raiz del proyecto:

```bash
python main.py
```

## Ejecutable con PyInstaller
Este proyecto incluye `InkSiege.spec`.

Compilar:

```bash
pyinstaller InkSiege.spec
```

Salida esperada:
- Ejecutable en `dist/InkSiege/`
- Recursos del juego en `assets/`

## Solucion de problemas
- Si no hay audio: verifica dispositivo de sonido y archivos en `assets/music`.
- Si falla `imageio`: el juego puede funcionar sin grabacion de video, pero instala `imageio` para funcionalidad completa.
- Si hay pantalla negra o bajo FPS: baja carga del sistema y cierra apps pesadas.
