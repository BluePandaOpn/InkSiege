# Arquitectura Tecnica

## Archivo principal
- `main.py`: contiene configuracion, entidades, gameplay, UI, audio, guardado y loop principal.

## Componentes principales
- `Data`: constantes globales de juego (resolucion, combate, spawn, colores, limites).
- Entidades: `Player`, `Enemy`, `Projectile`, `ManaDrop`, `Particle`.
- `StorageManager`: persistencia de sesiones, settings y records.
- `AudioManager`: carga y reproduccion de musica/SFX con volumen por grupo.
- `Game`: estado general, menus, loop, dificultad, upgrades y render.
- `Mp4Recorder`: grabacion de video por frames (si procede).

## Rendimiento
La logica usa limites por frame para evitar sobrecarga:
- enemigos activos
- colisiones
- proyectiles
- particulas
- drops

Tambien registra telemetria local para validar rendimiento y corregir estados invalidos.

## Internacionalizacion
Textos en `assets/lang/langs.json` con claves ES/EN.

## Build
- Especificacion de empaquetado: `InkSiege.spec`
- Activos incluidos en build: carpeta `assets`
