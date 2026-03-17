# InkSiege - Documentacion Completa

Documentacion oficial del juego desarrollado por BluePanda.

## 1. Resumen del juego
InkSiege es un juego de supervivencia arcade hecho en Python + Pygame.
- Objetivo: sobrevivir oleadas de enemigos mientras mejoras al personaje.
- Estilo: cartoon, combate rapido, progresion por niveles.
- Ventana de juego: 1200x780 a 60 FPS.

## 2. Caracteristicas principales
- Movimiento WASD y disparo automatico hacia el enemigo mas cercano.
- Sistema de mejoras por nivel (pasivas y activas).
- Enemigos normales, elites y jefes con escalado dinamico.
- Modo Infernal/Pesadilla desbloqueable en partidas avanzadas.
- Guardado de partidas por sesion y registro historico de resultados.
- Soporte de idioma ES/EN.
- Grabacion de datos de partida y telemetria local.

## 3. Estructura de esta documentacion
- [INSTALACION.md](./INSTALACION.md): requisitos, instalacion y ejecucion.
- [JUGABILIDAD.md](./JUGABILIDAD.md): controles, mecanicas y habilidades.
- [SISTEMA_GUARDADO.md](./SISTEMA_GUARDADO.md): partidas, records y configuracion.
- [ARQUITECTURA.md](./ARQUITECTURA.md): resumen tecnico del codigo.

## 4. Tecnologias usadas
- Python
- Pygame
- imageio (opcional, para funciones de video)
- PyInstaller (build ejecutable via `InkSiege.spec`)

## 5. Estado del proyecto
Proyecto en desarrollo activo. La logica actual prioriza jugabilidad y rendimiento con limites por frame para entidades.

## 6. Empresa
Desarrollado por BluePanda.
