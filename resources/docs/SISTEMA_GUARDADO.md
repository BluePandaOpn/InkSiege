# Sistema de Guardado y Datos

## Rutas principales
- `save/settings.json`: configuracion global.
- `save/records.json`: historial global de records.
- `save/current/savegame.json`: snapshot actual.
- `save/partidas/`: sesiones completas por partida.

## Estructura por sesion
Cada sesion se guarda en `save/partidas/partida_<fecha>_<id>/` con:
- `session.scens`: metadatos de sesion.
- `world/state.json`: estado del mundo.
- `skills/*.json`: estado de mejoras/habilidades.
- `data/save_snapshot.json`: snapshot cargable.
- `data/runtime.json`: estado de runtime al guardar.
- `data/record.json`: resumen final de partida.
- `data/session_stats.json`: estadisticas acumuladas.
- `data/telemetry_runtime.json`: telemetria periodica.
- `data/telemetry_final.json`: telemetria final.
- `recordings/`: capturas de grabacion (si estan activadas).

## Guardado seguro
El juego permite guardado manual desde pausa y marca partidas aptas para carga segura.

## Datos registrados
- Score
- Duracion
- Dano realizado/recibido
- Enemigos eliminados
- Precision de disparo
- Mana recolectada
- Mejoras elegidas
- Telemetria de rendimiento
