# 🖋️ InkSiege (V0.1.5)
**Desarrollado por Pato404 | BluePanda Studios**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/Library-Pygame-green.svg)
![License](https://img.shields.io/badge/License-MIT%20/%20Custom-orange.svg)

---

## 🎮 Introducción al Juego
**InkSiege** es un intenso juego de supervivencia tipo *Bullet Hell* con mecánicas *Roguelike*. En este mundo visualmente minimalista basado en arte programático, tu objetivo es resistir el asedio de hordas de enemigos que se vuelven más fuertes con cada segundo. 

A medida que recolectas maná de los enemigos caídos, podrás subir de nivel para desbloquear habilidades únicas, desde proyectiles perforantes hasta escudos de energía y duplicados de tu personaje. El juego destaca por su alta fluidez, permitiendo cientos de entidades en pantalla sin perder rendimiento.

### ✨ Características Principales
* **Progresión Dinámica:** Sistema de rarezas (Común hasta Mítico) para mejoras aleatorias en cada partida.
* **Bestiario Completo:** Enfréntate a enemigos Normales, Elites, Tanques y Jefes con patrones de ataque únicos.
* **Sistema de Repeticiones:** Gracias a la integración con `imageio`, puedes guardar tus muertes o momentos épicos en formato GIF/MP4.
* **Estética "Cartoon":** Gráficos generados mediante código que garantizan ligereza y un estilo visual limpio.

---

## 🚀 Cómo Arrancar el Proyecto

Para facilitar el inicio a cualquier jugador o desarrollador, el proyecto incluye un sistema de preparación automática.

### ⚡ Método Rápido (Recomendado)
Ejecuta el archivo **`Play_InkSiege.bat`** ubicado en la raíz del proyecto.
Este script se encargará de:
1. Crear el entorno virtual (`.venv`) si no existe.
2. Instalar las dependencias necesarias (`pygame`, `imageio`) automáticamente.
3. Iniciar el juego directamente.

### 🖥️ Método por Consola (Comando único)
Si prefieres usar la terminal, una vez configurado el entorno, puedes arrancar el juego con:
```bash
python main.py