# Informacion 
# V0.1.5 Version "The Polish Update"
# ==============================================
# Motor: PyGame 
# Creador: Pato404 | BluePanda Studios
# ==============================================
# Musica: Toda la musica usada en el proyecto fue sacada de la pajina https://pixabay.com
# Imagenes: El 100% del juego no usa nada de Imagenes todo lo q se usa en el juego son Imagenes para el Logo y para portada y poco mas 
# Licencia de uso No esta revisada No esta completa 
# Documentacion Incompleta
# ... 

from bluepanda import BluePanda
import pygame
import math
import random
import json
import csv
import os
import sys
from collections import deque
from datetime import datetime
try:
    import imageio.v2 as imageio
except Exception:
    imageio = None

import logging  # Añadir esta importación

# Configuración del reporte a consola
logging.basicConfig(
    level=logging.DEBUG, # Nivel DEBUG captura TODO
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("InkSiege")

# Mensaje de inicio
logger.info("--- Sistema de Reporte Activo: InkSiege V0.1.5 ---")


# =========================================================
# BLOQUE: RUTAS DE PROYECTO (fuente unica de verdad)
# =========================================================
def _walk_up_dirs(start_dir):
    """Itera desde start_dir hacia arriba hasta la raiz del disco."""
    cur = os.path.abspath(start_dir)
    while True:
        yield cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent


def find_project_root():
    """
    Busca la raiz del proyecto por presencia de carpeta 'resources'.
    Prioridad:
    1) CWD (donde se ejecuta python)
    2) Carpeta de este archivo
    3) Carpeta temporal de PyInstaller (_MEIPASS), si aplica
    """
    starts = [os.getcwd(), os.path.dirname(os.path.abspath(__file__))]
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        starts.append(meipass)
    for start in starts:
        for candidate in _walk_up_dirs(start):
            if os.path.isdir(os.path.join(candidate, "resources")):
                return candidate
    return os.path.dirname(os.path.abspath(__file__))


PROJECT_ROOT = find_project_root()
RESOURCES_DIR = os.path.join(PROJECT_ROOT, "resources")


def rpath(*parts):
    """Compone una ruta absoluta dentro de resources/."""
    return os.path.join(RESOURCES_DIR, *parts)


class ResourceCache:
    """
    Cache ligero de recursos para evitar cargas repetidas en runtime.
    - path_cache: resolucion de rutas de archivos por carpeta base
    - sound_cache: objetos pygame.Sound por ruta absoluta
    """
    def __init__(self):
        self.path_cache = {}
        self.sound_cache = {}


# =========================================================
# GUIA RAPIDA PARA DESARROLLADORES (mapa del archivo)
# - Data: constantes globales de balance y configuracion.
# - Entity/Player/Enemy/Projectile: logica de entidades.
# - StorageManager: guardado/carga y sesiones.
# - Localizer: traducciones ES/EN.
# - Game.update(): logica principal por frame.
# - Game.draw(): render principal.
# - Game.run(): bucle de eventos de Pygame.
# =========================================================

# --- LIBRERÍA DE DATOS Y ESTILO ---
BluePanda()
class Data:
    """Constantes globales del juego y ajustes de balance."""
    WIDTH = 1200
    HEIGHT = 780
    FPS = 60
    MASTER_VOLUME_DEFAULT = 1.0
    
    # Ajustes del Jugador
    PLAYER_SPEED = 5
    PLAYER_MAX_HP = 100
    PLAYER_SIZE = (48, 48)
    
    # Ajustes de Enemigos
    ENEMY_MAX_COUNT = 45        
    MAX_NORMAL_ENEMIES = 300
    MAX_ELITE_ENEMIES = 100
    MAX_BOSS_ENEMIES = 2
    ENEMY_SPAWN_TIME = 550      
    ENEMY_SPEED_MIN = 1.6
    ENEMY_SPEED_MAX = 3.0
    ENEMY_HP = 45
    ENEMY_SIZE = (42, 42)
    ENEMY_DAMAGE = 1.8
    PLAYER_HIT_COOLDOWN_MS = 300
    ENEMY_KNOCKBACK = 7.5
    ELITE_MIN_DIFF = 2.0
    ELITE_DAMAGE_MULT = 1.65
    ELITE_HP_MULT = 2.2
    ELITE_MANA_DROPS = 4
    SPECIAL_ENEMY_CHANCE = 0.09
    ENEMY_SPAWN_HP_SCALING = 0.165
    ENEMY_SPAWN_DAMAGE_SCALING = 0.145
    ENEMY_SPAWN_SPEED_SCALING = 0.07
    FAST_VARIANT_BASE_CHANCE = 0.08
    FAST_VARIANT_MAX_CHANCE = 0.38
    FAST_VARIANT_ELITE_BONUS = 0.10
    FAST_VARIANT_MIN_MULT = 1.10
    FAST_VARIANT_MAX_MULT = 1.42
    BOSS_BASE_HP = 420
    BOSS_BASE_DAMAGE = 5.0
    BOSS_MANA_DROPS = 10
    BOSS_KILL_THRESHOLD = 28
    RECORD_VIDEO_FPS = 30
    DIFF_MAX = 10.0
    INFERNAL_DIFF = 11.0
    INFERNAL_UNLOCK_TIME_MS = 1800000  # 30 minutos en x10
    INFERNAL_POWER_MULT = 1.55
    INFERNAL_SPEED_MULT = 1.28
    RESPAWN_DELAY_START_MS = 2000
    RESPAWN_DELAY_MIN_MS = 100
    POWERUP_DROP_CHANCE = 0.10
    POWERUP_LIFETIME_MS = 8000
    POWERUP_DURATION_MS = 10000
    REPLAY_DURATION_S = 5
    REPLAY_FPS = 20
    COMBO_MAX_TIME = 2500       # Tiempo para mantener el combo (ms)
    DASH_COOLDOWN_MS = 2000
    UPGRADE_RARITY_WEIGHTS = {
        "Comun": 48,
        "Poco Comun": 24,
        "Raro": 14,
        "Epico": 8,
        "Legendario": 4,
        "Mitico": 2
    }
    # Paleta propia (cartoon) para rarezas de habilidades.
    UPGRADE_RARITY_COLORS = {
        "Comun": (120, 120, 120),
        "Poco Comun": (52, 168, 138),
        "Raro": (72, 123, 227),
        "Epico": (172, 76, 193),
        "Legendario": (242, 142, 54),
        "Mitico": (236, 84, 84)
    }
    
    # Combate
    FIREBALL_SPEED = 18         
    FIREBALL_DAMAGE = 40
    DETECTION_RANGE = 400       
    SHOOT_COOLDOWN = 400        
    INK_FIRE_DAMAGE_MULT = 0.75
    INK_FIRE_BURN_DURATION_MS = 2200
    INK_FIRE_BURN_DPS_RATIO = 0.28
    INK_CRYO_DAMAGE_MULT = 0.90
    INK_CRYO_SLOW_DURATION_MS = 1800
    INK_HEAVY_DAMAGE_MULT = 1.00
    INK_HEAVY_KNOCKBACK_MULT = 1.70
    
    # Sistema de Maná/Energía
    MANA_DROP_CHANCE = 0.74     
    MANA_PER_DROP = 15          
    INITIAL_MAX_ENERGY = 10
    ENERGY_SCALING = 1.5        # Cada nivel pide 50% mas: 10 -> 15 -> 22 -> 33...
    DIFF_TIME_SCALE_MS = 120000
    DIFF_LEVEL_SCALE = 0.12
    
    # Colores Estilo Cartoon
    COLOR_BG = (240, 240, 235)      
    COLOR_GRID = (220, 220, 210)    
    COLOR_PLAYER = (80, 200, 255)   
    COLOR_ENEMY = (255, 80, 80)     
    COLOR_FIREBALL = (255, 230, 0)  
    COLOR_MANA = (0, 150, 255)      
    COLOR_OUTLINE = (30, 30, 30)    
    COLOR_TEXT = (40, 40, 40)
    COLOR_SHIELD = (150, 255, 255, 100)
    # Definimos la base en la carpeta de Documentos del usuario actual
    USER_BASE_PATH = os.path.join(os.path.expanduser("~"), "Documents", "InkSiege")
    SAVE_FILE = os.path.join(USER_BASE_PATH, "save", "current", "savegame.json")
    RECORDS_FILE = os.path.join(USER_BASE_PATH, "save", "records.json")
    SETTINGS_FILE = os.path.join(USER_BASE_PATH, "save", "settings.json")
    PARTIDAS_DIR = os.path.join(USER_BASE_PATH, "save", "partidas")
    STORAGE_VERSION = "1.0.0"
    MAX_ACTIVE_ENEMIES_PER_FRAME = 180
    MAX_ACTIVE_ENEMY_COLLISIONS_PER_FRAME = 220
    MAX_ACTIVE_PROJECTILES_PER_FRAME = 220
    MAX_ACTIVE_PARTICLES_PER_FRAME = 280
    MAX_ACTIVE_DROPS_PER_FRAME = 140

    @classmethod
    def load_config(cls):
        """Carga la configuración desde config.json si existe."""
        path = os.path.join(PROJECT_ROOT, "config.json")
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                for k, v in cfg.items():
                    if hasattr(cls, k):
                        setattr(cls, k, v)
        except Exception as e:
            logger.error(f"Error cargando config.json: {e}")

class ManaDrop:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.rect = pygame.Rect(x, y, 24, 24)
        self.bob = 0

    def update(self):
        self.bob += 0.1
        self.rect.topleft = (self.pos.x, self.pos.y + math.sin(self.bob) * 5)

    def draw(self, screen, offset):
        draw_pos = self.rect.topleft - offset
        pygame.draw.rect(screen, Data.COLOR_OUTLINE, (draw_pos[0]-2, draw_pos[1]-2, 28, 28), border_radius=6)
        pygame.draw.rect(screen, Data.COLOR_MANA, (*draw_pos, 24, 24), border_radius=5)

class Particle:
    def __init__(self, x, y, color):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(random.uniform(-5, 5), random.uniform(-5, 5))
        self.lifetime = 255
        self.max_lifetime = 255
        self.fade = 1.0
        self.color = color

    def update(self):
        self.pos += self.vel
        self.lifetime -= 10
        life_ratio = max(0.0, min(1.0, self.lifetime / max(1, self.max_lifetime)))
        self.fade = life_ratio * life_ratio

    def draw(self, screen, offset):
        if self.lifetime > 0:
            size = max(1, self.lifetime // 50)
            alpha = int(255 * max(0.0, min(1.0, self.fade)))
            px = int(self.pos.x - offset.x)
            py = int(self.pos.y - offset.y)
            color = (int(self.color[0]), int(self.color[1]), int(self.color[2]), alpha)
            diameter = size * 2 + 2
            surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (diameter // 2, diameter // 2), size)
            screen.blit(surf, (px - diameter // 2, py - diameter // 2))

class Entity:
    def __init__(self, x, y, width, height):
        self.pos = pygame.Vector2(x, y)
        self.rect = pygame.Rect(x, y, width, height)

    def update_rect(self):
        self.rect.topleft = (self.pos.x, self.pos.y)

    def draw_cartoon_rect(self, screen, color, offset, border_radius=8):
        draw_pos = self.pos - offset
        pygame.draw.rect(screen, Data.COLOR_OUTLINE, 
                         (draw_pos.x - 3, draw_pos.y - 3, self.rect.width + 6, self.rect.height + 6), 
                         border_radius=border_radius)
        pygame.draw.rect(screen, color, 
                         (*draw_pos, self.rect.width, self.rect.height), 
                         border_radius=border_radius)

class PowerUp(Entity):
    def __init__(self, pos, type):
        self.type = type  # "FIRE", "ICE", "SHIELD"
        self.colors = {
            "FIRE": (255, 100, 0),
            "ICE": (0, 200, 255),
            "SHIELD": (200, 200, 200)
        }
        self.icons = {
            "FIRE": "F",
            "ICE": "I",
            "SHIELD": "S"
        }
        super().__init__(pos.x, pos.y, 32, 32)
        self.color = self.colors[self.type]
        self.icon = self.icons[self.type]
        self.lifetime = Data.POWERUP_LIFETIME_MS
        self.bob = random.random() * math.pi * 2

    def update(self, dt):
        self.lifetime -= dt
        self.bob += 0.05

    def draw(self, screen, offset, font):
        draw_pos = self.pos - offset
        y_offset = math.sin(self.bob) * 6
        
        pygame.draw.circle(screen, Data.COLOR_OUTLINE, (draw_pos.x, draw_pos.y + y_offset), 18)
        pygame.draw.circle(screen, self.color, (draw_pos.x, draw_pos.y + y_offset), 15)
        
        icon_text = font.render(self.icon, True, Data.COLOR_OUTLINE)
        screen.blit(icon_text, icon_text.get_rect(center=(draw_pos.x, draw_pos.y + y_offset)))

class Projectile(Entity):
    def __init__(self, x, y, target_pos, damage, color=Data.COLOR_FIREBALL, size=16, speed=Data.FIREBALL_SPEED, pierce_left=1, bounces_left=0, boomerang=False, ink_type="heavy", ink_effects=None):
        super().__init__(x, y, size, size)
        self.damage = damage
        self.color = color
        self.pierce_left = pierce_left
        self.bounces_left = bounces_left
        self.boomerang = boomerang
        self.ink_type = ink_type
        self.ink_effects = ink_effects or {}
        self.returning = False
        self.travel = 0
        self.max_travel = 520
        self.hit_memory = {}
        direction = (pygame.Vector2(target_pos) - self.pos)
        if direction.length() > 0:
            self.vel = direction.normalize() * speed
        else:
            self.vel = pygame.Vector2(speed, 0)

    def update(self, dt, player_pos=None):
        if self.boomerang and player_pos is not None:
            if not self.returning:
                self.travel += self.vel.length()
                if self.travel >= self.max_travel:
                    self.returning = True
            if self.returning:
                d = pygame.Vector2(player_pos) - self.pos
                if d.length() > 0:
                    self.vel = d.normalize() * max(12, self.vel.length())
        self.pos += self.vel
        # Envejecimiento de memoria de impactos para bumeran
        for eid in list(self.hit_memory.keys()):
            self.hit_memory[eid] -= dt
            if self.hit_memory[eid] <= 0:
                del self.hit_memory[eid]
        self.update_rect()

    def draw(self, screen, offset):
        draw_pos = self.pos - offset
        pygame.draw.circle(screen, Data.COLOR_OUTLINE, draw_pos, 10)
        pygame.draw.circle(screen, self.color, draw_pos, 7)

class Enemy(Entity):
    def __init__(self, x, y, enemy_type="normal", evolution_tier=0, special_ability=None, spawn_power=1.0, speed_multiplier=1.0, rapid_variant=False, boss_kind="minor"):
        size = Data.ENEMY_SIZE
        if enemy_type == "elite":
            size = (50, 50)
        elif enemy_type == "boss":
            size = (76 + evolution_tier * 4, 76 + evolution_tier * 4)
        super().__init__(x, y, size[0], size[1])
        self.enemy_type = enemy_type
        self.evolution_tier = 0
        self.special_ability = special_ability
        self.wiggle = random.random() * 10
        self.slow_timer = 0
        self.burn_timer = 0
        self.burn_dps = 0.0
        self.ability_timer = 0
        self.regen_timer = 0
        self.boss_charge_cd = 0
        self.boss_strafe_dir = random.choice([-1, 1])
        self.boss_mode_timer = 0
        self.rapid_variant = bool(rapid_variant)
        self.boss_kind = boss_kind if enemy_type == "boss" else "none"

        if enemy_type == "elite":
            self.hp = Data.ENEMY_HP * Data.ELITE_HP_MULT
            self.speed = random.uniform(Data.ENEMY_SPEED_MIN * 1.05, Data.ENEMY_SPEED_MAX * 1.15)
            self.damage = Data.ENEMY_DAMAGE * Data.ELITE_DAMAGE_MULT
            self.mana_drop_count = Data.ELITE_MANA_DROPS
            self.color = (255, 135, 70)
            self.score_value = 28
        elif enemy_type == "boss":
            self.hp = Data.BOSS_BASE_HP
            self.speed = random.uniform(1.1, 1.8)
            self.damage = Data.BOSS_BASE_DAMAGE
            self.mana_drop_count = Data.BOSS_MANA_DROPS
            self.color = (160, 55, 255)
            self.score_value = 170
        else:
            self.hp = Data.ENEMY_HP
            self.speed = random.uniform(Data.ENEMY_SPEED_MIN, Data.ENEMY_SPEED_MAX)
            self.damage = Data.ENEMY_DAMAGE
            self.mana_drop_count = 1
            self.color = Data.COLOR_ENEMY
            self.score_value = 10

        self.apply_evolution(max(0, int(evolution_tier)))
        self.apply_spawn_scaling(spawn_power, speed_multiplier)

    def on_death(self, game):
        """Metodo base para comportamiento al morir."""
        pass

    def apply_spawn_scaling(self, spawn_power, speed_multiplier):
        self.hp *= max(1.0, float(spawn_power))
        self.damage *= max(1.0, float(spawn_power) * 0.92)
        self.speed *= max(1.0, float(speed_multiplier))
        self.score_value = max(1, int(self.score_value * (0.95 + (max(1.0, float(spawn_power)) - 1.0) * 0.75)))
        if self.rapid_variant:
            if self.enemy_type == "normal":
                self.color = (255, 115, 115)
            elif self.enemy_type == "elite":
                self.color = (255, 175, 95)

    def apply_evolution(self, target_tier):
        while self.evolution_tier < target_tier:
            self.evolution_tier += 1
            if self.enemy_type == "boss":
                self.hp *= 1.25
                self.damage *= 1.18
                self.speed *= 1.03
                self.score_value = int(self.score_value * 1.14)
                self.mana_drop_count += 1
            elif self.enemy_type == "elite":
                self.hp *= 1.20
                self.damage *= 1.15
                self.speed *= 1.04
                self.score_value = int(self.score_value * 1.10)
            else:
                self.hp *= 1.15
                self.damage *= 1.12
                self.speed *= 1.03
                self.score_value = int(self.score_value * 1.08)
            if self.special_ability is None and random.random() < 0.08:
                self.special_ability = random.choice(["orbital", "dash", "regen"])

    def apply_burn(self, dps, duration_ms):
        self.burn_dps = max(self.burn_dps, float(dps))
        self.burn_timer = max(self.burn_timer, float(duration_ms))

    def update(self, target_pos, speed_factor=1.0, frozen=False, dt=0):
        self.wiggle += 0.1
        if self.slow_timer > 0:
            self.slow_timer -= dt
        if self.burn_timer > 0:
            self.burn_timer -= dt
            self.hp -= self.burn_dps * (dt / 1000.0)
            if self.burn_timer <= 0:
                self.burn_dps = 0.0
        self.ability_timer += dt
        self.regen_timer += dt
        self.boss_mode_timer += dt
        self.boss_charge_cd = max(0, self.boss_charge_cd - dt)
        if self.special_ability == "regen" and self.regen_timer >= 1400:
            self.regen_timer = 0
            self.hp += 1.4 + 0.25 * self.evolution_tier
        if frozen:
            self.update_rect()
            return
        direction = (target_pos - self.pos)
        dist = direction.length()
        if dist > 0:
            forward = direction.normalize()
            current_speed = self.speed * (0.5 if self.slow_timer > 0 else 1.0)
            if self.enemy_type == "boss":
                lateral = pygame.Vector2(-forward.y, forward.x) * self.boss_strafe_dir
                if self.boss_mode_timer >= 2400:
                    self.boss_mode_timer = 0
                    self.boss_strafe_dir *= -1

                if self.boss_charge_cd <= 0 and dist < 420:
                    # Carga periodica hacia el jugador.
                    self.pos += forward * current_speed * speed_factor * 3.0
                    self.boss_charge_cd = max(900, 2300 - self.evolution_tier * 90)
                else:
                    move = forward
                    if dist > 280:
                        move = forward * 1.25
                    elif dist > 130:
                        move = forward * 0.55 + lateral * 0.95
                    else:
                        move = (-forward * 0.45) + lateral * 1.05
                    if move.length() > 0:
                        self.pos += move.normalize() * current_speed * speed_factor * 1.35
            else:
                move_mult = 1.0
                if self.special_ability == "dash" and self.ability_timer >= 2200:
                    self.ability_timer = 0
                    move_mult = 2.0
                self.pos += forward * current_speed * speed_factor * move_mult
        self.update_rect()

    def draw(self, screen, offset):
        self.draw_cartoon_rect(screen, self.color, offset)
        dp = self.pos - offset
        pygame.draw.circle(screen, (255,255,255), (dp.x + self.rect.w * 0.25, dp.y + self.rect.h * 0.33), 5)
        pygame.draw.circle(screen, (255,255,255), (dp.x + self.rect.w * 0.70, dp.y + self.rect.h * 0.33), 5)
        pygame.draw.circle(screen, (0,0,0), (dp.x + self.rect.w * 0.25, dp.y + self.rect.h * 0.33), 2)
        pygame.draw.circle(screen, (0,0,0), (dp.x + self.rect.w * 0.70, dp.y + self.rect.h * 0.33), 2)
        if self.special_ability == "orbital":
            t = pygame.time.get_ticks() / 250
            for i in range(2):
                ang = t + i * math.pi
                ox = dp.x + self.rect.w / 2 + math.cos(ang) * (self.rect.w * 0.8)
                oy = dp.y + self.rect.h / 2 + math.sin(ang) * (self.rect.h * 0.8)
                pygame.draw.circle(screen, Data.COLOR_OUTLINE, (ox, oy), 7)
                pygame.draw.circle(screen, (255, 210, 60), (ox, oy), 4)

class TankEnemy(Enemy):
    def __init__(self, x, y, **kwargs):
        # Forzamos el tipo para que la logica base no se rompa, pero usamos stats propios
        kwargs["enemy_type"] = "tank"
        super().__init__(x, y, **kwargs)
        self.hp *= 3.5          # Mucha mas vida
        self.speed *= 0.55      # Mas lento
        self.color = (80, 20, 20) # Rojo oscuro
        self.score_value = int(self.score_value * 2.5)
        # Hacerlo visualmente mas grande
        center = self.rect.center
        self.rect.width = int(self.rect.width * 1.4)
        self.rect.height = int(self.rect.height * 1.4)
        self.rect.center = center

class ExploderEnemy(Enemy):
    def __init__(self, x, y, **kwargs):
        kwargs["enemy_type"] = "exploder"
        super().__init__(x, y, **kwargs)
        self.hp *= 0.45         # Menos vida
        self.speed *= 1.45      # Muy rapido
        self.color = (255, 140, 0) # Naranja
        self.score_value = int(self.score_value * 1.5)

    def on_death(self, game):
        # Explosion de tinta al morir
        game.draw_ink_splat(self.pos, self.color, 90)
        game.trigger_shake(15, 20)
        # (Opcional) Podria dañar al jugador si esta muy cerca, por ahora solo visual/shake

class Player(Entity):
    def __init__(self):
        super().__init__(Data.WIDTH//2, Data.HEIGHT//2, Data.PLAYER_SIZE[0], Data.PLAYER_SIZE[1])
        self.hp = Data.PLAYER_MAX_HP
        self.energy = 0
        self.max_energy = Data.INITIAL_MAX_ENERGY
        self.level = 1
        self.anim_timer = 0

        # Power-ups
        self.active_powerup = None
        self.powerup_timer = 0
        self.selected_ink_type = "heavy"
        
        # Estadísticas base
        self.base_fire_rate = Data.SHOOT_COOLDOWN
        self.base_damage = Data.FIREBALL_DAMAGE
        self.base_speed = Data.PLAYER_SPEED
        
        # Buffs activos (timer en milisegundos)
        self.buffs = {
            "shield": 0,
            "haste": 0,
            "multishot": 0,
            "orbitals": 0,
            "ink_trail": 0,
            "confetti": 0,
            "giant": 0,
            "dash_invuln": 0,
            "adrenaline": 0,
            "flame_ring": 0,
            "arcane_volley": 0,
            "storm_sparks": 0,
            "blade_dance": 0
        }
        self.upgrades = {
            "mana_magnet": False,
            "magic_bounce": False,
            "piercing": False,
            "dash": True,
            "vampirism": False,
            "rubber_body": False,
            "clone": False,
            "freeze_time": False,
            "boomerang": False,
            "giant_unlock": False,
            "crit_mastery": False,
            "second_wind": False,
            "shockwave": False,
            "adrenaline_rush": False
        }
        self.skill_levels = {
            "speed": 0,
            "damage": 0,
            "rate": 0,
            "shield": 0,
            "haste": 0,
            "multishot": 0,
            "orbitals": 0,
            "heal": 0,
            "ink": 0,
            "confetti": 0,
            "mana_magnet": 0,
            "magic_bounce": 0,
            "piercing": 0,
            "dash": 0,
            "vampirism": 0,
            "rubber_body": 0,
            "clone": 0,
            "giant_unlock": 0,
            "freeze_time": 0,
            "boomerang": 0,
            "crit_mastery": 0,
            "second_wind": 0,
            "shockwave": 0,
            "adrenaline_rush": 0,
            "flame_ring": 0,
            "arcane_volley": 0,
            "storm_sparks": 0,
            "blade_dance": 0
        }
        self.kills_for_heal = 0
        self.damage_reduction = 0.0
        self.pickup_radius = 0
        self.dash_cooldown = 0
        self.clone_cooldown = 0
        self.freeze_cooldown = 0
        self.boomerang_cooldown = 0
        self.giant_cooldown = 0
        self.shockwave_cooldown = 0
        self.adrenaline_cooldown = 0
        self.second_wind_tick = 0
        self.second_wind_lock = 0
        self.arcane_volley_tick = 0
        self.storm_sparks_tick = 0
        self.blade_dance_tick = 0
        self.last_move_dir = pygame.Vector2(1, 0)
        self.giant_applied = False

    def get_speed(self):
        speed_mult = 2.0 if self.buffs["haste"] > 0 else 1.0
        if self.buffs["adrenaline"] > 0:
            speed_mult *= 1.20
        return self.base_speed * speed_mult

    def move(self, keys):
        move_vec = pygame.Vector2(0, 0)
        if keys[pygame.K_w]: move_vec.y -= 1
        if keys[pygame.K_s]: move_vec.y += 1
        if keys[pygame.K_a]: move_vec.x -= 1
        if keys[pygame.K_d]: move_vec.x += 1
        
        if move_vec.length() > 0:
            if pygame.time.get_ticks() % 100 < 20:
                logger.debug(f"Jugador en pos: {self.pos}")
            self.last_move_dir = move_vec.normalize()
            self.pos += move_vec.normalize() * self.get_speed()
            self.anim_timer += 0.2
        self.update_rect()

    def set_giant_form(self, active):
        if active and not self.giant_applied:
            center = pygame.Vector2(self.rect.center)
            self.rect.w = Data.PLAYER_SIZE[0] * 2
            self.rect.h = Data.PLAYER_SIZE[1] * 2
            self.pos = center - pygame.Vector2(self.rect.w / 2, self.rect.h / 2)
            self.update_rect()
            self.giant_applied = True
        elif (not active) and self.giant_applied:
            center = pygame.Vector2(self.rect.center)
            self.rect.w = Data.PLAYER_SIZE[0]
            self.rect.h = Data.PLAYER_SIZE[1]
            self.pos = center - pygame.Vector2(self.rect.w / 2, self.rect.h / 2)
            self.update_rect()
            self.giant_applied = False

    def apply_powerup(self, type):
        self.active_powerup = type
        self.powerup_timer = Data.POWERUP_DURATION_MS
        # Podríamos añadir un sonido aquí
        logger.info(f"Power-up activado: {type}")

    def draw(self, screen, offset):
        bounce = abs(math.sin(self.anim_timer)) * 4
        self.draw_flame_ring(screen, offset, bounce)
        self.draw_cartoon_rect(screen, Data.COLOR_PLAYER, offset + pygame.Vector2(0, bounce))
        dp = self.pos - offset + pygame.Vector2(0, bounce)
        
        # Efecto Escudo
        if self.buffs["shield"] > 0:
            shield_layer = pygame.Surface((96, 96), pygame.SRCALPHA)
            pygame.draw.circle(
                shield_layer,
                Data.COLOR_SHIELD,
                (48, 48),
                40,
                3
            )
            screen.blit(shield_layer, (int(dp.x - 24), int(dp.y - 24)))
            
        # Ojos
        pygame.draw.ellipse(screen, (255,255,255), (dp.x + 10, dp.y + 10, 10, 14))
        pygame.draw.ellipse(screen, (255,255,255), (dp.x + 28, dp.y + 10, 10, 14))

    def draw_flame_ring(self, screen, offset, bounce):
        if self.buffs["flame_ring"] <= 0:
            return
        fr_lvl = max(1, self.skill_levels.get("flame_ring", 1))
        now = pygame.time.get_ticks() / 160.0
        center = pygame.Vector2(self.rect.centerx - offset.x, self.rect.centery - offset.y + bounce)
        base_radius = 95 + (8 * fr_lvl)
        breath = math.sin(now) * (3 + fr_lvl * 0.3)
        radius = max(24, int(base_radius + breath))
        color = Data.COLOR_FIREBALL[:3]
        ring_width = max(2, int(6 - min(3, abs(math.sin(now * 0.9)) * 4)))
        for i in range(3):
            rr = radius - (i * 8)
            if rr <= 0:
                continue
            alpha = max(24, 92 - i * 24)
            layer = pygame.Surface((rr * 2 + 8, rr * 2 + 8), pygame.SRCALPHA)
            pygame.draw.circle(layer, (color[0], color[1], color[2], alpha), (layer.get_width() // 2, layer.get_height() // 2), rr, max(1, ring_width - i))
            screen.blit(layer, (int(center.x - layer.get_width() // 2), int(center.y - layer.get_height() // 2)))


class AdminNPC(Entity):
    def __init__(self, player):
        super().__init__(player.pos.x + random.uniform(-70, 70), player.pos.y + random.uniform(-70, 70), player.rect.w, player.rect.h)
        self.hp = float(player.hp)
        self.energy = int(player.energy)
        self.base_speed = float(player.base_speed)
        self.anim_timer = random.random() * 6.28
        self.color = (120, 235, 170)
        self.follow_offset = pygame.Vector2(random.uniform(-90, 90), random.uniform(-80, 80))
        self.roam_target = pygame.Vector2(self.pos)

    def update_follow(self, player_history):
        if not player_history:
            return
        target = pygame.Vector2(player_history[0]) + self.follow_offset
        direction = target - self.pos
        if direction.length() > 0.5:
            step = min(direction.length(), max(1.4, self.base_speed * 0.88))
            self.pos += direction.normalize() * step
            self.anim_timer += 0.16
        self.update_rect()

    def update_free_roam(self):
        if (self.roam_target - self.pos).length() < 28:
            self.roam_target = self.pos + pygame.Vector2(random.uniform(-220, 220), random.uniform(-220, 220))
        direction = self.roam_target - self.pos
        if direction.length() > 0:
            step = min(direction.length(), max(1.2, self.base_speed * 0.75))
            self.pos += direction.normalize() * step
            self.anim_timer += 0.12
        self.update_rect()

    def draw(self, screen, offset):
        bounce = abs(math.sin(self.anim_timer)) * 3
        draw_pos = self.pos - offset + pygame.Vector2(0, bounce)
        pygame.draw.rect(screen, Data.COLOR_OUTLINE, (draw_pos.x - 3, draw_pos.y - 3, self.rect.w + 6, self.rect.h + 6), border_radius=8)
        pygame.draw.rect(screen, self.color, (draw_pos.x, draw_pos.y, self.rect.w, self.rect.h), border_radius=8)
        pygame.draw.ellipse(screen, (255, 255, 255), (draw_pos.x + 10, draw_pos.y + 10, 10, 14))
        pygame.draw.ellipse(screen, (255, 255, 255), (draw_pos.x + 28, draw_pos.y + 10, 10, 14))
        pygame.draw.circle(screen, (0, 0, 0), (draw_pos.x + 15, draw_pos.y + 17), 2)
        pygame.draw.circle(screen, (0, 0, 0), (draw_pos.x + 33, draw_pos.y + 17), 2)
        tag = pygame.font.SysFont("Comic Sans MS", 15, bold=True).render("NPC", True, (20, 45, 20))
        screen.blit(tag, (draw_pos.x + self.rect.w / 2 - tag.get_width() / 2, draw_pos.y - 18))

class AudioManager:
    def __init__(self, music_dir, resources=None):
        self.music_dir = music_dir
        self.resources = resources or ResourceCache()
        self.enabled = False
        self.current_music_track = None
        self.sounds = {}
        self.cooldowns = {}
        self.volumes = {
            "master": Data.MASTER_VOLUME_DEFAULT,
            "music": 0.55,
            "ui": 0.85,
            "player": 0.85,
            "combat": 0.9
        }

    def setup(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.set_num_channels(32)
            self.enabled = True
        except pygame.error:
            self.enabled = False

    def update(self, dt):
        for key in list(self.cooldowns.keys()):
            self.cooldowns[key] = max(0, self.cooldowns[key] - dt)

    def _resolve_path(self, filename):
        key = (os.path.abspath(self.music_dir), str(filename).lower())
        cached = self.resources.path_cache.get(key)
        if cached:
            return cached
        exact = os.path.join(self.music_dir, filename)
        if os.path.exists(exact):
            self.resources.path_cache[key] = exact
            return exact
        if not os.path.isdir(self.music_dir):
            return None
        wanted = filename.lower()
        for name in os.listdir(self.music_dir):
            if name.lower() == wanted:
                resolved = os.path.join(self.music_dir, name)
                self.resources.path_cache[key] = resolved
                return resolved
        return None

    def load_sound(self, key, filename, group="combat"):
        if not self.enabled:
            return
        path = self._resolve_path(filename)
        if not path:
            print(f"[AudioManager] Recurso SFX no encontrado: {filename}")
            return
        try:
            if path not in self.resources.sound_cache:
                self.resources.sound_cache[path] = pygame.mixer.Sound(path)
            self.sounds[key] = {"sound": self.resources.sound_cache[path], "group": group}
        except pygame.error as e:
            print(f"[AudioManager] Error cargando SFX '{filename}': {e}")

    def _effective_volume(self, group, scale=1.0):
        v = self.volumes["master"] * self.volumes.get(group, 1.0) * scale
        return max(0.0, min(1.0, v))

    def play_sfx(self, key, cooldown_ms=0, cooldown_key=None, volume_scale=1.0):
        if not self.enabled:
            return
        data = self.sounds.get(key)
        if not data:
            return
        gate = cooldown_key or key
        if self.cooldowns.get(gate, 0) > 0:
            return
        ch = pygame.mixer.find_channel(True)
        if ch is None:
            return
        ch.set_volume(self._effective_volume(data["group"], volume_scale))
        ch.play(data["sound"])
        if cooldown_ms > 0:
            self.cooldowns[gate] = cooldown_ms

    def play_random(self, keys, cooldown_ms=0, cooldown_key=None, volume_scale=1.0):
        if not keys:
            return
        self.play_sfx(random.choice(keys), cooldown_ms=cooldown_ms, cooldown_key=cooldown_key, volume_scale=volume_scale)

    def play_music(self, filename, force=False):
        if not self.enabled:
            return
        if (not force) and self.current_music_track == filename:
            return
        path = self._resolve_path(filename)
        if not path:
            print(f"[AudioManager] Recurso de musica no encontrado: {filename}")
            return
        try:
            pygame.mixer.music.fadeout(220)
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self._effective_volume("music"))
            pygame.mixer.music.play(-1, fade_ms=300)
            self.current_music_track = filename
        except pygame.error as e:
            print(f"[AudioManager] Error reproduciendo musica '{filename}': {e}")

    def set_volume(self, key, value):
        if key not in self.volumes:
            return
        self.volumes[key] = max(0.0, min(1.0, value))
        if key in ("master", "music") and self.enabled and pygame.mixer.get_init():
            pygame.mixer.music.set_volume(self._effective_volume("music"))

    def get_volume(self, key):
        return self.volumes.get(key, 1.0)

    def stop(self):
        if self.enabled and pygame.mixer.get_init():
            pygame.mixer.music.stop()


class StorageManager:
    """
    Capa de persistencia (save/load).
    Para devs: evita escribir archivos directo fuera de esta clase.
    """
    def __init__(self, base_dir):
        self.base_dir = base_dir
        # Usamos las rutas seguras definidas en Data
        self.save_root = os.path.join(Data.USER_BASE_PATH, "save")
        self.current_dir = os.path.dirname(Data.SAVE_FILE)
        self.partidas_dir = Data.PARTIDAS_DIR
        self.records_path = Data.RECORDS_FILE
        self.settings_path = Data.SETTINGS_FILE
        self.current_save_path = Data.SAVE_FILE
        self.session = None
        
        # Crear la estructura de carpetas automáticamente si no existe
        os.makedirs(self.current_dir, exist_ok=True)
        os.makedirs(self.partidas_dir, exist_ok=True)
        
        logger.info(f"Sistema de archivos redirigido a: {self.save_root}")

    def _write_json(self, path, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        logger.debug(f"Guardando datos en: {path}")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _read_json(self, path, fallback):
        if not os.path.exists(path):
            return fallback
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except (ValueError, OSError, json.JSONDecodeError, TypeError):
            return fallback

    def load_settings(self, defaults):
        local = self._read_json(self.settings_path, None)
        if isinstance(local, dict):
            return local
        # Migracion ligera desde ruta legacy
        legacy = self._read_json(os.path.join(self.base_dir, "settings.json"), None)
        if isinstance(legacy, dict):
            self._write_json(self.settings_path, legacy)
            return legacy
        return defaults

    def save_settings(self, payload):
        self._write_json(self.settings_path, payload)

    def load_global_records(self):
        data = self._read_json(self.records_path, None)
        if isinstance(data, list):
            return data
        legacy = self._read_json(os.path.join(self.base_dir, "records.json"), None)
        if isinstance(legacy, list):
            self._write_json(self.records_path, legacy)
            return legacy
        return []

    def load_session_records(self):
        out = []
        if not os.path.isdir(self.partidas_dir):
            return out
        for entry in os.listdir(self.partidas_dir):
            rec_path = os.path.join(self.partidas_dir, entry, "data", "record.json")
            data = self._read_json(rec_path, None)
            if isinstance(data, dict):
                out.append(data)
        return out

    def save_global_records(self, records):
        self._write_json(self.records_path, records)

    def create_session(self, reason="new_game"):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rnd = random.randint(1000, 9999)
        sid = f"partida_{stamp}_{rnd}"
        session_dir = os.path.join(self.partidas_dir, sid)
        data_dir = os.path.join(session_dir, "data")
        world_dir = os.path.join(session_dir, "world")
        skills_dir = os.path.join(session_dir, "skills")
        rec_dir = os.path.join(session_dir, "recordings")
        for d in (session_dir, data_dir, world_dir, skills_dir, rec_dir):
            os.makedirs(d, exist_ok=True)

        scens = {
            "type": "GAME_SESSION",
            "version": Data.STORAGE_VERSION,
            "session_id": sid,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "created_reason": reason,
            "paths": {
                "data": "data",
                "world": "world",
                "skills": "skills",
                "recordings": "recordings",
                "record_summary": "data/record.json",
                "world_state": "world/state.json",
                "save_snapshot": "data/save_snapshot.json"
            }
        }
        self._write_json(os.path.join(session_dir, "session.scens"), scens)
        logger.info(f"Nueva sesión de juego creada: {sid}")
        self.session = {
            "id": sid,
            "dir": session_dir,
            "data_dir": data_dir,
            "world_dir": world_dir,
            "skills_dir": skills_dir,
            "recordings_dir": rec_dir,
            "scens_path": os.path.join(session_dir, "session.scens")
        }
        return self.session

    def attach_session(self, session_dir):
        if not os.path.isdir(session_dir):
            return False
        data_dir = os.path.join(session_dir, "data")
        world_dir = os.path.join(session_dir, "world")
        skills_dir = os.path.join(session_dir, "skills")
        rec_dir = os.path.join(session_dir, "recordings")
        for d in (data_dir, world_dir, skills_dir, rec_dir):
            os.makedirs(d, exist_ok=True)
        session_id = os.path.basename(session_dir)
        self.session = {
            "id": session_id,
            "dir": session_dir,
            "data_dir": data_dir,
            "world_dir": world_dir,
            "skills_dir": skills_dir,
            "recordings_dir": rec_dir,
            "scens_path": os.path.join(session_dir, "session.scens")
        }
        return True

    def has_session(self):
        return self.session is not None

    def write_world_state(self, game):
        if not self.session:
            return
        payload = {
            "player": {
                "x": round(float(game.player.pos.x), 2),
                "y": round(float(game.player.pos.y), 2),
                "hp": round(float(game.player.hp), 2),
                "energy": int(game.player.energy)
            },
            "enemies": [
                {"x": round(float(e.pos.x), 2), "y": round(float(e.pos.y), 2), "hp": round(float(e.hp), 2)}
                for e in game.enemies
            ],
            "drops": [
                {"x": round(float(d.pos.x), 2), "y": round(float(d.pos.y), 2)}
                for d in game.drops
            ],
            "camera": {"x": round(float(game.camera_offset.x), 2), "y": round(float(game.camera_offset.y), 2)},
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self._write_json(os.path.join(self.session["world_dir"], "state.json"), payload)

    def write_skill_files(self, player):
        if not self.session:
            return
        for skill_id, level in player.skill_levels.items():
            payload = {
                "skill_id": skill_id,
                "level": int(level),
                "unlocked": bool(player.upgrades.get(skill_id, False)),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self._write_json(os.path.join(self.session["skills_dir"], f"{skill_id}.json"), payload)

    def write_session_data(self, data_name, payload):
        if not self.session:
            return
        self._write_json(os.path.join(self.session["data_dir"], data_name), payload)

    def write_recording(self, recording_data):
        if not self.session or not recording_data:
            return
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._write_json(os.path.join(self.session["recordings_dir"], f"record_{stamp}.json"), recording_data)

    def update_scens_metadata(self, meta_updates):
        if not self.session:
            return
        scens_path = self.session.get("scens_path")
        data = self._read_json(scens_path, {})
        if not isinstance(data, dict):
            data = {}
        meta = data.get("meta", {})
        if not isinstance(meta, dict):
            meta = {}
        meta.update(meta_updates)
        data["meta"] = meta
        self._write_json(scens_path, data)

    def save_current_snapshot(self, save_payload):
        self._write_verified_snapshot(self.current_save_path, save_payload)
        if self.session:
            self._write_verified_snapshot(os.path.join(self.session["data_dir"], "save_snapshot.json"), save_payload)

    def _write_verified_snapshot(self, path, payload):
        backup_path = f"{path}.bak"
        previous = self._read_json(path, None) if os.path.exists(path) else None
        if isinstance(previous, dict):
            self._write_json(backup_path, previous)
        try:
            self._write_json(path, payload)
        except OSError:
            pass
        valid = False
        try:
            valid = os.path.getsize(path) > 0 and isinstance(self._read_json(path, None), dict)
        except OSError:
            valid = False
        if valid:
            return True
        restore = self._read_json(backup_path, None)
        if isinstance(restore, dict):
            self._write_json(path, restore)
        return False

    def load_current_snapshot(self):
        return self._read_json(self.current_save_path, None)


class Localizer:
    """
    Sistema de idiomas (ES/EN).
    Fuente recomendada: resources/lang/langs.json.
    """
    SUPPORTED = ("es", "en")

    def __init__(self, resources_dir, language="es"):
        # Se carga desde resources/lang/langs.json (formato recomendado).
        self.resources_dir = resources_dir
        self.language = language if language in self.SUPPORTED else "es"
        self.catalog = {}
        self.load_catalog()

    def load_catalog(self):
        self.catalog = {}
        lang_dir = os.path.join(self.resources_dir, "lang")
        modern_path = os.path.join(lang_dir, "langs.json")
        legacy_path = os.path.join(lang_dir, f"{self.language}.json")
        try:
            if os.path.exists(modern_path):
                with open(modern_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    # Formato esperado: key -> {"es": "...", "en": "..."}
                    for k, row in data.items():
                        if isinstance(row, dict):
                            self.catalog[str(k)] = row
                        elif isinstance(row, str):
                            # Compatibilidad defensiva para filas antiguas.
                            self.catalog[str(k)] = {"es": row}
                    return
            if os.path.exists(legacy_path):
                with open(legacy_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    # Legacy: key -> "texto"
                    for k, v in data.items():
                        self.catalog[str(k)] = {self.language: str(v)}
        except Exception as e:
            logger.error(f"Error cargando idioma {self.language}: {e}")

    def set_language(self, language):
        self.language = language if language in self.SUPPORTED else "es"
        self.load_catalog() # Recargar catalogo al cambiar idioma

    def tr(self, key, default=None, **kwargs):
        row = self.catalog.get(str(key), {})
        text = row.get(self.language) or row.get("es") or (default if default is not None else str(key))
        try:
            return text.format(**kwargs)
        except Exception:
            return text


class Mp4Recorder:
    def __init__(self):
        self.writer = None
        self.path = None
        self.active = False
        self.accum_ms = 0
        self.frame_interval_ms = max(1, int(1000 / Data.RECORD_VIDEO_FPS))

    def start(self, out_path):
        self.stop()
        if imageio is None:
            return False
        try:
            self.writer = imageio.get_writer(out_path, fps=Data.RECORD_VIDEO_FPS, codec="libx264", quality=7, macro_block_size=None)
            self.path = out_path
            self.active = True
            self.accum_ms = 0
            return True
        except Exception:
            self.writer = None
            self.path = None
            self.active = False
            return False

    def capture(self, surface, dt):
        if (not self.active) or self.writer is None:
            return
        self.accum_ms += dt
        if self.accum_ms < self.frame_interval_ms:
            return
        self.accum_ms = 0
        frame = pygame.surfarray.array3d(surface).swapaxes(0, 1)
        try:
            self.writer.append_data(frame)
        except Exception:
            self.stop()

    def stop(self):
        if self.writer is not None:
            try:
                self.writer.close()
            except Exception:
                pass
        self.writer = None
        self.path = None
        self.active = False
        self.accum_ms = 0


class Game:
    """
    Orquestador principal del juego:
    - run() gestiona eventos
    - update() aplica simulacion
    - draw() renderiza pantalla
    """
    def __init__(self):
        # base_dir = carpeta del script, project_root = raiz detectada con resources/
        self.base_dir = os.path.dirname(__file__)
        self.project_root = PROJECT_ROOT
        self.resources_dir = RESOURCES_DIR
        
        # Cargar configuración externa
        Data.load_config()
        
        pygame.init()
        pygame.event.set_allowed([
            pygame.QUIT,
            pygame.KEYDOWN, pygame.KEYUP,
            pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION
        ])
        self.screen = pygame.display.set_mode((Data.WIDTH, Data.HEIGHT))
        pygame.display.set_caption("InkSiege")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Comic Sans MS", 20, bold=True)
        self.title_font = pygame.font.SysFont("Comic Sans MS", 36, bold=True)
        self.resource_cache = ResourceCache()
        self.music_dir = os.path.join(self.resources_dir, "assets", "music")
        self.audio = AudioManager(self.music_dir, resources=self.resource_cache)
        self.storage = StorageManager(self.base_dir)
        self.localizer = Localizer(self.resources_dir, language="es")
        self.volume_items = [
            ("master", "volume.master"),
            ("music", "volume.music"),
            ("ui", "volume.ui"),
            ("player", "volume.player"),
            ("combat", "volume.combat")
        ]
        
        self.player = None
        self.enemies = []
        self.projectiles = []
        self.particles = []
        self.drops = []
        self.powerups = []
        self.camera_offset = pygame.Vector2(0, 0)
        
        self.running = True
        self.state = "MENU"
        self.menu_panel = "MAIN"
        self.menu_message = ""
        self.menu_message_time = 0
        self.pause_message = ""
        self.pause_message_time = 0
        self.spawn_timer = 0
        self.fire_timer = 0
        self.score = 0
        self.combo_multiplier = 1.0
        self.combo_timer = 0
        self.upgrade_options = []
        self.records = self.load_records()
        self.settings = self.load_settings()
        self.language = str(self.settings.get("language", "es"))
        self.localizer.set_language(self.language)
        self.session_active = False
        self.session_recorded = False
        self.session_started_at = 0
        self.session_stats = {}
        self.record_enabled = bool(self.settings.get("record_enabled", False))
        self.recording_data = None
        self.recording_tick_accum = 0
        self.video_recorder = Mp4Recorder()
        self.video_recording_enabled_runtime = False
        self.video_last_dt = 0
        self.video_file_name = ""
        self.replay_frames = deque(maxlen=Data.REPLAY_FPS * Data.REPLAY_DURATION_S)
        self.highlight_saved = False
        self.highlight_message = ""
        self.highlight_message_timer = 0
        self.storage_tick_accum = 0
        
        # --- NUEVO: Sistema de Tinta y Shake ---
        self.ink_surface = pygame.Surface((Data.WIDTH, Data.HEIGHT), pygame.SRCALPHA)
        self.ink_trails = deque(maxlen=150)
        self.shake_intensity = 0
        self.shake_duration = 0
        self.shake_offset = pygame.Vector2(0, 0)
        self.walk_ink_timer = 0
        # ---------------------------------------
        
        self.loadable_saves = []
        self.admin_mode = False
        self.admin_god_mode = False
        self.is_console_open = False
        self.console_input = ""
        self.console_log = []
        self.console_forced_pause = False
        self.creative_mode = False
        self.admin_npcs = []
        self.player_trail = deque(maxlen=360)
        self.admin_disable_player_shoot = False
        self.admin_npc_free_mode = False
        self.admin_npc_shoot_mode = False
        self.admin_npc_shoot_timer = 0
        self.enemy_target_mode = "player"
        self.enemy_spawn_origin = "player"
        self.admin_ignore_runtime_limits = False

        self.setup_audio()
        self.apply_settings_to_audio()
        self.reset_game()

    def tr(self, key, default=None, **kwargs):
        return self.localizer.tr(key, default=default, **kwargs)

    def init_session_stats(self):
        self.session_stats = {
            "damage_taken": 0.0,
            "damage_dealt": 0.0,
            "enemies_killed": 0,
            "shots_fired": 0,
            "shots_hit": 0,
            "mana_collected": 0,
            "upgrades_picked": 0,
            "kill_chain_max": 0
        }
        self.kill_chain_count = 0

    def init_local_telemetry(self):
        self.telemetry = {
            "fps_sum": 0.0,
            "fps_samples": 0,
            "max_entities": {
                "enemies": 0,
                "projectiles": 0,
                "particles": 0,
                "drops": 0,
                "total": 0
            },
            "phase_time_ms": {
                "early": 0,
                "mid": 0,
                "late": 0,
                "apex": 0,
                "infernal": 0
            },
            "entity_limit_hits": {
                "enemies": 0,
                "enemy_collisions": 0,
                "projectiles": 0,
                "particles": 0,
                "drops": 0
            },
            "validator_corrections": {
                "final_boss_unique": 0,
                "pending_non_negative": 0,
                "caps_sanitized": 0
            }
        }

    def get_local_telemetry_snapshot(self):
        avg_fps = 0.0
        if self.telemetry["fps_samples"] > 0:
            avg_fps = self.telemetry["fps_sum"] / self.telemetry["fps_samples"]
        return {
            "avg_fps": round(avg_fps, 2),
            "max_entities": dict(self.telemetry["max_entities"]),
            "phase_time_ms": dict(self.telemetry["phase_time_ms"]),
            "entity_limit_hits": dict(self.telemetry["entity_limit_hits"]),
            "validator_corrections": dict(self.telemetry["validator_corrections"])
        }

    def begin_session(self, reason="new_game", existing_session_dir=None):
        self.session_active = True
        self.session_recorded = False
        self.session_started_at = pygame.time.get_ticks()
        self.init_session_stats()
        if existing_session_dir and (not self.storage.attach_session(existing_session_dir)):
            self.storage.create_session(reason=reason)
        elif not existing_session_dir:
            self.storage.create_session(reason=reason)
        self.storage.write_skill_files(self.player)
        self.storage.write_world_state(self)
        self.start_recording_session()

    def start_recording_session(self):
        self.recording_data = None
        self.recording_tick_accum = 0
        self.video_recording_enabled_runtime = False
        self.video_file_name = ""
        self.video_recorder.stop()
        if not self.record_enabled:
            return
        self.recording_data = {
            "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "snapshots": []
        }
        self.start_video_recording()

    def start_video_recording(self):
        if (not self.record_enabled) or (not self.storage.has_session()):
            return
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.video_file_name = f"gameplay_{stamp}.mp4"
        out_path = os.path.join(self.storage.session["recordings_dir"], self.video_file_name)
        self.video_recording_enabled_runtime = self.video_recorder.start(out_path)
        if self.recording_data is not None:
            self.recording_data["video_file"] = self.video_file_name if self.video_recording_enabled_runtime else ""

    def capture_video_frame(self, dt):
        if self.video_recording_enabled_runtime and self.state == "PLAYING":
            self.video_recorder.capture(self.screen, dt)

    def stop_video_recording(self):
        self.video_recorder.stop()
        self.video_recording_enabled_runtime = False

    def load_records(self):
        global_records = self.storage.load_global_records()
        session_records = self.storage.load_session_records()
        merged = []
        seen = set()
        for rec in global_records + session_records:
            key = (
                str(rec.get("session_id", "")),
                str(rec.get("played_at", "")),
                str(rec.get("score", "")),
                str(rec.get("duration_seconds", ""))
            )
            if key in seen:
                continue
            seen.add(key)
            merged.append(rec)
        merged.sort(key=lambda r: str(r.get("played_at", "")))
        return merged

    def load_settings(self):
        defaults = {
            "record_enabled": False,
            "language": "es",
            "volumes": {
                "master": Data.MASTER_VOLUME_DEFAULT,
                "music": 0.55,
                "ui": 0.85,
                "player": 0.85,
                "combat": 0.9
            }
        }
        raw = self.storage.load_settings(defaults)
        if not isinstance(raw, dict):
            return defaults
        merged = defaults.copy()
        merged["record_enabled"] = bool(raw.get("record_enabled", defaults["record_enabled"]))
        lang = str(raw.get("language", defaults["language"]))
        merged["language"] = lang if lang in ("es", "en") else "es"
        loaded_vols = raw.get("volumes", {})
        if isinstance(loaded_vols, dict):
            for k in merged["volumes"]:
                if k in loaded_vols:
                    merged["volumes"][k] = max(0.0, min(1.0, float(loaded_vols[k])))
        return merged

    def save_settings(self):
        payload = {
            "record_enabled": self.record_enabled,
            "language": self.language,
            "volumes": {k: self.audio.get_volume(k) for k in self.audio.volumes}
        }
        self.storage.save_settings(payload)

    def apply_settings_to_audio(self):
        vols = self.settings.get("volumes", {})
        for k in self.audio.volumes.keys():
            if k in vols:
                self.audio.set_volume(k, float(vols[k]))

    def cycle_language(self):
        self.language = "en" if self.language == "es" else "es"
        self.localizer.set_language(self.language)
        self.save_settings()

    def save_records(self):
        self.storage.save_global_records(self.records)

    def format_duration(self, seconds):
        secs = max(0, int(seconds))
        m, s = divmod(secs, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

    def finalize_session_record(self, end_reason):
        if (not self.session_active) or self.session_recorded:
            return
        self.stop_video_recording()
        elapsed_ms = max(0, pygame.time.get_ticks() - self.session_started_at)
        elapsed_sec = round(elapsed_ms / 1000.0, 2)
        record = {
            "session_id": self.storage.session["id"] if self.storage.has_session() else "",
            "played_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "end_reason": end_reason,
            "duration_seconds": elapsed_sec,
            "duration_label": self.format_duration(elapsed_sec),
            "score": int(self.score),
            "max_level": int(self.player.level if self.player else 0),
            "damage_taken_total": round(self.session_stats["damage_taken"], 2),
            "damage_dealt_total": round(self.session_stats["damage_dealt"], 2),
            "enemies_killed": int(self.session_stats["enemies_killed"]),
            "shots_fired": int(self.session_stats["shots_fired"]),
            "shots_hit": int(self.session_stats["shots_hit"]),
            "mana_collected": int(self.session_stats["mana_collected"]),
            "upgrades_picked": int(self.session_stats["upgrades_picked"]),
            "kill_chain_max": int(self.session_stats.get("kill_chain_max", 0)),
            "telemetry": self.get_local_telemetry_snapshot(),
            "video_file": self.video_file_name if self.video_file_name else ""
        }
        self.records.append(record)
        self.save_records()
        if self.storage.has_session():
            self.storage.write_session_data("record.json", record)
            self.storage.write_session_data("session_stats.json", {
                "recorded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "stats": self.session_stats
            })
            self.storage.write_session_data("telemetry_final.json", {
                "recorded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "telemetry": self.get_local_telemetry_snapshot()
            })
            self.storage.write_world_state(self)
            self.storage.write_skill_files(self.player)
            self.storage.update_scens_metadata({
                "ended_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "end_reason": end_reason,
                "score": int(self.score),
                "duration_seconds": elapsed_sec,
                "storage_version": Data.STORAGE_VERSION,
                "video_file": record["video_file"]
            })
        self.finalize_recording_file(record)
        self.session_recorded = True
        self.session_active = False

    def finalize_recording_file(self, record):
        if not self.recording_data:
            return
        self.recording_data["summary"] = record
        self.storage.write_recording(self.recording_data)
        self.recording_data = None

    def setup_audio(self):
        self.audio.setup()
        self.audio.load_sound("player_damage", "Da\u00f1o_player.mp3", group="player")
        self.audio.load_sound("shot_magic", "disparo_magic.mp3", group="combat")
        self.audio.load_sound("button_select", "Selecionar.mp3", group="ui")
        self.audio.load_sound("enemy_hit_1", "Da\u00f1o_enemigo_disparo_1.mp3", group="combat")
        self.audio.load_sound("enemy_hit_2", "Da\u00f1o_enemigo_disparo_2.mp3", group="combat")
        self.audio.load_sound("pop", "pop.mp3", group="player")
        self.update_music_for_state(force=True)

    # --- NUEVO: Métodos de Efectos ---
    def trigger_shake(self, intensity, duration):
        self.shake_intensity = intensity
        self.shake_duration = duration

    def update_shake(self):
        if self.shake_duration > 0:
            self.shake_duration -= 1
            sx = random.uniform(-self.shake_intensity, self.shake_intensity)
            sy = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.shake_offset = pygame.Vector2(sx, sy)
        else:
            self.shake_offset = pygame.Vector2(0, 0)

    def _generate_splat_offsets(self, radius):
        lobes = random.randint(7, 11)
        steps = max(20, int(radius * 1.4))
        phase_a = random.uniform(0, math.pi * 2)
        phase_b = random.uniform(0, math.pi * 2)
        points = []
        for i in range(steps):
            ang = (math.pi * 2 * i) / steps
            wave_a = 0.22 * math.sin(ang * lobes + phase_a)
            wave_b = 0.11 * math.sin(ang * (lobes * 2) + phase_b)
            jitter = random.uniform(-0.03, 0.03)
            rr = radius * (1.0 + wave_a + wave_b + jitter)
            rr = max(radius * 0.55, min(radius * 1.65, rr))
            points.append(pygame.Vector2(math.cos(ang) * rr, math.sin(ang) * rr))
        return points

    def draw_ink_splat(self, pos, color, size):
        rgb = tuple(int(c) for c in color[:3]) if len(color) >= 3 else (220, 40, 40)
        alpha = int(color[3]) if len(color) >= 4 else 210
        center = pygame.Vector2(pos)
        if size <= 8:
            self.ink_trails.append({
                "type": "circle",
                "pos": center,
                "size": size,
                "fill": (rgb[0], rgb[1], rgb[2], alpha)
            })
            return
        radius = max(12, size * random.uniform(0.85, 1.05))
        offsets = self._generate_splat_offsets(radius)
        droplets = []
        for _ in range(random.randint(2, 4)):
            base = random.choice(offsets)
            n = base.normalize() if base.length() > 0 else pygame.Vector2(1, 0)
            droplets.append({
                "offset": n * random.uniform(radius * 0.8, radius * 1.2),
                "r": random.uniform(radius * 0.18, radius * 0.30)
            })
        self.ink_trails.append({
            "type": "blob",
            "pos": center,
            "offsets": offsets,
            "droplets": droplets,
            "fill": (rgb[0], rgb[1], rgb[2], min(255, alpha + 10)),
            "rim": (max(0, rgb[0] - 45), max(0, rgb[1] - 45), max(0, rgb[2] - 45), min(255, alpha))
        })

    def play_shot_sfx(self):
        self.audio.play_sfx("shot_magic", cooldown_ms=50)

    def play_damage_sfx(self):
        self.audio.play_sfx("player_damage", cooldown_ms=90)

    def play_button_sfx(self):
        # Boton: siempre intentar reproducir, sin cooldown.
        if "button_select" not in self.audio.sounds:
            self.audio.load_sound("button_select", "Selecionar.mp3", group="ui")
        self.audio.play_sfx("button_select", cooldown_ms=0)

    def play_enemy_hit_sfx(self):
        self.audio.play_random(["enemy_hit_1", "enemy_hit_2"], cooldown_ms=30, cooldown_key="enemy_hit")

    def play_pop_sfx(self):
        self.audio.play_sfx("pop")

    def update_music_for_state(self, force=False):
        # Menu: fondo principal. Juego: fondo2.
        music = "fondo.mp3" if self.state == "MENU" else "fondo2.mp3"
        self.audio.play_music(music, force=force)

    def get_ink_profile(self, ink_type):
        profiles = {
            "fire": {
                "label": "Ignea",
                "color": (255, 90, 70),
                "damage_mult": Data.INK_FIRE_DAMAGE_MULT,
                "burn_duration_ms": Data.INK_FIRE_BURN_DURATION_MS,
                "burn_dps_ratio": Data.INK_FIRE_BURN_DPS_RATIO,
                "slow_duration_ms": 0,
                "knockback_mult": 0.90
            },
            "cryo": {
                "label": "Criogenica",
                "color": (70, 180, 255),
                "damage_mult": Data.INK_CRYO_DAMAGE_MULT,
                "burn_duration_ms": 0,
                "burn_dps_ratio": 0.0,
                "slow_duration_ms": Data.INK_CRYO_SLOW_DURATION_MS,
                "knockback_mult": 0.55
            },
            "heavy": {
                "label": "Pesada",
                "color": (48, 48, 62),
                "damage_mult": Data.INK_HEAVY_DAMAGE_MULT,
                "burn_duration_ms": 0,
                "burn_dps_ratio": 0.0,
                "slow_duration_ms": 0,
                "knockback_mult": Data.INK_HEAVY_KNOCKBACK_MULT
            }
        }
        return profiles.get(ink_type, profiles["heavy"])

    def get_current_ink_type(self):
        # Los power-ups actuales pueden sobreescribir temporalmente el tipo elegido.
        if self.player.active_powerup == "FIRE":
            return "fire"
        if self.player.active_powerup == "ICE":
            return "cryo"
        return self.player.selected_ink_type

    def set_player_ink_type(self, ink_type):
        if ink_type not in ("fire", "cryo", "heavy"):
            return
        self.player.selected_ink_type = ink_type
        profile = self.get_ink_profile(ink_type)
        logger.info(f"Tinta equipada: {profile['label']}")

    def reset_game(self):
        self.stop_video_recording()
        self.player = Player()
        self.enemies = []
        self.projectiles = []
        self.particles = []
        self.drops = []
        self.powerups = []
        self.ink_puddles = []
        self.clone_pos = None
        self.clone_timer = 0
        self.freeze_timer = 0
        self.camera_offset = pygame.Vector2(0, 0)
        self.spawn_timer = 0
        self.fire_timer = 0
        self.score = 0
        self.combo_multiplier = 1.0
        self.combo_timer = 0
        self.replay_frames.clear()
        self.highlight_saved = False
        self.highlight_message = ""
        self.highlight_message_timer = 0
        self.upgrade_options = []
        self.storage_tick_accum = 0
        self.session_elapsed_ms = 0
        self.player_hit_cooldown = 0
        self.diff_factor = 1.0
        self.infernal_mode = False
        self.max_diff_hold_ms = 0
        self.final_boss_spawned = False
        self.final_boss_defeated = False
        self.mass_kill_mode = False
        self.kills_since_boss = 0
        self.bosses_spawned = 0
        self.boss_alive = False
        self.pause_message = ""
        self.pause_message_time = 0
        self.creative_mode = False
        self.admin_npcs = []
        self.player_trail.clear()
        self.admin_disable_player_shoot = False
        self.admin_npc_free_mode = False
        self.admin_npc_shoot_mode = False
        self.admin_npc_shoot_timer = 0
        self.enemy_target_mode = "player"
        self.enemy_spawn_origin = "player"
        self.admin_ignore_runtime_limits = False
        self.pending_respawns = {
            "normal": 0,
            "elite": 0,
            "boss": 0
        }
        self.entity_frame_limits = {
            "enemies": Data.MAX_ACTIVE_ENEMIES_PER_FRAME,
            "enemy_collisions": Data.MAX_ACTIVE_ENEMY_COLLISIONS_PER_FRAME,
            "projectiles": Data.MAX_ACTIVE_PROJECTILES_PER_FRAME,
            "particles": Data.MAX_ACTIVE_PARTICLES_PER_FRAME,
            "drops": Data.MAX_ACTIVE_DROPS_PER_FRAME
        }
        self.frame_entity_cursor = {
            "enemies": 0,
            "enemy_collisions": 0,
            "projectiles": 0,
            "particles": 0,
            "drops": 0
        }
        self.init_local_telemetry()

    def refresh_loadable_saves(self):
        self.loadable_saves = []
        if not os.path.isdir(self.storage.partidas_dir):
            return
        for entry in os.listdir(self.storage.partidas_dir):
            session_dir = os.path.join(self.storage.partidas_dir, entry)
            scens_path = os.path.join(session_dir, "session.scens")
            snap_path = os.path.join(session_dir, "data", "save_snapshot.json")
            if (not os.path.isdir(session_dir)) or (not os.path.exists(scens_path)) or (not os.path.exists(snap_path)):
                continue
            meta = self.storage._read_json(scens_path, {}).get("meta", {})
            if not isinstance(meta, dict):
                continue
            end_reason = str(meta.get("end_reason", ""))
            if end_reason not in ("menu_exit", "quit"):
                continue
            snap = self.storage._read_json(snap_path, {})
            score = int(snap.get("score", 0))
            p = snap.get("player", {})
            lvl = int(p.get("level", 1)) if isinstance(p, dict) else 1
            self.loadable_saves.append({
                "session_id": entry,
                "ended_at": str(meta.get("ended_at", "")),
                "score": score,
                "level": lvl,
                "snapshot_path": snap_path
            })
        self.loadable_saves.sort(key=lambda x: (x.get("ended_at", ""), x.get("session_id", "")), reverse=True)

    def load_entry_rect(self, index):
        return pygame.Rect(Data.WIDTH // 2 - 500, 252 + index * 66, 1000, 58)

    def start_new_game(self):
        self.reset_game()
        self.state = "PLAYING"
        self.begin_session(reason="new_game")

    def save_game(self):
        if not self.player:
            return
        data = {
            "player": {
                "x": float(self.player.pos.x),
                "y": float(self.player.pos.y),
                "hp": float(self.player.hp),
                "energy": int(self.player.energy),
                "max_energy": int(self.player.max_energy),
                "level": int(self.player.level),
                "base_fire_rate": int(self.player.base_fire_rate),
                "base_damage": int(self.player.base_damage),
                "base_speed": float(self.player.base_speed),
                "ink_type": self.player.selected_ink_type,
                "buffs": {k: int(max(0, v)) for k, v in self.player.buffs.items()},
                "upgrades": self.player.upgrades,
                "skill_levels": self.player.skill_levels,
                "kills_for_heal": int(self.player.kills_for_heal),
                "damage_reduction": float(self.player.damage_reduction),
                "pickup_radius": int(self.player.pickup_radius)
            },
            "score": int(self.score)
        }
        self.storage.save_current_snapshot(data)
        if self.storage.has_session():
            self.storage.write_world_state(self)
            self.storage.write_skill_files(self.player)
            self.storage.write_session_data("runtime.json", {
                "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "state": self.state,
                "score": int(self.score),
                "player_level": int(self.player.level)
            })

    def load_game(self, snapshot_path=None):
        data = None
        existing_session_dir = None
        if snapshot_path:
            data = self.storage._read_json(snapshot_path, None)
            snap_dir = os.path.dirname(snapshot_path)
            if os.path.basename(snap_dir) == "data":
                existing_session_dir = os.path.dirname(snap_dir)
        else:
            data = self.storage.load_current_snapshot()
            if data is None and os.path.exists("savegame.json"):
                try:
                    with open("savegame.json", "r", encoding="utf-8") as f:
                        data = json.load(f)
                except (ValueError, OSError, json.JSONDecodeError, TypeError):
                    data = None
        if data is None:
            return False
        try:
            p = data.get("player", {})
            self.reset_game()
            self.player.pos.x = float(p.get("x", self.player.pos.x))
            self.player.pos.y = float(p.get("y", self.player.pos.y))
            self.player.update_rect()
            self.player.hp = max(1, min(Data.PLAYER_MAX_HP, float(p.get("hp", Data.PLAYER_MAX_HP))))
            self.player.energy = max(0, int(p.get("energy", 0)))
            self.player.max_energy = max(1, int(p.get("max_energy", Data.INITIAL_MAX_ENERGY)))
            self.player.level = max(1, int(p.get("level", 1)))
            self.player.base_fire_rate = max(80, int(p.get("base_fire_rate", Data.SHOOT_COOLDOWN)))
            self.player.base_damage = max(1, int(p.get("base_damage", Data.FIREBALL_DAMAGE)))
            self.player.base_speed = max(1.0, float(p.get("base_speed", Data.PLAYER_SPEED)))
            loaded_ink = str(p.get("ink_type", "heavy")).lower()
            self.player.selected_ink_type = loaded_ink if loaded_ink in ("fire", "cryo", "heavy") else "heavy"
            loaded_buffs = p.get("buffs", {})
            for k in self.player.buffs:
                self.player.buffs[k] = max(0, int(loaded_buffs.get(k, 0)))
            loaded_upgrades = p.get("upgrades", {})
            for k in self.player.upgrades:
                self.player.upgrades[k] = bool(loaded_upgrades.get(k, False))
            self.player.upgrades["dash"] = True
            loaded_levels = p.get("skill_levels", {})
            for k in self.player.skill_levels:
                self.player.skill_levels[k] = max(0, int(loaded_levels.get(k, self.player.skill_levels[k])))
            for k, unlocked in self.player.upgrades.items():
                if unlocked and self.player.skill_levels.get(k, 0) == 0:
                    self.player.skill_levels[k] = 1
            self.player.kills_for_heal = max(0, int(p.get("kills_for_heal", 0)))
            self.player.damage_reduction = max(0.0, min(0.8, float(p.get("damage_reduction", 0.0))))
            self.player.pickup_radius = max(0, int(p.get("pickup_radius", 0)))
            self.score = max(0, int(data.get("score", 0)))
            self.storage.save_current_snapshot(data)
            self.state = "PLAYING"
            self.begin_session(reason="loaded_save", existing_session_dir=existing_session_dir)
            return True
        except (ValueError, OSError, json.JSONDecodeError, TypeError):
            return False

    def generate_upgrades(self):
        pool = [
            {"id": "speed", "name": "Pasivo: Botas", "desc": "Velocidad +15% Permanente"},
            {"id": "damage", "name": "Pasivo: Fuerza", "desc": "Daño +20 Permanente"},
            {"id": "rate", "name": "Pasivo: Cadencia", "desc": "Disparo más rápido"},
            {"id": "shield", "name": "Activa: Escudo", "desc": "Invulnerable (8 seg)"},
            {"id": "haste", "name": "Activa: Turbo", "desc": "Velocidad x2 (6 seg)"},
            {"id": "multishot", "name": "Activa: Lluvia", "desc": "Triple disparo (10 seg)"},
            {"id": "orbitals", "name": "Activa: Cuchillas", "desc": "Daño orbital (12 seg)"},
            {"id": "flame_ring", "name": "Activa: Anillo de Fuego", "desc": "Aura de daño cercana"},
            {"id": "arcane_volley", "name": "Activa: Descarga Arcana", "desc": "Ráfagas en circulo"},
            {"id": "storm_sparks", "name": "Activa: Chispas de Tormenta", "desc": "Rayos automáticos"},
            {"id": "blade_dance", "name": "Activa: Danza de Cuchillas", "desc": "Abanico de cuchillas"},
            {"id": "heal", "name": "Consumible: Vida", "desc": "Cura 50 HP"},
            {"id": "ink", "name": "Activa: Charco de Tinta", "desc": "Rastro que frena y daña (10 seg)"},
            {"id": "confetti", "name": "Activa: Confeti", "desc": "30% explosión al matar (12 seg)"},
            {"id": "mana_magnet", "name": "Pasivo: Imán de Maná", "desc": "Recogida de maná ampliada"},
            {"id": "magic_bounce", "name": "Pasivo: Rebote Mágico", "desc": "Tus disparos rebotan 1 vez"},
            {"id": "piercing", "name": "Pasivo: Perforante", "desc": "Bala atraviesa hasta 3 enemigos"},
            {"id": "dash", "name": "Activa: Dash Fantasmal", "desc": "Tecla SHIFT (cooldown corto)"},
            {"id": "vampirism", "name": "Pasivo: Vampirismo", "desc": "Cada 10 kills curas 5"},
            {"id": "rubber_body", "name": "Pasivo: Cuerpo de Goma", "desc": "20% menos daño por contacto"},
            {"id": "crit_mastery", "name": "Pasivo: Precisión Critica", "desc": "Probabilidad de critico en disparos"},
            {"id": "second_wind", "name": "Pasivo: Segundo Aire", "desc": "Regeneración gradual de vida"},
            {"id": "clone", "name": "Activa: Clon de Papel", "desc": "Tecla C, distrae 5 seg"},
            {"id": "giant_unlock", "name": "Activa: Crecimiento Gigante", "desc": "Tecla G, 10 seg"},
            {"id": "freeze_time", "name": "Activa: Congelar Tiempo", "desc": "Tecla F, enemigos parados"},
            {"id": "boomerang", "name": "Activa: Gran Bumerán", "desc": "Tecla B, ida y vuelta"},
            {"id": "shockwave", "name": "Activa: Onda Expansiva", "desc": "Tecla Q, golpe de área"},
            {"id": "adrenaline_rush", "name": "Activa: Subidón de Adrenalina", "desc": "Tecla E, potencia temporal"}
        ]
        for upg in pool:
            uid = str(upg.get("id", ""))
            upg["name"] = self.tr(f"upgrade.{uid}.name", upg.get("name", uid))
            upg["desc"] = self.tr(f"upgrade.{uid}.desc", upg.get("desc", uid))
        available = pool[:]
        selected = []
        for _ in range(min(3, len(available))):
            pick = self.pick_upgrade_by_rarity(available)
            if pick is None:
                break
            selected.append(pick)
            available.remove(pick)
        for upg in selected:
            upg["rarity"] = self.get_upgrade_rarity(upg["id"])
        self.upgrade_options = selected

    def get_upgrade_rarity(self, uid):
        rarity_map = {
            "speed": "Comun",
            "damage": "Comun",
            "rate": "Comun",
            "heal": "Comun",
            "flame_ring": "Comun",
            "arcane_volley": "Comun",
            "storm_sparks": "Comun",
            "blade_dance": "Poco Comun",
            "shield": "Poco Comun",
            "haste": "Poco Comun",
            "mana_magnet": "Poco Comun",
            "multishot": "Raro",
            "orbitals": "Raro",
            "ink": "Raro",
            "magic_bounce": "Raro",
            "piercing": "Raro",
            "rubber_body": "Raro",
            "crit_mastery": "Raro",
            "second_wind": "Raro",
            "dash": "Epico",
            "confetti": "Epico",
            "vampirism": "Epico",
            "boomerang": "Epico",
            "shockwave": "Epico",
            "clone": "Legendario",
            "giant_unlock": "Legendario",
            "adrenaline_rush": "Legendario",
            "freeze_time": "Mitico"
        }
        return rarity_map.get(uid, "Comun")
    def pick_upgrade_by_rarity(self, candidates):
        if not candidates:
            return None
        grouped = {}
        for upg in candidates:
            rr = self.get_upgrade_rarity(upg["id"])
            grouped.setdefault(rr, []).append(upg)
        available_rarities = []
        weights = []
        for rr, weight in Data.UPGRADE_RARITY_WEIGHTS.items():
            if grouped.get(rr):
                available_rarities.append(rr)
                weights.append(weight)
        if not available_rarities:
            return random.choice(candidates)
        chosen_rarity = random.choices(available_rarities, weights=weights, k=1)[0]
        return random.choice(grouped[chosen_rarity])

    def ms_to_seconds_text(self, ms):
        return f"{(max(0, int(ms)) / 1000.0):.1f}s"

    def get_dash_invuln_ms(self, lvl):
        return 220 + (90 * max(1, int(lvl)))

    def get_clone_duration_ms(self, lvl):
        return 4200 + (900 * max(1, int(lvl)))

    def get_clone_cooldown_ms(self, lvl):
        return max(2500, 9000 - (450 * (max(1, int(lvl)) - 1)))

    def get_freeze_duration_ms(self, lvl):
        return 2500 + (700 * max(1, int(lvl)))

    def get_freeze_cooldown_ms(self, lvl):
        return max(4000, 12000 - (500 * (max(1, int(lvl)) - 1)))

    def get_boomerang_cooldown_ms(self, lvl):
        return max(3000, 7000 - (300 * (max(1, int(lvl)) - 1)))

    def get_giant_duration_ms(self, lvl):
        return 8000 + (1500 * max(1, int(lvl)))

    def get_giant_cooldown_ms(self, lvl):
        return max(5000, 15000 - (700 * (max(1, int(lvl)) - 1)))

    def get_shockwave_cooldown_ms(self, lvl):
        return max(2800, 9000 - (500 * (max(1, int(lvl)) - 1)))

    def get_adrenaline_duration_ms(self, lvl):
        return 3800 + (800 * max(1, int(lvl)))

    def get_adrenaline_cooldown_ms(self, lvl):
        return max(4500, 13000 - (650 * (max(1, int(lvl)) - 1)))

    def get_flame_ring_duration_ms(self, lvl):
        return 6500 + (900 * max(1, int(lvl)))

    def get_arcane_volley_duration_ms(self, lvl):
        return 7000 + (900 * max(1, int(lvl)))

    def get_storm_sparks_duration_ms(self, lvl):
        return 6800 + (1000 * max(1, int(lvl)))

    def get_blade_dance_duration_ms(self, lvl):
        return 6200 + (900 * max(1, int(lvl)))

    def get_upgrade_dynamic_desc(self, uid, level):
        lvl = max(1, int(level))
        if uid == "speed":
            return f"Velocidad +{0.45 + (0.15 * lvl):.2f}"
        if uid == "damage":
            return f"Daño +{12 + (4 * lvl)}"
        if uid == "rate":
            return f"Disparo -{30 + (4 * lvl)} ms"
        if uid == "shield":
            return f"Invulnerable {self.ms_to_seconds_text(7000 + (900 * lvl))}"
        if uid == "haste":
            return f"Velocidad x2 por {self.ms_to_seconds_text(5200 + (800 * lvl))}"
        if uid == "multishot":
            return f"Triple disparo {self.ms_to_seconds_text(9000 + (1200 * lvl))}"
        if uid == "orbitals":
            return f"Cuchillas activas {self.ms_to_seconds_text(10000 + (1200 * lvl))}"
        if uid == "heal":
            return f"Cura instantánea +{35 + (12 * lvl)} HP"
        if uid == "ink":
            return f"Charco de tinta {self.ms_to_seconds_text(9000 + (1200 * lvl))}"
        if uid == "confetti":
            return f"Confeti {self.ms_to_seconds_text(10000 + (1300 * lvl))}"
        if uid == "mana_magnet":
            return f"Radio de recogida: {100 + (20 * (lvl - 1))}"
        if uid == "magic_bounce":
            return "Tus disparos rebotan 1 vez"
        if uid == "piercing":
            return f"Atraviesa hasta {1 + (2 * lvl)} enemigos"
        if uid == "dash":
            inv = self.get_dash_invuln_ms(lvl)
            return f"SHIFT CD {self.ms_to_seconds_text(Data.DASH_COOLDOWN_MS)} | invuln {self.ms_to_seconds_text(inv)}"
        if uid == "vampirism":
            kills_needed = max(3, 10 - (lvl - 1))
            heal_amount = 3 + (2 * lvl)
            return f"Cura {heal_amount} cada {kills_needed} kills"
        if uid == "rubber_body":
            reduction = min(0.6, 0.12 + (0.04 * lvl)) * 100.0
            return f"Reducción de daño por contacto: {reduction:.0f}%"
        if uid == "crit_mastery":
            chance = min(55, int((0.08 + 0.04 * lvl) * 100))
            mult = 1.6 + (0.15 * lvl)
            return f"Crit {chance}% x{mult:.2f}"
        if uid == "second_wind":
            heal = 0.8 + (0.45 * lvl)
            return f"Regenera {heal:.1f} HP cada pocos segundos"
        if uid == "clone":
            dur = self.get_clone_duration_ms(lvl)
            cd = self.get_clone_cooldown_ms(lvl)
            return f"Tecla C: clon {self.ms_to_seconds_text(dur)} | CD {self.ms_to_seconds_text(cd)}"
        if uid == "giant_unlock":
            dur = self.get_giant_duration_ms(lvl)
            cd = self.get_giant_cooldown_ms(lvl)
            return f"Tecla G: gigante {self.ms_to_seconds_text(dur)} | CD {self.ms_to_seconds_text(cd)}"
        if uid == "freeze_time":
            dur = self.get_freeze_duration_ms(lvl)
            cd = self.get_freeze_cooldown_ms(lvl)
            return f"Tecla F: congelar {self.ms_to_seconds_text(dur)} | CD {self.ms_to_seconds_text(cd)}"
        if uid == "boomerang":
            cd = self.get_boomerang_cooldown_ms(lvl)
            return f"Tecla B: gran bumerán | CD {self.ms_to_seconds_text(cd)}"
        if uid == "shockwave":
            cd = self.get_shockwave_cooldown_ms(lvl)
            radius = 150 + (16 * lvl)
            return f"Tecla Q: onda {radius}px | CD {self.ms_to_seconds_text(cd)}"
        if uid == "adrenaline_rush":
            dur = self.get_adrenaline_duration_ms(lvl)
            cd = self.get_adrenaline_cooldown_ms(lvl)
            return f"Tecla E: buff {self.ms_to_seconds_text(dur)} | CD {self.ms_to_seconds_text(cd)}"
        if uid == "flame_ring":
            dur = self.get_flame_ring_duration_ms(lvl)
            return f"Aura de fuego {self.ms_to_seconds_text(dur)}"
        if uid == "arcane_volley":
            dur = self.get_arcane_volley_duration_ms(lvl)
            return f"Ráfagas arcanas {self.ms_to_seconds_text(dur)}"
        if uid == "storm_sparks":
            dur = self.get_storm_sparks_duration_ms(lvl)
            return f"Rayos automáticos {self.ms_to_seconds_text(dur)}"
        if uid == "blade_dance":
            dur = self.get_blade_dance_duration_ms(lvl)
            return f"Cuchillas giratorias {self.ms_to_seconds_text(dur)}"
        return "Mejora aplicada"

    def apply_upgrade(self, upgrade):
        uid = upgrade["id"]
        self.player.skill_levels[uid] = self.player.skill_levels.get(uid, 0) + 1
        lvl = self.player.skill_levels[uid]
        self.session_stats["upgrades_picked"] += 1

        if uid == "speed":
            self.player.base_speed += 0.45 + (0.15 * lvl)
        elif uid == "damage":
            self.player.base_damage += 12 + (4 * lvl)
        elif uid == "rate":
            self.player.base_fire_rate = max(70, self.player.base_fire_rate - (30 + (4 * lvl)))
        elif uid == "shield":
            self.player.buffs["shield"] = 7000 + (900 * lvl)
        elif uid == "haste":
            self.player.buffs["haste"] = 5200 + (800 * lvl)
        elif uid == "multishot":
            self.player.buffs["multishot"] = 9000 + (1200 * lvl)
        elif uid == "orbitals":
            self.player.buffs["orbitals"] = 10000 + (1200 * lvl)
        elif uid == "heal":
            self.player.hp = min(Data.PLAYER_MAX_HP, self.player.hp + (35 + 12 * lvl))
        elif uid == "ink":
            self.player.buffs["ink_trail"] = 9000 + (1200 * lvl)
        elif uid == "confetti":
            self.player.buffs["confetti"] = 10000 + (1300 * lvl)
        elif uid == "mana_magnet":
            self.player.upgrades["mana_magnet"] = True
            self.player.pickup_radius = 100 + (20 * (lvl - 1))
        elif uid == "magic_bounce": self.player.upgrades["magic_bounce"] = True
        elif uid == "piercing": self.player.upgrades["piercing"] = True
        elif uid == "dash": self.player.upgrades["dash"] = True
        elif uid == "vampirism": self.player.upgrades["vampirism"] = True
        elif uid == "rubber_body":
            self.player.upgrades["rubber_body"] = True
            self.player.damage_reduction = min(0.6, 0.12 + (0.04 * lvl))
        elif uid == "crit_mastery":
            self.player.upgrades["crit_mastery"] = True
        elif uid == "second_wind":
            self.player.upgrades["second_wind"] = True
        elif uid == "clone": self.player.upgrades["clone"] = True
        elif uid == "giant_unlock": self.player.upgrades["giant_unlock"] = True
        elif uid == "freeze_time": self.player.upgrades["freeze_time"] = True
        elif uid == "boomerang": self.player.upgrades["boomerang"] = True
        elif uid == "shockwave": self.player.upgrades["shockwave"] = True
        elif uid == "adrenaline_rush":
            self.player.upgrades["adrenaline_rush"] = True
            self.player.buffs["adrenaline"] = self.get_adrenaline_duration_ms(lvl)
        elif uid == "flame_ring":
            self.player.buffs["flame_ring"] = self.get_flame_ring_duration_ms(lvl)
        elif uid == "arcane_volley":
            self.player.buffs["arcane_volley"] = self.get_arcane_volley_duration_ms(lvl)
        elif uid == "storm_sparks":
            self.player.buffs["storm_sparks"] = self.get_storm_sparks_duration_ms(lvl)
        elif uid == "blade_dance":
            self.player.buffs["blade_dance"] = self.get_blade_dance_duration_ms(lvl)
        
        # Escalar dificultad
        self.player.energy = 0
        self.player.level += 1
        self.player.max_energy = int(self.player.max_energy * Data.ENERGY_SCALING)
        self.state = "PLAYING"

    def roll_special_ability(self):
        if random.random() >= Data.SPECIAL_ENEMY_CHANCE:
            return None
        return random.choice(["orbital", "dash", "regen"])

    def get_enemy_type_counts(self):
        normal_alive = 0
        elite_alive = 0
        boss_alive = 0
        for e in self.enemies:
            et = getattr(e, "enemy_type", "normal")
            if et == "elite":
                elite_alive += 1
            elif et == "boss":
                boss_alive += 1
            else:
                normal_alive += 1
        return normal_alive, elite_alive, boss_alive

    def get_respawn_delay_ms(self):
        if Data.DIFF_MAX <= 1.0:
            return Data.RESPAWN_DELAY_MIN_MS
        t = (self.diff_factor - 1.0) / (Data.DIFF_MAX - 1.0)
        t = max(0.0, min(1.0, t))
        # Curva acelerada: desde dificultades bajas el spawn ya se acelera,
        # y al acercarse al maximo llega al minimo definido.
        t = t ** 0.65
        span = Data.RESPAWN_DELAY_START_MS - Data.RESPAWN_DELAY_MIN_MS
        delay = int(Data.RESPAWN_DELAY_START_MS - (span * t))
        if self.infernal_mode:
            delay = int(delay * 0.82)
        return max(Data.RESPAWN_DELAY_MIN_MS, delay)

    def queue_respawn(self, enemy_type):
        if enemy_type not in self.pending_respawns:
            return
        self.pending_respawns[enemy_type] += 1

    def get_diff_progress(self):
        if Data.DIFF_MAX <= 1.0:
            return 1.0
        t = (self.diff_factor - 1.0) / (Data.DIFF_MAX - 1.0)
        return max(0.0, min(1.0, t))

    def get_phase_state(self):
        if self.infernal_mode:
            return "infernal"
        if self.diff_factor >= Data.DIFF_MAX:
            return "apex"
        if self.diff_factor >= 6.0:
            return "late"
        if self.diff_factor >= Data.ELITE_MIN_DIFF:
            return "mid"
        return "early"

    def get_spawn_budget_for_phase(self, phase=None):
        p = phase or self.get_phase_state()
        return {
            "early": 1,
            "mid": 1,
            "late": 2,
            "apex": 2,
            "infernal": 3
        }.get(p, 1)

    def sanitize_pending_respawns(self):
        fixes = 0
        if not isinstance(self.pending_respawns, dict):
            self.pending_respawns = {"normal": 0, "elite": 0, "boss": 0}
            self.telemetry["validator_corrections"]["pending_non_negative"] += 1
            return
        for key in ("normal", "elite", "boss"):
            raw = self.pending_respawns.get(key, 0)
            try:
                val = int(raw)
            except (ValueError, TypeError):
                val = 0
                fixes += 1
            if val < 0:
                val = 0
                fixes += 1
            self.pending_respawns[key] = val
        for key in list(self.pending_respawns.keys()):
            if key not in ("normal", "elite", "boss"):
                del self.pending_respawns[key]
                fixes += 1
        if fixes > 0:
            self.telemetry["validator_corrections"]["pending_non_negative"] += fixes

    def validate_dynamic_caps(self, caps=None):
        caps = caps if isinstance(caps, dict) else self.get_dynamic_spawn_caps()
        fixed = {
            "normal": int(max(0, caps.get("normal", 0))),
            "elite": int(max(0, caps.get("elite", 0))),
            "boss": int(max(0, caps.get("boss", 0)))
        }
        fixed["normal"] = min(Data.MAX_NORMAL_ENEMIES, fixed["normal"])
        fixed["elite"] = min(Data.MAX_ELITE_ENEMIES, fixed["elite"])
        fixed["boss"] = min(Data.MAX_BOSS_ENEMIES, fixed["boss"])
        if not self.infernal_mode:
            fixed["boss"] = min(1, fixed["boss"])
        if self.get_phase_state() in ("early", "mid", "late"):
            fixed["boss"] = 0
        if fixed["elite"] > fixed["normal"]:
            fixed["elite"] = fixed["normal"]
        if fixed != caps:
            self.telemetry["validator_corrections"]["caps_sanitized"] += 1
        return fixed

    def validate_runtime_state(self):
        self.sanitize_pending_respawns()
        final_bosses = [
            e for e in self.enemies
            if getattr(e, "enemy_type", "normal") == "boss" and getattr(e, "boss_kind", "minor") == "final"
        ]
        if len(final_bosses) > 1:
            for extra in final_bosses[1:]:
                if extra in self.enemies:
                    self.enemies.remove(extra)
            self.telemetry["validator_corrections"]["final_boss_unique"] += (len(final_bosses) - 1)
        self.boss_alive = any(getattr(e, "enemy_type", "normal") == "boss" for e in self.enemies)
        self.adjust_dynamic_particle_limit()
        return self.validate_dynamic_caps()

    def adjust_dynamic_particle_limit(self):
        if self.admin_ignore_runtime_limits:
            self.entity_frame_limits["particles"] = 999999
            return
        base = Data.MAX_ACTIVE_PARTICLES_PER_FRAME
        pressure = len(self.enemies) + int(len(self.projectiles) * 0.65)
        if pressure >= 260:
            dyn = int(base * 0.60)
        elif pressure >= 190:
            dyn = int(base * 0.74)
        elif pressure >= 130:
            dyn = int(base * 0.86)
        else:
            dyn = base
        self.entity_frame_limits["particles"] = max(90, min(base, dyn))

    def get_entities_for_frame(self, key, items, limit):
        if self.admin_ignore_runtime_limits:
            return items[:]
        if limit <= 0 or len(items) <= limit:
            return items[:]
        cursor = int(self.frame_entity_cursor.get(key, 0)) % len(items)
        end = cursor + limit
        if end <= len(items):
            active = items[cursor:end]
        else:
            active = items[cursor:] + items[:(end - len(items))]
        self.frame_entity_cursor[key] = (cursor + limit) % len(items)
        self.telemetry["entity_limit_hits"][key] += 1
        return active

    def update_local_telemetry(self, dt):
        if dt <= 0:
            return
        fps = 1000.0 / dt
        self.telemetry["fps_sum"] += fps
        self.telemetry["fps_samples"] += 1
        entities = self.telemetry["max_entities"]
        entities["enemies"] = max(entities["enemies"], len(self.enemies))
        entities["projectiles"] = max(entities["projectiles"], len(self.projectiles))
        entities["particles"] = max(entities["particles"], len(self.particles))
        entities["drops"] = max(entities["drops"], len(self.drops))
        entities["total"] = max(entities["total"], len(self.enemies) + len(self.projectiles) + len(self.particles) + len(self.drops))
        phase = self.get_phase_state()
        self.telemetry["phase_time_ms"][phase] = self.telemetry["phase_time_ms"].get(phase, 0) + int(dt)

    def get_spawn_power_for_type(self, enemy_type):
        t = self.get_diff_progress()
        base_diff = max(1.0, min(Data.DIFF_MAX, self.diff_factor))
        # Ajuste de balance base: menos picos de daño/vida en variantes rápidas.
        hp_mult = 1.0 + (t * Data.ENEMY_SPAWN_HP_SCALING * base_diff * 0.82)
        dmg_mult = 1.0 + (t * Data.ENEMY_SPAWN_DAMAGE_SCALING * base_diff * 0.78)
        if enemy_type == "elite":
            hp_mult *= 1.12
            dmg_mult *= 1.10
        elif enemy_type == "boss":
            hp_mult *= 1.20
            dmg_mult *= 1.14
        power = max(hp_mult, dmg_mult)
        if self.infernal_mode:
            power *= Data.INFERNAL_POWER_MULT
            return min(power, 7.0)
        caps = {"normal": 2.4, "elite": 3.1, "boss": 4.0}
        return min(power, caps.get(enemy_type, 2.8))

    def get_speed_variant_for_spawn(self, enemy_type):
        t = self.get_diff_progress()
        chance = Data.FAST_VARIANT_BASE_CHANCE + (Data.FAST_VARIANT_MAX_CHANCE - Data.FAST_VARIANT_BASE_CHANCE) * t
        if enemy_type == "elite":
            chance += Data.FAST_VARIANT_ELITE_BONUS
        if enemy_type == "boss":
            chance *= 0.4
        chance = max(0.0, min(0.52, chance))
        rapid = random.random() < chance
        base_speed_mult = 1.0 + (t * Data.ENEMY_SPAWN_SPEED_SCALING * max(1.0, min(Data.DIFF_MAX, self.diff_factor)) * 0.8)
        if self.infernal_mode:
            base_speed_mult *= Data.INFERNAL_SPEED_MULT
        if not rapid:
            return min(base_speed_mult, 2.05 if self.infernal_mode else 1.55), False
        fast_mult = random.uniform(Data.FAST_VARIANT_MIN_MULT, Data.FAST_VARIANT_MAX_MULT)
        speed_mult = base_speed_mult * fast_mult
        speed_cap = 2.35 if self.infernal_mode else 1.82
        return min(speed_mult, speed_cap), True

    def get_dynamic_spawn_caps(self):
        t = self.get_diff_progress()
        phase = self.get_phase_state()
        normal_cap = max(18, min(Data.MAX_NORMAL_ENEMIES, 50 + int(250 * t)))

        elite_cap = 0
        if self.diff_factor >= Data.ELITE_MIN_DIFF:
            elite_cap = min(Data.MAX_ELITE_ENEMIES, 3 + int((self.diff_factor - Data.ELITE_MIN_DIFF) * 10))

        boss_cap = 0
        if self.diff_factor >= Data.DIFF_MAX:
            boss_cap = 1
            if self.infernal_mode:
                boss_cap = min(Data.MAX_BOSS_ENEMIES, 2)

        if self.infernal_mode:
            normal_cap = min(Data.MAX_NORMAL_ENEMIES, int(normal_cap * 1.18))
            elite_cap = min(Data.MAX_ELITE_ENEMIES, max(elite_cap + 5, int(elite_cap * 1.35)))

        if phase == "early":
            normal_cap = int(normal_cap * 0.88)
            elite_cap = 0
            boss_cap = 0
        elif phase == "mid":
            normal_cap = int(normal_cap * 0.98)
            elite_cap = int(elite_cap * 0.85)
            boss_cap = 0
        elif phase == "late":
            normal_cap = int(normal_cap * 1.08)
            elite_cap = int(elite_cap * 1.08)
            boss_cap = 0
        elif phase == "apex":
            normal_cap = int(normal_cap * 1.14)
            elite_cap = int(elite_cap * 1.2)
            boss_cap = min(1, max(1, boss_cap))
        elif phase == "infernal":
            normal_cap = int(normal_cap * 1.22)
            elite_cap = int(elite_cap * 1.3)
            boss_cap = min(Data.MAX_BOSS_ENEMIES, max(1, boss_cap))

        caps = {"normal": normal_cap, "elite": elite_cap, "boss": boss_cap}
        return self.validate_dynamic_caps(caps)

    def spawn_enemy_of_type(self, enemy_type):
        angle = random.uniform(0, math.pi * 2)
        spawn_radius = 900 if enemy_type == "boss" else 750
        origin = self.get_enemy_spawn_origin_position()
        sx = origin.x + math.cos(angle) * spawn_radius
        sy = origin.y + math.sin(angle) * spawn_radius
        # Cada salto de x1 en dificultad sube una tier de evolucion.
        evo_tier = max(0, int(self.diff_factor) - 1)
        ability = self.roll_special_ability()
        spawn_power = self.get_spawn_power_for_type(enemy_type)
        speed_multiplier, rapid_variant = self.get_speed_variant_for_spawn(enemy_type)
        boss_kind = "minor"
        if enemy_type == "boss":
            self.bosses_spawned += 1
            self.boss_alive = True
            if (not self.final_boss_spawned) and self.diff_factor >= Data.DIFF_MAX:
                boss_kind = "final"
                self.final_boss_spawned = True
            evo_tier += max(0, self.bosses_spawned - 1)
        
        # Logica de Spawner Inteligente (Probabilidades)
        EnemyClass = Enemy
        if enemy_type == "normal":
            r = random.random()
            if r < 0.12:   # 12% Tank
                EnemyClass = TankEnemy
            elif r < 0.28: # 16% Exploder (Total 28%)
                EnemyClass = ExploderEnemy
        
        # Instanciamos la clase elegida
        new_enemy = EnemyClass(
            sx,
            sy,
            enemy_type=enemy_type, # Pasamos el tipo original para mantener compatibilidad de caps
            evolution_tier=evo_tier,
            special_ability=ability,
            spawn_power=spawn_power,
            speed_multiplier=speed_multiplier,
            rapid_variant=rapid_variant,
            boss_kind=boss_kind
        )
        self.enemies.append(new_enemy)

    def spawn_enemy_at_position(self, enemy_type, world_x, world_y):
        evo_tier = max(0, int(self.diff_factor) - 1)
        ability = self.roll_special_ability()
        spawn_power = self.get_spawn_power_for_type(enemy_type)
        speed_multiplier, rapid_variant = self.get_speed_variant_for_spawn(enemy_type)
        boss_kind = "minor"
        if enemy_type == "boss":
            self.bosses_spawned += 1
            self.boss_alive = True
            if (not self.final_boss_spawned) and self.diff_factor >= Data.DIFF_MAX:
                boss_kind = "final"
                self.final_boss_spawned = True
            evo_tier += max(0, self.bosses_spawned - 1)
        self.enemies.append(
            Enemy(
                world_x,
                world_y,
                enemy_type=enemy_type,
                evolution_tier=evo_tier,
                special_ability=ability,
                spawn_power=spawn_power,
                speed_multiplier=speed_multiplier,
                rapid_variant=rapid_variant,
                boss_kind=boss_kind
            )
        )

    def spawn_admin_enemy_at_cursor(self, enemy_type):
        if self.state not in ("PLAYING", "PAUSED"):
            return
        mx, my = pygame.mouse.get_pos()
        wx = mx + self.camera_offset.x + random.uniform(-40, 40)
        wy = my + self.camera_offset.y + random.uniform(-40, 40)
        self.spawn_enemy_at_position(enemy_type, wx, wy)

    def get_primary_admin_npc(self):
        return self.admin_npcs[0] if self.admin_npcs else None

    def get_enemy_focus_position(self):
        npc = self.get_primary_admin_npc()
        if self.enemy_target_mode == "npc" and npc is not None:
            return pygame.Vector2(npc.pos)
        if self.clone_pos is not None:
            return pygame.Vector2(self.clone_pos)
        return pygame.Vector2(self.player.pos)

    def get_enemy_spawn_origin_position(self):
        npc = self.get_primary_admin_npc()
        if self.enemy_spawn_origin == "npc" and npc is not None:
            return pygame.Vector2(npc.pos)
        return pygame.Vector2(self.player.pos)

    def get_closest_enemy_from(self, pos, max_range=Data.DETECTION_RANGE):
        origin = pygame.Vector2(pos)
        valid = [e for e in self.enemies if origin.distance_to(e.pos) <= max_range]
        return min(valid, key=lambda e: origin.distance_to(e.pos)) if valid else None

    def is_player_invulnerable(self):
        return self.admin_mode and (self.admin_god_mode or self.creative_mode)

    def draw_admin_panel(self):
        if not self.admin_mode:
            return
        panel = pygame.Surface((420, 188), pygame.SRCALPHA)
        panel.fill((8, 12, 18, 190))
        pygame.draw.rect(panel, (255, 255, 255, 40), (0, 0, 420, 188), 2)
        avg_fps = self.clock.get_fps()
        normal_alive, elite_alive, boss_alive = self.get_enemy_type_counts()
        lines = [
            "ADMIN MODE [ON]",
            f"FPS: {avg_fps:.1f}",
            f"Player XY: ({self.player.pos.x:.1f}, {self.player.pos.y:.1f})",
            f"HP: {self.player.hp:.1f}/{Data.PLAYER_MAX_HP}  Mana: {self.player.energy}/{self.player.max_energy}",
            f"Enemies N/E/B: {normal_alive}/{elite_alive}/{boss_alive}  Total: {len(self.enemies)}",
            f"Diff: x{self.diff_factor:.2f}  Infernal: {'yes' if self.infernal_mode else 'no'}  NPCs: {len(self.admin_npcs)}",
            f"God {'ON' if self.admin_god_mode else 'off'} | Creative {'ON' if self.creative_mode else 'off'} | NoShoot {'ON' if self.admin_disable_player_shoot else 'off'}",
            f"NpcFree {'ON' if self.admin_npc_free_mode else 'off'} | NpcShoot {'ON' if self.admin_npc_shoot_mode else 'off'} | Target {self.enemy_target_mode} | Spawn {self.enemy_spawn_origin}",
            "Ctrl+T console | /help para comandos"
        ]
        for i, line in enumerate(lines):
            color = (245, 245, 245) if i > 0 else (255, 210, 70)
            txt = self.font.render(line, True, color)
            panel.blit(txt, (12, 10 + i * 21))
        self.screen.blit(panel, (Data.WIDTH - panel.get_width() - 14, 12))

    def log_console(self, text):
        self.console_log.append(str(text))
        if len(self.console_log) > 7:
            self.console_log = self.console_log[-7:]

    def open_console(self):
        if not self.admin_mode:
            return
        self.is_console_open = True
        self.console_input = ""
        if self.state == "PLAYING":
            self.state = "PAUSED"
            self.console_forced_pause = True
        self.log_console("Console abierta. Usa /help.")

    def close_console(self):
        self.is_console_open = False
        self.console_input = ""
        if self.console_forced_pause and self.state == "PAUSED":
            self.state = "PLAYING"
        self.console_forced_pause = False

    def toggle_console(self):
        if self.is_console_open:
            self.close_console()
        else:
            self.open_console()

    def get_spawn_type_alias(self, raw):
        token = str(raw).strip().lower()
        alias = {
            "n": "normal",
            "normal": "normal",
            "e": "elite",
            "elite": "elite",
            "b": "boss",
            "boss": "boss"
        }
        return alias.get(token, None)

    def spawn_admin_npc(self):
        npc = AdminNPC(self.player)
        self.admin_npcs.append(npc)
        return npc

    def admin_boost_ability(self, ability_name, amount):
        uid = str(ability_name).strip().lower()
        if uid not in self.player.skill_levels:
            return False
        amount = max(1, int(amount))
        for _ in range(amount):
            self.player.skill_levels[uid] = self.player.skill_levels.get(uid, 0) + 1
            lvl = self.player.skill_levels[uid]
            if uid == "speed":
                self.player.base_speed += 0.45 + (0.15 * lvl)
            elif uid == "damage":
                self.player.base_damage += 12 + (4 * lvl)
            elif uid == "rate":
                self.player.base_fire_rate = max(70, self.player.base_fire_rate - (30 + (4 * lvl)))
            elif uid == "shield":
                self.player.buffs["shield"] = 7000 + (900 * lvl)
            elif uid == "haste":
                self.player.buffs["haste"] = 5200 + (800 * lvl)
            elif uid == "multishot":
                self.player.buffs["multishot"] = 9000 + (1200 * lvl)
            elif uid == "orbitals":
                self.player.buffs["orbitals"] = 10000 + (1200 * lvl)
            elif uid == "heal":
                self.player.hp = min(Data.PLAYER_MAX_HP, self.player.hp + (35 + 12 * lvl))
            elif uid == "ink":
                self.player.buffs["ink_trail"] = 9000 + (1200 * lvl)
            elif uid == "confetti":
                self.player.buffs["confetti"] = 10000 + (1300 * lvl)
            elif uid == "mana_magnet":
                self.player.upgrades["mana_magnet"] = True
                self.player.pickup_radius = 100 + (20 * (lvl - 1))
            elif uid == "magic_bounce":
                self.player.upgrades["magic_bounce"] = True
            elif uid == "piercing":
                self.player.upgrades["piercing"] = True
            elif uid == "dash":
                self.player.upgrades["dash"] = True
            elif uid == "vampirism":
                self.player.upgrades["vampirism"] = True
            elif uid == "rubber_body":
                self.player.upgrades["rubber_body"] = True
                self.player.damage_reduction = min(0.6, 0.12 + (0.04 * lvl))
            elif uid == "crit_mastery":
                self.player.upgrades["crit_mastery"] = True
            elif uid == "second_wind":
                self.player.upgrades["second_wind"] = True
            elif uid == "clone":
                self.player.upgrades["clone"] = True
            elif uid == "giant_unlock":
                self.player.upgrades["giant_unlock"] = True
            elif uid == "freeze_time":
                self.player.upgrades["freeze_time"] = True
            elif uid == "boomerang":
                self.player.upgrades["boomerang"] = True
            elif uid == "shockwave":
                self.player.upgrades["shockwave"] = True
            elif uid == "adrenaline_rush":
                self.player.upgrades["adrenaline_rush"] = True
                self.player.buffs["adrenaline"] = self.get_adrenaline_duration_ms(lvl)
            elif uid == "flame_ring":
                self.player.buffs["flame_ring"] = self.get_flame_ring_duration_ms(lvl)
            elif uid == "arcane_volley":
                self.player.buffs["arcane_volley"] = self.get_arcane_volley_duration_ms(lvl)
            elif uid == "storm_sparks":
                self.player.buffs["storm_sparks"] = self.get_storm_sparks_duration_ms(lvl)
            elif uid == "blade_dance":
                self.player.buffs["blade_dance"] = self.get_blade_dance_duration_ms(lvl)
        return True

    def execute_console_command(self, raw_cmd):
        logger.warning(f"COMANDO ADMIN EJECUTADO: {raw_cmd}")
        text = str(raw_cmd).strip()
        if not text:
            return
        self.log_console(f"> {text}")
        if text in ("/exit", "/close"):
            self.close_console()
            return
        if text in ("/help", "/?"):
            self.log_console("Cmds: /spawn n|e|b [n], /spawn npc [n], /mode creative|normal, /ability <id> [n], /ability <n>, /pause, /play, /god, /noshoot on|off")
            self.log_console("NPC: /npc free on|off, /npc shoot on|off, /npc clear, /npc tp x y")
            self.log_console("AI: /enemytarget player|npc, /spawnorigin player|npc, /limits off|on")
            self.log_console("Extra: /hp n, /mana n, /tp x y, /clear, /killall, /status")
            return
        parts = text.split()
        cmd = parts[0].lower()
        args = parts[1:]
        try:
            if cmd == "/spawn":
                if not args:
                    self.log_console("Uso: /spawn n|e|b [count] o /spawn npc [count]")
                    return
                kind = args[0].lower()
                count = int(args[1]) if len(args) > 1 and str(args[1]).lstrip("-").isdigit() else 1
                count = max(1, min(3000, count))
                if kind == "npc":
                    for _ in range(count):
                        self.spawn_admin_npc()
                    self.log_console(f"NPC creados: {count}")
                    return
                enemy_type = self.get_spawn_type_alias(kind)
                if enemy_type is None:
                    self.log_console("Tipo invalido. Usa n/e/b o normal/elite/boss")
                    return
                for _ in range(count):
                    self.spawn_admin_enemy_at_cursor(enemy_type)
                self.log_console(f"Spawn {enemy_type}: {count}")
            elif cmd == "/mode":
                if not args:
                    self.log_console("Uso: /mode creative|normal")
                    return
                mode = args[0].lower()
                if mode == "creative":
                    self.creative_mode = True
                    self.log_console("Creative ON")
                elif mode in ("normal", "survival"):
                    self.creative_mode = False
                    self.log_console("Creative OFF")
                else:
                    self.log_console("Modo invalido")
            elif cmd == "/noshoot":
                val = args[0].lower() if args else "toggle"
                if val == "toggle":
                    self.admin_disable_player_shoot = not self.admin_disable_player_shoot
                else:
                    self.admin_disable_player_shoot = val in ("1", "on", "true", "yes")
                self.log_console(f"NoShoot {'ON' if self.admin_disable_player_shoot else 'OFF'}")
            elif cmd == "/npc":
                if not args:
                    self.log_console("Uso: /npc free on|off | /npc shoot on|off | /npc clear | /npc tp x y")
                    return
                sub = args[0].lower()
                if sub == "free":
                    val = args[1].lower() if len(args) > 1 else "toggle"
                    if val == "toggle":
                        self.admin_npc_free_mode = not self.admin_npc_free_mode
                    else:
                        self.admin_npc_free_mode = val in ("1", "on", "true", "yes")
                    self.log_console(f"NpcFree {'ON' if self.admin_npc_free_mode else 'OFF'}")
                elif sub == "shoot":
                    val = args[1].lower() if len(args) > 1 else "toggle"
                    if val == "toggle":
                        self.admin_npc_shoot_mode = not self.admin_npc_shoot_mode
                    else:
                        self.admin_npc_shoot_mode = val in ("1", "on", "true", "yes")
                    self.log_console(f"NpcShoot {'ON' if self.admin_npc_shoot_mode else 'OFF'}")
                elif sub == "clear":
                    removed = len(self.admin_npcs)
                    self.admin_npcs.clear()
                    self.log_console(f"NPC eliminados: {removed}")
                elif sub == "tp":
                    if len(args) < 3:
                        self.log_console("Uso: /npc tp <x> <y>")
                        return
                    npc = self.get_primary_admin_npc()
                    if npc is None:
                        self.log_console("No hay NPC")
                        return
                    npc.pos.x = float(args[1])
                    npc.pos.y = float(args[2])
                    npc.update_rect()
                    self.log_console(f"NPC TP ({npc.pos.x:.1f}, {npc.pos.y:.1f})")
                else:
                    self.log_console("Subcomando npc invalido")
            elif cmd in ("/enemytarget", "/target"):
                if not args:
                    self.log_console("Uso: /enemytarget player|npc")
                    return
                mode = args[0].lower()
                if mode in ("player", "npc"):
                    self.enemy_target_mode = mode
                    self.log_console(f"Enemy target = {mode}")
                else:
                    self.log_console("Valor invalido")
            elif cmd in ("/spawnorigin", "/spawnfrom"):
                if not args:
                    self.log_console("Uso: /spawnorigin player|npc")
                    return
                mode = args[0].lower()
                if mode in ("player", "npc"):
                    self.enemy_spawn_origin = mode
                    self.log_console(f"Spawn origin = {mode}")
                else:
                    self.log_console("Valor invalido")
            elif cmd in ("/limits", "/unlimit"):
                val = args[0].lower() if args else "toggle"
                if val == "toggle":
                    self.admin_ignore_runtime_limits = not self.admin_ignore_runtime_limits
                elif val in ("off", "0", "false", "no"):
                    self.admin_ignore_runtime_limits = True
                elif val in ("on", "1", "true", "yes"):
                    self.admin_ignore_runtime_limits = False
                else:
                    self.log_console("Uso: /limits off|on")
                    return
                state = "OFF (sin limites)" if self.admin_ignore_runtime_limits else "ON (limites activos)"
                self.log_console(f"Entity limits {state}")
            elif cmd in ("/ability", "/avility", "/abilty"):
                if not args:
                    self.log_console("Uso: /ability <id> [n] o /ability <n>")
                    return
                if str(args[0]).lstrip("-").isdigit():
                    amount = max(1, int(args[0]))
                    for uid in self.player.skill_levels.keys():
                        self.admin_boost_ability(uid, amount)
                    self.log_console(f"Todas las habilidades +{amount}")
                else:
                    uid = args[0].lower()
                    amount = int(args[1]) if len(args) > 1 and str(args[1]).lstrip("-").isdigit() else 1
                    if self.admin_boost_ability(uid, amount):
                        self.log_console(f"Habilidad {uid} +{amount}")
                    else:
                        self.log_console(f"Habilidad desconocida: {uid}")
            elif cmd == "/pause":
                self.state = "PAUSED"
                self.console_forced_pause = False
                self.log_console("Juego en pausa")
            elif cmd == "/play":
                self.state = "PLAYING"
                self.console_forced_pause = False
                self.log_console("Juego reanudado")
                self.close_console()
            elif cmd == "/god":
                self.admin_god_mode = not self.admin_god_mode
                self.log_console(f"God mode {'ON' if self.admin_god_mode else 'OFF'}")
            elif cmd == "/hp":
                if not args:
                    self.log_console("Uso: /hp <valor>")
                    return
                self.player.hp = max(1.0, min(float(args[0]), float(Data.PLAYER_MAX_HP)))
                self.log_console(f"HP = {self.player.hp:.1f}")
            elif cmd == "/mana":
                if not args:
                    self.log_console("Uso: /mana <valor>")
                    return
                self.player.energy = max(0, min(int(float(args[0])), int(self.player.max_energy)))
                self.log_console(f"Mana = {self.player.energy}")
            elif cmd == "/tp":
                if len(args) < 2:
                    self.log_console("Uso: /tp <x> <y>")
                    return
                self.player.pos.x = float(args[0])
                self.player.pos.y = float(args[1])
                self.player.update_rect()
                self.log_console(f"TP ({self.player.pos.x:.1f}, {self.player.pos.y:.1f})")
            elif cmd in ("/clear", "/killall"):
                removed = len(self.enemies)
                self.enemies.clear()
                self.pending_respawns = {"normal": 0, "elite": 0, "boss": 0}
                self.log_console(f"Enemigos eliminados: {removed}")
            elif cmd == "/status":
                self.log_console(
                    f"HP {self.player.hp:.1f} | Mana {self.player.energy}/{self.player.max_energy} | Enemies {len(self.enemies)} | NPC {len(self.admin_npcs)} | Creative {'ON' if self.creative_mode else 'OFF'} | NoShoot {'ON' if self.admin_disable_player_shoot else 'OFF'}"
                )
                self.log_console(
                    f"NpcFree {'ON' if self.admin_npc_free_mode else 'OFF'} | NpcShoot {'ON' if self.admin_npc_shoot_mode else 'OFF'} | EnemyTarget {self.enemy_target_mode} | SpawnOrigin {self.enemy_spawn_origin} | LimitsOff {'YES' if self.admin_ignore_runtime_limits else 'NO'}"
                )
            else:
                self.log_console(f"Comando no reconocido: {cmd}")
        except (ValueError, TypeError):
            self.log_console("Parametros invalidos")

    def draw_console(self):
        if not self.is_console_open:
            return
        height = 148
        overlay = pygame.Surface((Data.WIDTH, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 215))
        self.screen.blit(overlay, (0, Data.HEIGHT - height))
        pygame.draw.rect(self.screen, Data.COLOR_OUTLINE, (0, Data.HEIGHT - height, Data.WIDTH, height), 2)

        log_start = Data.HEIGHT - height + 8
        for i, msg in enumerate(self.console_log[-5:]):
            txt = self.font.render(msg, True, (200, 220, 200))
            self.screen.blit(txt, (10, log_start + i * 22))
        caret = "_" if (pygame.time.get_ticks() // 350) % 2 == 0 else ""
        entry = self.font.render(f"> {self.console_input}{caret}", True, (255, 236, 120))
        self.screen.blit(entry, (10, Data.HEIGHT - 30))

    def process_enemy_respawns(self):
        self.sanitize_pending_respawns()
        normal_alive, elite_alive, boss_alive = self.get_enemy_type_counts()
        caps = self.validate_dynamic_caps(self.get_dynamic_spawn_caps())
        alive = {"normal": normal_alive, "elite": elite_alive, "boss": boss_alive}
        spawned_any = False

        for enemy_type in ("normal", "elite", "boss"):
            cap = caps[enemy_type]
            if cap <= 0:
                self.pending_respawns[enemy_type] = 0
                continue
            deficit = max(0, cap - alive[enemy_type])
            if deficit > 0:
                self.pending_respawns[enemy_type] = max(self.pending_respawns.get(enemy_type, 0), deficit)
            if alive[enemy_type] >= cap:
                continue
            if self.pending_respawns.get(enemy_type, 0) <= 0:
                continue

        budget = self.get_spawn_budget_for_phase()
        for _ in range(max(1, int(budget))):
            spawned = False
            for enemy_type in ("boss", "elite", "normal"):
                cap = caps[enemy_type]
                if cap <= 0:
                    continue
                if alive[enemy_type] >= cap:
                    continue
                if self.pending_respawns.get(enemy_type, 0) <= 0:
                    continue
                self.spawn_enemy_of_type(enemy_type)
                self.pending_respawns[enemy_type] = max(0, self.pending_respawns[enemy_type] - 1)
                alive[enemy_type] += 1
                spawned = True
                spawned_any = True
                break
            if not spawned:
                break
        return spawned_any

    def update_projectile_collisions(self, dt):
        """Actualiza proyectiles y resuelve impactos contra enemigos."""
        active_projectiles = self.get_entities_for_frame("projectiles", self.projectiles, self.entity_frame_limits["projectiles"])
        collision_targets = self.get_entities_for_frame("enemy_collisions", self.enemies, self.entity_frame_limits["enemy_collisions"])
        for p in active_projectiles:
            if p not in self.projectiles:
                continue
            p.update(dt, self.player.rect.center)
            if p.boomerang and p.returning and p.rect.colliderect(self.player.rect):
                self.projectiles.remove(p)
                continue
            if p.pos.distance_to(self.player.pos) > 1500 and not p.boomerang:
                self.projectiles.remove(p)
                continue
            if p.bounces_left > 0:
                dp = p.pos - self.camera_offset
                bounced = False
                if dp.x < 0 or dp.x > Data.WIDTH:
                    p.vel.x *= -1
                    bounced = True
                if dp.y < 0 or dp.y > Data.HEIGHT:
                    p.vel.y *= -1
                    bounced = True
                if bounced:
                    p.bounces_left -= 1
            for e in collision_targets:
                if e not in self.enemies:
                    continue
                if not p.rect.colliderect(e.rect):
                    continue
                eid = id(e)
                if eid in p.hit_memory:
                    continue
                p.hit_memory[eid] = 140

                hit_damage = p.damage
                if self.player.upgrades["crit_mastery"]:
                    crit_lvl = max(1, self.player.skill_levels.get("crit_mastery", 1))
                    crit_chance = min(0.55, 0.08 + (0.04 * crit_lvl))
                    if random.random() < crit_chance:
                        crit_mult = 1.6 + (0.15 * crit_lvl)
                        hit_damage *= crit_mult
                        self.emit_particle(e.rect.centerx, e.rect.centery, (255, 245, 140))
                e.hp -= hit_damage
                slow_duration = int(p.ink_effects.get("slow_duration_ms", 0))
                if slow_duration > 0:
                    e.slow_timer = max(e.slow_timer, slow_duration)
                burn_duration = int(p.ink_effects.get("burn_duration_ms", 0))
                burn_ratio = float(p.ink_effects.get("burn_dps_ratio", 0.0))
                if burn_duration > 0 and burn_ratio > 0:
                    e.apply_burn(hit_damage * burn_ratio, burn_duration)
                logger.info(f"¡Impacto! Enemigo {e.enemy_type} recibió {hit_damage:.1f} de daño. HP restante: {e.hp:.1f}")
                if p.vel.length() > 0:
                    e.pos += p.vel.normalize() * Data.ENEMY_KNOCKBACK * float(p.ink_effects.get("knockback_mult", 1.0))
                    e.update_rect()
                self.session_stats["damage_dealt"] += hit_damage
                self.session_stats["shots_hit"] += 1
                self.play_enemy_hit_sfx()
                self.emit_ink_splash(e.rect.centerx, e.rect.centery, p.color, count=4)
                if e.hp <= 0:
                    self.on_enemy_killed(e)
                if p.boomerang:
                    continue
                p.pierce_left -= 1
                if p.pierce_left <= 0:
                    if p.bounces_left > 0:
                        p.vel = -p.vel
                        p.bounces_left -= 1
                        p.pierce_left = 1
                    elif p in self.projectiles:
                        self.projectiles.remove(p)
                    break

    def update_enemy_collisions(self, dt):
        """Actualiza enemigos y resuelve dato por contacto/habilidades."""
        active_enemies = self.get_entities_for_frame("enemies", self.enemies, self.entity_frame_limits["enemies"])
        for e in active_enemies:
            if e not in self.enemies:
                continue
            e.apply_evolution(max(0, int(self.diff_factor) - 1))
            if self.freeze_timer > 0:
                e.update(self.player.pos, speed_factor=0, frozen=True, dt=dt)
            elif self.creative_mode:
                e.update(e.pos, speed_factor=0, frozen=True, dt=dt)
            else:
                speed_factor = 1.0
                for puddle in self.ink_puddles:
                    if e.pos.distance_to(puddle["pos"]) < puddle["radius"]:
                        ink_lvl = self.player.skill_levels.get("ink", 1)
                        speed_factor = min(speed_factor, max(0.2, 0.55 - (0.05 * ink_lvl)))
                        ink_dmg = (0.03 + (0.015 * ink_lvl)) * dt
                        e.hp -= ink_dmg
                        self.session_stats["damage_dealt"] += ink_dmg
                        if e.hp <= 0:
                            self.on_enemy_killed(e)
                            break
                if e not in self.enemies:
                    continue
                target = self.get_enemy_focus_position()
                e.update(target, speed_factor=speed_factor, frozen=False, dt=dt)
            if e in self.enemies and e.hp <= 0:
                self.on_enemy_killed(e)
                continue

            if e in self.enemies and e.special_ability == "orbital":
                target_npc = self.get_primary_admin_npc() if self.enemy_target_mode == "npc" else None
                if target_npc is not None and target_npc.pos.distance_to(e.pos) <= max(95, e.rect.w * 1.4):
                    target_npc.hp -= max(0.4, e.damage * 0.35)
                    if target_npc.hp <= 0 and target_npc in self.admin_npcs:
                        self.admin_npcs.remove(target_npc)
                elif self.enemy_target_mode != "npc" and self.player.pos.distance_to(e.pos) <= max(95, e.rect.w * 1.4):
                    if self.player.buffs["shield"] <= 0 and self.player.buffs["dash_invuln"] <= 0 and self.player_hit_cooldown <= 0 and (not self.is_player_invulnerable()):
                        extra = max(0.4, e.damage * 0.35)
                        self.player.hp -= extra
                        logger.warning(f"¡Jugador herido! HP restante: {self.player.hp:.1f}")
                        self.session_stats["damage_taken"] += extra
                        self.player_hit_cooldown = Data.PLAYER_HIT_COOLDOWN_MS
                        self.player.second_wind_lock = max(self.player.second_wind_lock, 2200)
                        self.play_damage_sfx()
                        self.trigger_shake(12, 15)

            target_npc = self.get_primary_admin_npc() if self.enemy_target_mode == "npc" else None
            if e in self.enemies and target_npc is not None and e.rect.colliderect(target_npc.rect):
                target_npc.hp -= e.damage * 0.8
                if target_npc.hp <= 0 and target_npc in self.admin_npcs:
                    self.admin_npcs.remove(target_npc)
            elif self.enemy_target_mode != "npc" and e in self.enemies and e.rect.colliderect(self.player.rect):
                if self.player.active_powerup == "SHIELD":
                    self.player.powerup_timer = 0
                    self.player.active_powerup = None
                    self.trigger_shake(15, 15)
                    continue
                if self.player.buffs["shield"] <= 0 and self.player.buffs["dash_invuln"] <= 0 and self.player_hit_cooldown <= 0 and (not self.is_player_invulnerable()):
                    damage = e.damage * (1.0 - self.player.damage_reduction)
                    self.player.hp -= damage
                    logger.warning(f"¡Jugador herido! HP restante: {self.player.hp:.1f}")
                    self.session_stats["damage_taken"] += damage
                    self.player_hit_cooldown = Data.PLAYER_HIT_COOLDOWN_MS
                    self.player.second_wind_lock = max(self.player.second_wind_lock, 2200)
                    self.play_damage_sfx()
                    self.trigger_shake(12, 15)

    def update(self):
        if self.state != "PLAYING":
            return
        dt = min(self.clock.get_time(), 50)
        self.video_last_dt = dt
        self.session_elapsed_ms += dt
        self.kill_chain_count = 0

        for key in self.player.buffs:
            if self.player.buffs[key] > 0:
                self.player.buffs[key] = max(0, self.player.buffs[key] - dt)

        if self.player.powerup_timer > 0:
            self.player.powerup_timer -= dt
            if self.player.powerup_timer <= 0:
                self.player.active_powerup = None

        for p_up in self.powerups[:]:
            p_up.update(dt)
            if p_up.lifetime <= 0:
                self.powerups.remove(p_up)
            elif self.player.rect.colliderect(p_up.rect):
                self.player.apply_powerup(p_up.type)
                self.powerups.remove(p_up)

        if self.combo_timer > 0:
            self.combo_timer -= dt
        else:
            self.combo_multiplier = 1.0

        self.player.dash_cooldown = max(0, self.player.dash_cooldown - dt)
        self.player.clone_cooldown = max(0, self.player.clone_cooldown - dt)
        self.player.freeze_cooldown = max(0, self.player.freeze_cooldown - dt)
        self.player.boomerang_cooldown = max(0, self.player.boomerang_cooldown - dt)
        self.player.giant_cooldown = max(0, self.player.giant_cooldown - dt)
        self.player.shockwave_cooldown = max(0, self.player.shockwave_cooldown - dt)
        self.player.adrenaline_cooldown = max(0, self.player.adrenaline_cooldown - dt)
        self.player.second_wind_lock = max(0, self.player.second_wind_lock - dt)
        self.update_shake()
        self.audio.update(dt)
        self.clone_timer = max(0, self.clone_timer - dt)
        self.freeze_timer = max(0, self.freeze_timer - dt)
        self.player_hit_cooldown = max(0, self.player_hit_cooldown - dt)
        if self.clone_timer <= 0:
            self.clone_pos = None

        if self.storage.has_session():
            self.storage_tick_accum += dt
            if self.storage_tick_accum >= 2000:
                self.storage_tick_accum = 0
                self.storage.write_world_state(self)
                self.storage.write_skill_files(self.player)

        keys = pygame.key.get_pressed()
        self.player.move(keys)
        self.player.set_giant_form(self.player.buffs["giant"] > 0)
        if self.player.buffs["ink_trail"] > 0:
            self.walk_ink_timer += dt
            if self.walk_ink_timer > 180:
                self.walk_ink_timer = 0
                self.draw_ink_splat(self.player.pos, (Data.COLOR_PLAYER[0], Data.COLOR_PLAYER[1], Data.COLOR_PLAYER[2], 100), 5)
        if self.player.upgrades["second_wind"] and self.player.hp < Data.PLAYER_MAX_HP:
            if self.player.second_wind_lock <= 0:
                sw_lvl = max(1, self.player.skill_levels.get("second_wind", 1))
                regen_interval = max(350, 1250 - (90 * (sw_lvl - 1)))
                self.player.second_wind_tick += dt
                while self.player.second_wind_tick >= regen_interval:
                    self.player.second_wind_tick -= regen_interval
                    self.player.hp = min(Data.PLAYER_MAX_HP, self.player.hp + (0.8 + 0.45 * sw_lvl))
            else:
                self.player.second_wind_tick = 0
        else:
            self.player.second_wind_tick = 0
        ink_lvl = self.player.skill_levels.get("ink", 0)
        ink_spawn = min(0.85, 0.35 + (0.08 * max(0, ink_lvl - 1)))
        if self.player.buffs["ink_trail"] > 0 and random.random() < ink_spawn:
            self.ink_puddles.append({"pos": pygame.Vector2(self.player.rect.center), "radius": 46 + (8 * max(1, ink_lvl)), "time": 2200 + (220 * ink_lvl)})
        for puddle in self.ink_puddles[:]:
            puddle["time"] -= dt
            if puddle["time"] <= 0:
                self.ink_puddles.remove(puddle)

        target_cam = self.player.pos - pygame.Vector2(Data.WIDTH // 2, Data.HEIGHT // 2)
        self.camera_offset += (target_cam - self.camera_offset) * 0.08

        base_diff = 1.0 + (self.session_elapsed_ms / Data.DIFF_TIME_SCALE_MS) + max(0, self.player.level - 1) * Data.DIFF_LEVEL_SCALE
        if self.infernal_mode:
            self.diff_factor = Data.INFERNAL_DIFF
        else:
            self.diff_factor = min(Data.DIFF_MAX, base_diff)
            if self.diff_factor >= Data.DIFF_MAX:
                self.max_diff_hold_ms += dt
                if self.max_diff_hold_ms >= Data.INFERNAL_UNLOCK_TIME_MS:
                    self.infernal_mode = True
                    self.diff_factor = Data.INFERNAL_DIFF
            else:
                self.max_diff_hold_ms = 0

        spawn_interval = self.get_respawn_delay_ms()
        self.validate_runtime_state()
        self.spawn_timer += dt
        while self.spawn_timer >= spawn_interval:
            self.spawn_timer -= spawn_interval
            self.process_enemy_respawns()

        shoot_interval = self.player.base_fire_rate
        shot_damage = self.player.base_damage
        if self.player.buffs["adrenaline"] > 0:
            ad_lvl = max(1, self.player.skill_levels.get("adrenaline_rush", 1))
            shoot_interval = max(45, int(self.player.base_fire_rate * max(0.45, 0.76 - (0.03 * ad_lvl))))
            shot_damage *= (1.18 + (0.08 * ad_lvl))

        self.fire_timer += dt
        if (not self.admin_disable_player_shoot) and self.fire_timer >= shoot_interval:
            target = self.get_closest_enemy()
            if target:
                self.spawn_player_shot(target.rect.center, shot_damage)
                if self.player.buffs["multishot"] > 0:
                    off_target1 = pygame.Vector2(target.rect.center) + pygame.Vector2(60, 60)
                    off_target2 = pygame.Vector2(target.rect.center) + pygame.Vector2(-60, -60)
                    self.spawn_player_shot(off_target1, shot_damage, (100, 255, 100))
                    self.spawn_player_shot(off_target2, shot_damage, (100, 255, 100))
                self.fire_timer = 0
        elif self.admin_disable_player_shoot:
            self.fire_timer = 0

        if self.admin_npc_shoot_mode and self.admin_npcs:
            self.admin_npc_shoot_timer += dt
            npc_interval = max(90, int(shoot_interval * 1.2))
            while self.admin_npc_shoot_timer >= npc_interval:
                self.admin_npc_shoot_timer -= npc_interval
                for npc in self.admin_npcs:
                    target = self.get_closest_enemy_from(npc.pos, Data.DETECTION_RANGE + 220)
                    if target is None:
                        continue
                    self.spawn_shot_from_origin(npc.rect.center, target.rect.center, shot_damage * 0.85, color=(130, 255, 175), play_sfx=False)
        else:
            self.admin_npc_shoot_timer = 0

        if self.player.buffs["orbitals"] > 0:
            for e in self.enemies[:]:
                orbit_lvl = self.player.skill_levels.get("orbitals", 1)
                if self.player.pos.distance_to(e.pos) < (110 + 6 * orbit_lvl):
                    orb_dmg = 1.1 + (0.4 * orbit_lvl)
                    e.hp -= orb_dmg
                    self.session_stats["damage_dealt"] += orb_dmg
                    self.play_enemy_hit_sfx()
                    if e.hp <= 0:
                        self.on_enemy_killed(e)

        if self.player.buffs["flame_ring"] > 0:
            fr_lvl = max(1, self.player.skill_levels.get("flame_ring", 1))
            fr_radius = 95 + (8 * fr_lvl)
            fr_dmg = (34 + (6 * fr_lvl)) * (dt / 1000.0)
            for e in self.enemies[:]:
                if self.player.pos.distance_to(e.pos) <= fr_radius:
                    e.hp -= fr_dmg
                    self.session_stats["damage_dealt"] += fr_dmg
                    if e.hp <= 0:
                        self.on_enemy_killed(e)

        if self.player.buffs["arcane_volley"] > 0:
            av_lvl = max(1, self.player.skill_levels.get("arcane_volley", 1))
            self.player.arcane_volley_tick += dt
            av_interval = max(260, 780 - (45 * (av_lvl - 1)))
            if self.player.arcane_volley_tick >= av_interval:
                self.player.arcane_volley_tick = 0
                bolts = min(12, 6 + (av_lvl // 2))
                bolt_damage = self.player.base_damage * (0.45 + 0.05 * av_lvl)
                for i in range(bolts):
                    ang = (math.pi * 2 * i) / bolts
                    target = (
                        self.player.rect.centerx + math.cos(ang) * 320,
                        self.player.rect.centery + math.sin(ang) * 320
                    )
                    self.projectiles.append(
                        Projectile(
                            self.player.rect.centerx,
                            self.player.rect.centery,
                            target,
                            bolt_damage,
                            color=(120, 220, 255),
                            size=12,
                            speed=14 + (0.3 * av_lvl),
                            pierce_left=1
                        )
                    )
                self.session_stats["shots_fired"] += bolts
        else:
            self.player.arcane_volley_tick = 0

        if self.player.buffs["storm_sparks"] > 0:
            ss_lvl = max(1, self.player.skill_levels.get("storm_sparks", 1))
            self.player.storm_sparks_tick += dt
            ss_interval = max(300, 1100 - (70 * (ss_lvl - 1)))
            if self.player.storm_sparks_tick >= ss_interval:
                self.player.storm_sparks_tick = 0
                ss_range = 320 + (20 * ss_lvl)
                ss_targets = min(6, 2 + (ss_lvl // 2))
                ss_base = 10 + (6 * ss_lvl)
                near = [e for e in self.enemies if self.player.pos.distance_to(e.pos) <= ss_range]
                near.sort(key=lambda e: self.player.pos.distance_to(e.pos))
                for i, enemy in enumerate(near[:ss_targets]):
                    dmg = ss_base * (0.82 ** i)
                    enemy.hp -= dmg
                    self.session_stats["damage_dealt"] += dmg
                    self.emit_particle(enemy.rect.centerx, enemy.rect.centery, (175, 235, 255))
                    if enemy.hp <= 0:
                        self.on_enemy_killed(enemy)
        else:
            self.player.storm_sparks_tick = 0

        if self.player.buffs["blade_dance"] > 0:
            bd_lvl = max(1, self.player.skill_levels.get("blade_dance", 1))
            self.player.blade_dance_tick += dt
            bd_interval = max(220, 620 - (35 * (bd_lvl - 1)))
            if self.player.blade_dance_tick >= bd_interval:
                self.player.blade_dance_tick = 0
                target = self.get_closest_enemy()
                if target:
                    base_dir = (pygame.Vector2(target.rect.center) - pygame.Vector2(self.player.rect.center))
                else:
                    base_dir = pygame.Vector2(self.player.last_move_dir)
                if base_dir.length() == 0:
                    base_dir = pygame.Vector2(1, 0)
                base_dir = base_dir.normalize()
                base_ang = math.atan2(base_dir.y, base_dir.x)
                fan_damage = self.player.base_damage * (0.38 + 0.04 * bd_lvl)
                for offset_deg in (-16, 0, 16):
                    ang = base_ang + math.radians(offset_deg)
                    fan_target = (
                        self.player.rect.centerx + math.cos(ang) * 360,
                        self.player.rect.centery + math.sin(ang) * 360
                    )
                    self.projectiles.append(
                        Projectile(
                            self.player.rect.centerx,
                            self.player.rect.centery,
                            fan_target,
                            fan_damage,
                            color=(255, 205, 130),
                            size=13,
                            speed=15 + (0.25 * bd_lvl),
                            pierce_left=1
                        )
                    )
                self.session_stats["shots_fired"] += 3
        else:
            self.player.blade_dance_tick = 0

        active_drops = self.get_entities_for_frame("drops", self.drops, self.entity_frame_limits["drops"])
        for d in active_drops:
            if d not in self.drops:
                continue
            d.update()
            if self.player.upgrades["mana_magnet"]:
                magnet_range = max(100, self.player.pickup_radius)
                to_player = pygame.Vector2(self.player.rect.center) - d.pos
                dist = to_player.length()
                if 0 < dist <= magnet_range:
                    frame_scale = dt / (1000 / 60)
                    pull_speed = (4.5 + 0.03 * magnet_range) * frame_scale
                    d.pos += to_player.normalize() * pull_speed
                    d.rect.topleft = (d.pos.x, d.pos.y)
            picked = self.player.rect.colliderect(d.rect)
            if self.player.upgrades["mana_magnet"] and self.player.pos.distance_to(d.pos) <= self.player.pickup_radius:
                picked = True
            if picked:
                self.player.energy += Data.MANA_PER_DROP
                self.session_stats["mana_collected"] += Data.MANA_PER_DROP
                self.drops.remove(d)
                if self.player.energy >= self.player.max_energy:
                    self.player.energy = self.player.max_energy
                    self.generate_upgrades()
                    self.state = "UPGRADE"

        self.update_projectile_collisions(dt)
        self.update_enemy_collisions(dt)

        active_particles = self.get_entities_for_frame("particles", self.particles, self.entity_frame_limits["particles"])
        for pt in active_particles:
            if pt not in self.particles:
                continue
            pt.update()
            if pt.lifetime <= 0:
                self.particles.remove(pt)

        self.update_local_telemetry(dt)
        if self.player.hp <= 0:
            self.player.hp = 0
            self.highlight_saved = False
            self.state = "DEAD"
            self.finalize_session_record("death")
    def spawn_player_shot(self, target, damage, color=Data.COLOR_FIREBALL):
        self.spawn_shot_from_origin(self.player.rect.center, target, damage, color=color, play_sfx=True)

    def spawn_shot_from_origin(self, origin, target, damage, color=Data.COLOR_FIREBALL, play_sfx=True):
        pierce_lvl = self.player.skill_levels.get("piercing", 0)
        bounce_lvl = self.player.skill_levels.get("magic_bounce", 0)
        giant_lvl = self.player.skill_levels.get("giant_unlock", 0)
        pierce = (2 + pierce_lvl) if self.player.upgrades["piercing"] else 1
        bounce = bounce_lvl if self.player.upgrades["magic_bounce"] else 0
        shot_size = (22 + 3 * max(1, giant_lvl)) if self.player.buffs["giant"] > 0 else 16
        ink_type = self.get_current_ink_type()
        ink_profile = self.get_ink_profile(ink_type)
        shot_color = color if color != Data.COLOR_FIREBALL else ink_profile["color"]
        shot_damage = damage * ink_profile["damage_mult"]
        self.projectiles.append(
            Projectile(
                float(origin[0]),
                float(origin[1]),
                target,
                shot_damage,
                color=shot_color,
                size=shot_size,
                pierce_left=pierce,
                bounces_left=bounce,
                ink_type=ink_type,
                ink_effects=ink_profile
            )
        )
        self.session_stats["shots_fired"] += 1
        if play_sfx:
            self.play_shot_sfx()

    def cast_boomerang(self):
        target = self.get_closest_enemy()
        aim = target.rect.center if target else (self.player.rect.centerx + 200, self.player.rect.centery)
        lvl = max(1, self.player.skill_levels.get("boomerang", 1))
        self.projectiles.append(
            Projectile(
                self.player.rect.centerx,
                self.player.rect.centery,
                aim,
                int(self.player.base_damage * (1.5 + 0.3 * lvl)),
                color=(255, 170, 0),
                size=28 + (2 * lvl),
                speed=13 + (0.7 * lvl),
                pierce_left=999,
                boomerang=True
            )
        )
        self.session_stats["shots_fired"] += 1

    def cast_shockwave(self):
        lvl = max(1, self.player.skill_levels.get("shockwave", 1))
        radius = 150 + (16 * lvl)
        damage = 22 + (9 * lvl)
        knockback = 10 + (2.6 * lvl)
        hit_any = False
        for e in self.enemies[:]:
            direction = e.pos - self.player.pos
            dist = direction.length()
            if dist > radius:
                continue
            hit_any = True
            e.hp -= damage
            if dist > 0:
                e.pos += direction.normalize() * knockback
                e.update_rect()
            self.session_stats["damage_dealt"] += damage
            self.emit_particle(e.rect.centerx, e.rect.centery, (120, 230, 255))
            if e.hp <= 0:
                self.on_enemy_killed(e)
        if hit_any:
            self.play_pop_sfx()

    def emit_particle(self, x, y, color):
        if self.admin_ignore_runtime_limits:
            self.particles.append(Particle(x, y, color))
            return
        frame_limit = int(self.entity_frame_limits.get("particles", Data.MAX_ACTIVE_PARTICLES_PER_FRAME))
        hard_cap = max(Data.MAX_ACTIVE_PARTICLES_PER_FRAME, frame_limit * 5)
        if len(self.particles) >= hard_cap:
            overflow = (len(self.particles) - hard_cap) + 1
            if overflow > 0:
                del self.particles[:overflow]
        self.particles.append(Particle(x, y, color))

    def emit_ink_splash(self, x, y, color, count=4):
        for _ in range(max(1, int(count))):
            self.emit_particle(x + random.uniform(-6, 6), y + random.uniform(-6, 6), color)

    def on_enemy_killed(self, enemy):
        if enemy not in self.enemies:
            return
        logger.info(f"Enemigo {enemy.enemy_type} ELIMINADO.")
        
        # Ejecutar logica especifica de muerte (ej: explosion)
        enemy.on_death(self)
        
        self.draw_ink_splat(enemy.pos, enemy.color, 20)
        self.trigger_shake(5, 10)
        enemy_type = getattr(enemy, "enemy_type", "normal")
        self.session_stats["enemies_killed"] += 1
        self.kills_since_boss += 1
        self.kill_chain_count += 1
        self.session_stats["kill_chain_max"] = max(self.session_stats.get("kill_chain_max", 0), self.kill_chain_count)
        if enemy_type == "normal":
            if random.random() < Data.MANA_DROP_CHANCE:
                self.drops.append(ManaDrop(enemy.pos.x, enemy.pos.y))
        else:
            for _ in range(max(1, int(enemy.mana_drop_count))):
                jitter = pygame.Vector2(random.uniform(-28, 28), random.uniform(-28, 28))
                self.drops.append(ManaDrop(enemy.pos.x + jitter.x, enemy.pos.y + jitter.y))
        confetti_lvl = self.player.skill_levels.get("confetti", 0)
        confetti_chance = min(0.75, 0.25 + (0.05 * confetti_lvl))
        confetti_damage = 16 + (7 * max(1, confetti_lvl))
        confetti_radius = 120 + (12 * confetti_lvl)
        if self.player.buffs["confetti"] > 0 and random.random() < confetti_chance:
            for other in self.enemies[:]:
                if other is enemy:
                    continue
                if other.pos.distance_to(enemy.pos) <= confetti_radius:
                    other.hp -= confetti_damage
                    self.play_enemy_hit_sfx()
                    self.emit_particle(other.rect.centerx, other.rect.centery, (255, 255, 80))
                    if other.hp <= 0:
                        self.on_enemy_killed(other)
        self.enemies.remove(enemy)
        if enemy_type == "boss":
            self.boss_alive = any(getattr(e, "enemy_type", "normal") == "boss" for e in self.enemies)
            if getattr(enemy, "boss_kind", "minor") == "final":
                self.final_boss_defeated = True
        self.queue_respawn(enemy_type)
        
        # Sistema de Combo
        self.combo_multiplier += 0.1
        self.combo_timer = Data.COMBO_MAX_TIME
        points = int(enemy.score_value * self.combo_multiplier)
        self.score += points
        
        if self.player.upgrades["vampirism"]:
            vamp_lvl = max(1, self.player.skill_levels.get("vampirism", 1))
            kills_needed = max(3, 10 - (vamp_lvl - 1))
            heal_amount = 3 + (2 * vamp_lvl)
            self.player.kills_for_heal += 1
            if self.player.kills_for_heal >= kills_needed:
                self.player.kills_for_heal = 0
                self.player.hp = min(Data.PLAYER_MAX_HP, self.player.hp + heal_amount)
        
        # Probabilidad de soltar un Power-up
        if random.random() < Data.POWERUP_DROP_CHANCE:
            powerup_type = random.choice(["FIRE", "ICE", "SHIELD"])
            self.powerups.append(PowerUp(enemy.pos, powerup_type))

    def get_closest_enemy(self):
        valid = [e for e in self.enemies if self.player.pos.distance_to(e.pos) <= Data.DETECTION_RANGE]
        return min(valid, key=lambda e: self.player.pos.distance_to(e.pos)) if valid else None

    def draw(self):
        if self.state == "MENU":
            self.screen.fill(Data.COLOR_BG)
            self.draw_grid(self.camera_offset)
            self.draw_main_menu()
            pygame.display.flip()
            return

        render_offset = self.camera_offset - self.shake_offset

        self.screen.fill(Data.COLOR_BG)
        self.draw_grid(render_offset)
        
        # Dibujar rastro de tinta
        self.ink_surface.fill((0, 0, 0, 0))
        for splat in self.ink_trails:
            draw_pos = splat["pos"] - render_offset
            if splat.get("type") == "blob":
                pts = []
                for off in splat["offsets"]:
                    p = draw_pos + off
                    pts.append((int(p.x), int(p.y)))
                if len(pts) >= 3:
                    pygame.draw.polygon(self.ink_surface, splat["rim"], pts)
                    pygame.draw.polygon(self.ink_surface, splat["fill"], pts)
                for drop in splat.get("droplets", ()):
                    dp = draw_pos + drop["offset"]
                    rr = max(2, int(drop["r"]))
                    pygame.draw.circle(self.ink_surface, splat["rim"], (int(dp.x), int(dp.y)), rr + 1)
                    pygame.draw.circle(self.ink_surface, splat["fill"], (int(dp.x), int(dp.y)), rr)
            else:
                pygame.draw.circle(self.ink_surface, splat["fill"], (int(draw_pos.x), int(draw_pos.y)), int(splat["size"]))
        self.screen.blit(self.ink_surface, (0, 0))
        
        for puddle in self.ink_puddles:
            pp = puddle["pos"] - render_offset
            pygame.draw.circle(self.screen, Data.COLOR_OUTLINE, pp, puddle["radius"] + 3, 2)
            pygame.draw.circle(self.screen, (30, 30, 30), pp, puddle["radius"])

        if self.clone_pos is not None:
            cp = self.clone_pos - render_offset
            pygame.draw.rect(self.screen, Data.COLOR_OUTLINE, (cp.x - 20, cp.y - 24, 40, 48), border_radius=9)
            pygame.draw.rect(self.screen, (240, 240, 240), (cp.x - 17, cp.y - 21, 34, 42), border_radius=8)

        for p_up in self.powerups: p_up.draw(self.screen, render_offset, self.font)
        for d in self.drops: d.draw(self.screen, render_offset)
        for e in self.enemies: e.draw(self.screen, render_offset)
        
        # Dibujar orbitales si están activos
        if self.player.buffs["orbitals"] > 0:
            t = pygame.time.get_ticks() / 300
            for i in range(3):
                angle = t + (i * (math.pi * 2 / 3))
                ox = self.player.rect.centerx + math.cos(angle) * 100 - render_offset.x
                oy = self.player.rect.centery + math.sin(angle) * 100 - render_offset.y
                pygame.draw.circle(self.screen, Data.COLOR_OUTLINE, (ox, oy), 12)
                pygame.draw.circle(self.screen, (150, 0, 255), (ox, oy), 9)

        for p in self.projectiles: p.draw(self.screen, render_offset)
        for npc in self.admin_npcs: npc.draw(self.screen, render_offset)
        self.player.draw(self.screen, render_offset)
        
        # Dibujar Texto de Combo (flotante cerca del jugador)
        if self.combo_multiplier > 1.0:
            combo_txt = self.font.render(f"x{self.combo_multiplier:.1f}", True, (255, 255, 0))
            # Posicionamos un poco arriba a la derecha del jugador
            self.screen.blit(combo_txt, (self.player.rect.right + 10 - render_offset.x, self.player.rect.top - 20 - render_offset.y))

        # Dibujar barra de Power-up
        if self.player.powerup_timer > 0 and self.player.active_powerup:
            powerup_colors = {
                "FIRE": (255, 100, 0), "ICE": (0, 200, 255), "SHIELD": (200, 200, 200)
            }
            color = powerup_colors.get(self.player.active_powerup, (255, 255, 255))
            ratio = self.player.powerup_timer / Data.POWERUP_DURATION_MS
            bar_width = 50
            fill_width = int(bar_width * ratio)
            
            bar_rect = pygame.Rect(0, 0, bar_width, 8)
            bar_rect.centerx = self.player.rect.centerx - render_offset.x
            bar_rect.top = self.player.rect.bottom - render_offset.y + 8
            
            pygame.draw.rect(self.screen, Data.COLOR_OUTLINE, (bar_rect.x-2, bar_rect.y-2, bar_rect.w+4, bar_rect.h+4), border_radius=4)
            pygame.draw.rect(self.screen, (50, 50, 50), bar_rect, border_radius=3)
            if fill_width > 0:
                fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, fill_width, bar_rect.h)
                pygame.draw.rect(self.screen, color, fill_rect, border_radius=3)

        for pt in self.particles: pt.draw(self.screen, render_offset)
        
        # UI Superior
        self.draw_ui()
        
        if self.state == "UPGRADE":
            self.draw_upgrade_menu()
        elif self.state == "PAUSED":
            self.draw_pause_menu()
        elif self.state == "DEAD":
            self.draw_death_menu()
        if self.state in ("PLAYING", "PAUSED", "DEAD"):
            self.draw_admin_panel()
            self.draw_console()
            
        # Capturar frame para repetición al final del dibujado
        if self.state in ("PLAYING", "DEAD"):
            self.capture_replay_frame()

        pygame.display.flip()

    def capture_replay_frame(self):
        if not self.record_enabled: return
        # Captura la pantalla actual para el buffer de repetición
        frame = pygame.surfarray.array3d(self.screen)
        frame = frame.transpose([1, 0, 2]) # Ajustar ejes para imageio
        self.replay_frames.append(frame)

    def save_highlight_gif(self):
        if imageio is None or not self.replay_frames:
            self.highlight_message = self.tr("replay.error_no_imageio", "Error: imageio no está instalado.")
            self.highlight_message_timer = pygame.time.get_ticks()
            return

        highlights_dir = os.path.join(Data.USER_BASE_PATH, "highlights")
        os.makedirs(highlights_dir, exist_ok=True)
        
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = os.path.join(highlights_dir, f"highlight_{stamp}.gif")
        
        try:
            logger.info(f"Guardando GIF de la jugada en {path}...")
            imageio.mimsave(path, list(self.replay_frames), fps=Data.REPLAY_FPS)
            self.highlight_message = self.tr("replay.saved_ok", "¡Repetición guardada!")
        except Exception as e:
            self.highlight_message = self.tr("replay.error_saving", "Error al guardar la repetición.")
            logger.error(f"Error al guardar GIF: {e}")
        self.highlight_message_timer = pygame.time.get_ticks()

    def draw_button(self, text, rect, hover=False):
        draw_rect = rect.copy()
        if hover:
            pulse = 1 + int((math.sin(pygame.time.get_ticks() / 140.0) + 1) * 1.5)
            draw_rect.inflate_ip(pulse * 2, pulse)
        pygame.draw.rect(self.screen, Data.COLOR_OUTLINE, (draw_rect.x - 4, draw_rect.y - 4, draw_rect.w + 8, draw_rect.h + 8), border_radius=15)
        pygame.draw.rect(self.screen, (220, 255, 220) if hover else (255, 255, 255), draw_rect, border_radius=12)
        txt = self.font.render(text, True, Data.COLOR_TEXT)
        self.screen.blit(txt, (draw_rect.centerx - txt.get_width() // 2, draw_rect.centery - txt.get_height() // 2))

    def centered_button_rect(self, index, total):
        w, h = 340, 74
        gap = 22
        start_y = Data.HEIGHT // 2 - ((total * h + (total - 1) * gap) // 2) + 35
        x = Data.WIDTH // 2 - w // 2
        y = start_y + index * (h + gap)
        return pygame.Rect(x, y, w, h)

    def config_row_rect(self, index):
        return pygame.Rect(Data.WIDTH // 2 - 260, 215 + index * 70, 520, 56)

    def config_minus_rect(self, index):
        row = self.config_row_rect(index)
        return pygame.Rect(row.x + 320, row.y + 10, 48, 36)

    def config_plus_rect(self, index):
        row = self.config_row_rect(index)
        return pygame.Rect(row.x + 448, row.y + 10, 48, 36)

    def aggregate_profile_stats(self):
        if not self.records:
            return {
                "hours_total": 0.0,
                "games_total": 0,
                "score_total": 0,
                "damage_taken_total": 0.0,
                "damage_dealt_total": 0.0,
                "kills_total": 0,
                "radar": {
                    "Inteligencia": 10,
                    "Reaccion": 10,
                    "Precisión": 10,
                    "Supervivencia": 10,
                    "Agresividad": 10,
                    "Adaptacion": 10,
                    "Eficiencia": 10
                }
            }

        games = len(self.records)
        total_seconds = sum(float(r.get("duration_seconds", 0)) for r in self.records)
        score_total = sum(int(r.get("score", 0)) for r in self.records)
        dmg_taken = sum(float(r.get("damage_taken_total", 0)) for r in self.records)
        dmg_dealt = sum(float(r.get("damage_dealt_total", 0)) for r in self.records)
        kills = sum(int(r.get("enemies_killed", 0)) for r in self.records)
        shots_fired = sum(int(r.get("shots_fired", 0)) for r in self.records)
        shots_hit = sum(int(r.get("shots_hit", 0)) for r in self.records)
        mana = sum(int(r.get("mana_collected", 0)) for r in self.records)
        upgrades = sum(int(r.get("upgrades_picked", 0)) for r in self.records)

        avg_score = score_total / games
        avg_kills = kills / games
        acc = (shots_hit / shots_fired) if shots_fired > 0 else 0.0
        survival_ratio = (dmg_dealt / max(1.0, dmg_taken))
        tempo = kills / max(1.0, total_seconds / 60.0)
        growth = upgrades / games
        efficiency = (score_total + kills * 5) / max(1.0, total_seconds / 60.0)

        def clamp100(v):
            return max(0, min(100, int(v)))

        radar = {
            "Inteligencia": clamp100(20 + growth * 8 + avg_score / 25),
            "Reaccion": clamp100(20 + tempo * 8),
            "Precisión": clamp100(10 + acc * 90),
            "Supervivencia": clamp100(15 + survival_ratio * 25),
            "Agresividad": clamp100(15 + avg_kills * 4),
            "Adaptacion": clamp100(15 + (mana / max(1, games)) / 5 + growth * 5),
            "Eficiencia": clamp100(10 + efficiency * 3)
        }
        return {
            "hours_total": round(total_seconds / 3600.0, 2),
            "games_total": games,
            "score_total": score_total,
            "damage_taken_total": round(dmg_taken, 2),
            "damage_dealt_total": round(dmg_dealt, 2),
            "kills_total": kills,
            "radar": radar
        }

    def draw_heptagon_stats(self, center, radius, stats):
        labels = list(stats.keys())
        values = list(stats.values())
        points_bg = []
        points_fg = []
        for i in range(7):
            ang = -math.pi / 2 + i * (2 * math.pi / 7)
            bx = center[0] + math.cos(ang) * radius
            by = center[1] + math.sin(ang) * radius
            points_bg.append((bx, by))
            scale = max(0.0, min(1.0, values[i] / 100.0))
            fx = center[0] + math.cos(ang) * radius * scale
            fy = center[1] + math.sin(ang) * radius * scale
            points_fg.append((fx, fy))

        pygame.draw.polygon(self.screen, Data.COLOR_OUTLINE, points_bg, 2)
        for p in points_bg:
            pygame.draw.circle(self.screen, Data.COLOR_OUTLINE, (int(p[0]), int(p[1])), 3)
        fill = pygame.Surface((Data.WIDTH, Data.HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(fill, (80, 170, 255, 90), points_fg)
        self.screen.blit(fill, (0, 0))
        pygame.draw.polygon(self.screen, (40, 120, 220), points_fg, 2)

        for i, p in enumerate(points_bg):
            label = self.font.render(f"{labels[i]} {values[i]}", True, Data.COLOR_TEXT)
            lx = p[0] + (12 if p[0] >= center[0] else -label.get_width() - 12)
            ly = p[1] - 10
            self.screen.blit(label, (lx, ly))

    def draw_main_menu(self):
        title = self.title_font.render(self.tr("menu.title", "Mazmorra Cartoon"), True, Data.COLOR_TEXT)
        self.screen.blit(title, (Data.WIDTH // 2 - title.get_width() // 2, 95))
        subtitle = self.font.render(self.tr("menu.subtitle", "Panel de Inicio"), True, (90, 90, 90))
        self.screen.blit(subtitle, (Data.WIDTH // 2 - subtitle.get_width() // 2, 145))

        mx, my = pygame.mouse.get_pos()
        if self.menu_panel == "MAIN":
            labels = [
                self.tr("menu.main.play", "Jugar"),
                self.tr("menu.main.config", "Config"),
                self.tr("menu.main.records", "Records"),
                self.tr("menu.main.exit", "Salir")
            ]
        elif self.menu_panel == "PLAY":
            labels = [
                self.tr("menu.play.new", "Nueva partida"),
                self.tr("menu.play.load", "Cargar partida"),
                self.tr("common.back", "Volver")
            ]
        elif self.menu_panel == "LOAD_GAMES":
            labels = [self.tr("common.back", "Volver")]
            panel = pygame.Rect(Data.WIDTH // 2 - 520, 210, 1040, 430)
            pygame.draw.rect(self.screen, Data.COLOR_OUTLINE, (panel.x - 4, panel.y - 4, panel.w + 8, panel.h + 8), border_radius=14)
            pygame.draw.rect(self.screen, (255, 255, 255), panel, border_radius=12)
            title_load = self.font.render(self.tr("menu.play.load", "Cargar partida"), True, Data.COLOR_TEXT)
            sub_load = self.font.render(self.tr("menu.load.only_safe", "Solo partidas con salida segura"), True, (95, 95, 95))
            self.screen.blit(title_load, (panel.x + 20, panel.y + 12))
            self.screen.blit(sub_load, (panel.x + 20, panel.y + 40))
            shown = self.loadable_saves[:6]
            if not shown:
                msg = self.font.render(self.tr("menu.load.none_safe", "No hay partidas guardadas de salida segura."), True, (110, 110, 110))
                self.screen.blit(msg, (panel.x + 20, panel.y + 92))
            else:
                for i, save in enumerate(shown):
                    rect = self.load_entry_rect(i)
                    hover = rect.collidepoint(mx, my)
                    pygame.draw.rect(self.screen, Data.COLOR_OUTLINE, (rect.x-2, rect.y-2, rect.w+4, rect.h+4), border_radius=10)
                    pygame.draw.rect(self.screen, (235, 255, 235) if hover else (248, 248, 248), rect, border_radius=8)
                    line_main = f"{save['session_id']}  |  {save['ended_at']}"
                    line_sub = self.tr(
                        "menu.load.row_sub",
                        "Score {score}  |  Nivel {level}  |  Estado: Salida segura",
                        score=save["score"],
                        level=save["level"]
                    )
                    txt_main = self.font.render(line_main, True, (58, 58, 58))
                    txt_sub = self.font.render(line_sub, True, (98, 98, 98))
                    self.screen.blit(txt_main, (rect.x + 14, rect.y + 9))
                    self.screen.blit(txt_sub, (rect.x + 14, rect.y + 31))
        elif self.menu_panel == "CONFIG":
            labels = [
                self.tr("menu.config.sound", "Sonido"),
                self.tr("menu.config.stats", "Estado"),
                self.tr("menu.config.language", "Idioma: {lang}", lang=("English" if self.language == "en" else "Español")),
                self.tr("menu.config.record", "Grabar partidas: {state}", state=("ON" if self.record_enabled else "OFF")),
                self.tr("common.back", "Volver")
            ]
        elif self.menu_panel == "CONFIG_AUDIO":
            labels = [self.tr("common.back", "Volver")]
            for i, (key, label_key) in enumerate(self.volume_items):
                row = self.config_row_rect(i)
                minus = self.config_minus_rect(i)
                plus = self.config_plus_rect(i)
                pygame.draw.rect(self.screen, Data.COLOR_OUTLINE, (row.x-3, row.y-3, row.w+6, row.h+6), border_radius=12)
                pygame.draw.rect(self.screen, (255, 255, 255), row, border_radius=10)
                lv = int(self.audio.get_volume(key) * 100)
                text = self.font.render(f"{self.tr(label_key, key)}: {lv}%", True, Data.COLOR_TEXT)
                self.screen.blit(text, (row.x + 20, row.y + 16))
                self.draw_button("-", minus, minus.collidepoint(mx, my))
                self.draw_button("+", plus, plus.collidepoint(mx, my))
        elif self.menu_panel == "CONFIG_STATS":
            labels = [self.tr("common.back", "Volver")]
            panel = pygame.Rect(Data.WIDTH // 2 - 540, 205, 1080, 445)
            pygame.draw.rect(self.screen, Data.COLOR_OUTLINE, (panel.x - 4, panel.y - 4, panel.w + 8, panel.h + 8), border_radius=14)
            pygame.draw.rect(self.screen, (255, 255, 255), panel, border_radius=12)

            agg = self.aggregate_profile_stats()
            title_stats = self.font.render(self.tr("menu.stats.title", "Estado Global del Jugador"), True, Data.COLOR_TEXT)
            self.screen.blit(title_stats, (panel.x + 18, panel.y + 14))
            left_lines = [
                self.tr("menu.stats.hours", "Horas acumuladas: {v}", v=agg["hours_total"]),
                self.tr("menu.stats.games", "Partidas jugadas: {v}", v=agg["games_total"]),
                self.tr("menu.stats.score", "Score total: {v}", v=agg["score_total"]),
                self.tr("menu.stats.damage_taken", "Daño recibido total: {v}", v=agg["damage_taken_total"]),
                self.tr("menu.stats.damage_dealt", "Daño realizado total: {v}", v=int(agg["damage_dealt_total"])),
                self.tr("menu.stats.kills", "Enemigos eliminados: {v}", v=agg["kills_total"])
            ]
            for i, line in enumerate(left_lines):
                t = self.font.render(line, True, (75, 75, 75))
                self.screen.blit(t, (panel.x + 20, panel.y + 55 + i * 33))

            self.draw_heptagon_stats((panel.x + 780, panel.y + 235), 130, agg["radar"])
        elif self.menu_panel == "RECORDS":
            labels = [self.tr("common.back", "Volver")]
            panel = pygame.Rect(Data.WIDTH // 2 - 520, 210, 1040, 430)
            pygame.draw.rect(self.screen, Data.COLOR_OUTLINE, (panel.x - 4, panel.y - 4, panel.w + 8, panel.h + 8), border_radius=14)
            pygame.draw.rect(self.screen, (255, 255, 255), panel, border_radius=12)
            title_rec = self.font.render(self.tr("menu.records.title", "Historial de partidas"), True, Data.COLOR_TEXT)
            self.screen.blit(title_rec, (panel.x + 20, panel.y + 14))
            recent = self.records[-6:][::-1]
            total_games = len(self.records)
            best_score = max((int(r.get("score", 0)) for r in self.records), default=0)
            avg_kills = 0
            if total_games > 0:
                avg_kills = sum(int(r.get("enemies_killed", 0)) for r in self.records) / total_games

            chips = [
                (self.tr("menu.records.games", "Partidas"), str(total_games)),
                (self.tr("menu.records.top", "Top"), str(best_score)),
                (self.tr("menu.records.kills_per_game", "Kills/part"), f"{avg_kills:.1f}")
            ]
            chip_x = panel.x + 20
            chip_y = panel.y + 46
            for label_chip, value_chip in chips:
                chip_w = 150
                chip_h = 34
                pygame.draw.rect(self.screen, Data.COLOR_OUTLINE, (chip_x, chip_y, chip_w, chip_h), 2, border_radius=8)
                chip_txt = self.font.render(f"{label_chip}: {value_chip}", True, (80, 80, 80))
                self.screen.blit(chip_txt, (chip_x + 10, chip_y + 7))
                chip_x += chip_w + 12

            if not recent:
                no_data = self.font.render(self.tr("menu.records.none", "Sin records aún. Juega una partida para registrar datos."), True, (110, 110, 110))
                self.screen.blit(no_data, (panel.x + 20, panel.y + 100))
            else:
                for i, rec in enumerate(recent):
                    row_y = panel.y + 94 + i * 52
                    row = pygame.Rect(panel.x + 14, row_y, panel.w - 28, 48)
                    pygame.draw.rect(self.screen, Data.COLOR_OUTLINE, (row.x - 2, row.y - 2, row.w + 4, row.h + 4), border_radius=8)
                    pygame.draw.rect(self.screen, (248, 248, 248) if i % 2 == 0 else (241, 241, 241), row, border_radius=7)

                    played = str(rec.get("played_at", "--"))
                    dur = str(rec.get("duration_label", "--"))
                    score = int(rec.get("score", 0))
                    kills = int(rec.get("enemies_killed", 0))
                    dmg_out = int(rec.get("damage_dealt_total", 0))
                    dmg_in = int(rec.get("damage_taken_total", 0))
                    end_reason = str(rec.get("end_reason", "--"))
                    shot_fired = int(rec.get("shots_fired", 0))
                    shot_hit = int(rec.get("shots_hit", 0))
                    acc = 0.0 if shot_fired <= 0 else (shot_hit * 100.0 / shot_fired)
                    acc = max(0.0, min(100.0, acc))

                    main_line = self.tr(
                        "menu.records.row_main",
                        "{played}  |  {dur}  |  Score {score}  |  Kills {kills}  |  Daño {dmg_out}/{dmg_in}",
                        played=played, dur=dur, score=score, kills=kills, dmg_out=dmg_out, dmg_in=dmg_in
                    )
                    sub_line = self.tr(
                        "menu.records.row_sub",
                        "Precisión {acc}%  |  Maná {mana}  |  Mejoras {upgrades}  |  Fin {end}",
                        acc=f"{acc:.0f}", mana=rec.get("mana_collected", 0), upgrades=rec.get("upgrades_picked", 0), end=end_reason
                    )

                    txt_main = self.font.render(main_line, True, (62, 62, 62))
                    txt_sub = self.font.render(sub_line, True, (108, 108, 108))
                    self.screen.blit(txt_main, (row.x + 10, row.y + 3))
                    self.screen.blit(txt_sub, (row.x + 10, row.y + 19))
        else:
            labels = ["Volver"]

        for i, label in enumerate(labels):
            if self.menu_panel in ("RECORDS", "LOAD_GAMES"):
                rect = pygame.Rect(Data.WIDTH // 2 - 170, 650, 340, 66)
            elif self.menu_panel in ("CONFIG_AUDIO", "CONFIG_STATS"):
                rect = pygame.Rect(Data.WIDTH // 2 - 170, 215 + len(self.volume_items) * 70 + 18, 340, 66)
            else:
                rect = self.centered_button_rect(i, len(labels))
            self.draw_button(label, rect, rect.collidepoint(mx, my))

        if self.menu_message and pygame.time.get_ticks() - self.menu_message_time < 2500:
            msg = self.font.render(self.menu_message, True, (170, 40, 40))
            self.screen.blit(msg, (Data.WIDTH // 2 - msg.get_width() // 2, Data.HEIGHT - 90))

    def draw_death_menu(self):
        overlay = pygame.Surface((Data.WIDTH, Data.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        self.screen.blit(overlay, (0, 0))

        title = self.title_font.render(self.tr("death.title", "Has muerto"), True, (255, 80, 80))
        score = self.font.render(self.tr("death.score", "Score final: {score}", score=self.score), True, (255, 255, 255))
        self.screen.blit(title, (Data.WIDTH//2 - title.get_width()//2, 170))
        self.screen.blit(score, (Data.WIDTH//2 - score.get_width()//2, 225))

        labels = [self.tr("death.retry", "Reintentar"), self.tr("death.main_menu", "Menú principal")]
        if not self.highlight_saved and self.record_enabled:
            labels.insert(1, self.tr("death.save_replay", "Guardar Repetición"))

        mx, my = pygame.mouse.get_pos()
        for i, label in enumerate(labels):
            rect = self.centered_button_rect(i, len(labels))
            self.draw_button(label, rect, rect.collidepoint(mx, my))

        if self.highlight_message and pygame.time.get_ticks() - self.highlight_message_timer < 3000:
            msg = self.font.render(self.highlight_message, True, (170, 255, 170))
            self.screen.blit(msg, (Data.WIDTH // 2 - msg.get_width() // 2, 520))

    def draw_pause_menu(self):
        overlay = pygame.Surface((Data.WIDTH, Data.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        title = self.title_font.render(self.tr("pause.title", "Juego en pausa"), True, (255, 255, 255))
        self.screen.blit(title, (Data.WIDTH // 2 - title.get_width() // 2, 150))

        mx, my = pygame.mouse.get_pos()
        labels = [
            self.tr("pause.resume", "Reanudar"),
            self.tr("pause.save", "Guardar partida"),
            self.tr("pause.save_exit", "Guardar y salir al menú")
        ]
        for i, label in enumerate(labels):
            rect = self.centered_button_rect(i, len(labels))
            self.draw_button(label, rect, rect.collidepoint(mx, my))

        hint = self.font.render(self.tr("pause.hint", "ESC para reanudar"), True, (225, 225, 225))
        self.screen.blit(hint, (Data.WIDTH // 2 - hint.get_width() // 2, 120))

        if self.pause_message and pygame.time.get_ticks() - self.pause_message_time < 2200:
            msg = self.font.render(self.pause_message, True, (170, 255, 170))
            self.screen.blit(msg, (Data.WIDTH // 2 - msg.get_width() // 2, 520))

    def draw_ui(self):
        left_panel = pygame.Rect(10, 10, 320, 136)
        pygame.draw.rect(self.screen, (255, 255, 255), left_panel, border_radius=10)
        pygame.draw.rect(self.screen, Data.COLOR_OUTLINE, left_panel, 3, border_radius=10)

        hp_outer = pygame.Rect(24, 24, 292, 22)
        mana_outer = pygame.Rect(24, 56, 292, 22)
        pygame.draw.rect(self.screen, Data.COLOR_OUTLINE, hp_outer, border_radius=5)
        pygame.draw.rect(self.screen, Data.COLOR_OUTLINE, mana_outer, border_radius=5)
        hp_w = max(0, (self.player.hp / Data.PLAYER_MAX_HP) * (hp_outer.w - 4))
        mana_w = max(0, (self.player.energy / self.player.max_energy) * (mana_outer.w - 4))
        pygame.draw.rect(self.screen, (255, 50, 50), (hp_outer.x + 2, hp_outer.y + 2, hp_w, hp_outer.h - 4), border_radius=3)
        pygame.draw.rect(self.screen, Data.COLOR_MANA, (mana_outer.x + 2, mana_outer.y + 2, mana_w, mana_outer.h - 4), border_radius=3)

        lvl_txt = self.font.render(self.tr("ui.level", "Nivel: {v}", v=self.player.level), True, Data.COLOR_TEXT)
        score_txt = self.font.render(self.tr("ui.score", "Score: {v}", v=self.score), True, Data.COLOR_TEXT)
        energy_txt = self.font.render(self.tr("ui.mana", "Maná: {v}/{maxv}", v=self.player.energy, maxv=self.player.max_energy), True, (100, 100, 100))
        self.screen.blit(lvl_txt, (24, 88))
        self.screen.blit(score_txt, (170, 88))
        self.screen.blit(energy_txt, (24, 112))

        enemy_txt = self.font.render(self.tr("ui.enemies_alive", "Enemigos vivos: {v}", v=len(self.enemies)), True, (95, 95, 95))
        diff_txt = self.font.render(self.tr("ui.difficulty", "Dificultad x{v}", v=f"{self.diff_factor:.2f}"), True, (95, 95, 95))
        if self.infernal_mode:
            mode_label = self.tr("ui.mode_infernal", "Modo Infernal / Pesadilla")
        elif self.diff_factor >= Data.DIFF_MAX:
            remaining = max(0, Data.INFERNAL_UNLOCK_TIME_MS - self.max_diff_hold_ms)
            mode_label = self.tr("ui.mode_unlock", "x10 estable - Infernal en {sec}s", sec=f"{remaining/1000:.0f}")
        else:
            mode_label = self.tr("ui.mode_normal", "Modo Normal")
        mode_txt = self.font.render(mode_label, True, (95, 95, 95))
        normal_alive, elite_alive, boss_alive = self.get_enemy_type_counts()
        dynamic_caps = self.get_dynamic_spawn_caps()
        special_txt = self.font.render(
            f"N:{normal_alive}/{dynamic_caps['normal']}  E:{elite_alive}/{dynamic_caps['elite']}  B:{boss_alive}/{dynamic_caps['boss']}",
            True,
            (95, 95, 95)
        )
        ink_type = self.get_current_ink_type()
        ink_profile = self.get_ink_profile(ink_type)
        ink_txt = self.font.render(f"Tinta: {ink_profile['label']} [1/2/3]", True, ink_profile["color"])
        self.screen.blit(enemy_txt, (356, 22))
        self.screen.blit(diff_txt, (356, 50))
        self.screen.blit(mode_txt, (356, 78))
        self.screen.blit(special_txt, (356, 104))
        self.screen.blit(ink_txt, (356, 130))

        ability_title = self.font.render(self.tr("ui.active_timers", "Tiempos Activos"), True, Data.COLOR_TEXT)
        self.screen.blit(ability_title, (16, left_panel.bottom + 8))

        dash_lvl = max(1, self.player.skill_levels.get("dash", 1))
        clone_lvl = max(1, self.player.skill_levels.get("clone", 1))
        freeze_lvl = max(1, self.player.skill_levels.get("freeze_time", 1))
        giant_lvl = max(1, self.player.skill_levels.get("giant_unlock", 1))
        ad_lvl = max(1, self.player.skill_levels.get("adrenaline_rush", 1))

        timed_rows = [
            {
                "show": self.player.upgrades["clone"],
                "label": self.tr("ui.buff.clone", "Clon"),
                "act_rem": self.clone_timer,
                "act_total": self.get_clone_duration_ms(clone_lvl)
            },
            {
                "show": self.player.upgrades["freeze_time"],
                "label": self.tr("ui.buff.time", "Tiempo"),
                "act_rem": self.freeze_timer,
                "act_total": self.get_freeze_duration_ms(freeze_lvl)
            },
            {
                "show": self.player.upgrades["giant_unlock"],
                "label": self.tr("ui.buff.giant", "Gigante"),
                "act_rem": self.player.buffs["giant"],
                "act_total": self.get_giant_duration_ms(giant_lvl)
            },
            {
                "show": self.player.skill_levels.get("shield", 0) > 0 or self.player.buffs["shield"] > 0,
                "label": self.tr("ui.buff.shield", "Escudo"),
                "act_rem": self.player.buffs["shield"],
                "act_total": 7000 + (900 * max(1, self.player.skill_levels.get("shield", 1)))
            },
            {
                "show": self.player.skill_levels.get("haste", 0) > 0 or self.player.buffs["haste"] > 0,
                "label": self.tr("ui.buff.haste", "Turbo"),
                "act_rem": self.player.buffs["haste"],
                "act_total": 5200 + (800 * max(1, self.player.skill_levels.get("haste", 1)))
            },
            {
                "show": self.player.skill_levels.get("multishot", 0) > 0 or self.player.buffs["multishot"] > 0,
                "label": self.tr("ui.buff.multishot", "Lluvia"),
                "act_rem": self.player.buffs["multishot"],
                "act_total": 9000 + (1200 * max(1, self.player.skill_levels.get("multishot", 1)))
            },
            {
                "show": self.player.skill_levels.get("orbitals", 0) > 0 or self.player.buffs["orbitals"] > 0,
                "label": self.tr("ui.buff.orbitals", "Órbitas"),
                "act_rem": self.player.buffs["orbitals"],
                "act_total": 10000 + (1200 * max(1, self.player.skill_levels.get("orbitals", 1)))
            },
            {
                "show": self.player.skill_levels.get("ink", 0) > 0 or self.player.buffs["ink_trail"] > 0,
                "label": self.tr("ui.buff.ink", "Tinta"),
                "act_rem": self.player.buffs["ink_trail"],
                "act_total": 9000 + (1200 * max(1, self.player.skill_levels.get("ink", 1)))
            },
            {
                "show": self.player.skill_levels.get("confetti", 0) > 0 or self.player.buffs["confetti"] > 0,
                "label": self.tr("ui.buff.confetti", "Confeti"),
                "act_rem": self.player.buffs["confetti"],
                "act_total": 10000 + (1300 * max(1, self.player.skill_levels.get("confetti", 1)))
            },
            {
                "show": self.player.skill_levels.get("flame_ring", 0) > 0 or self.player.buffs["flame_ring"] > 0,
                "label": self.tr("ui.buff.flame_ring", "Anillo"),
                "act_rem": self.player.buffs["flame_ring"],
                "act_total": self.get_flame_ring_duration_ms(max(1, self.player.skill_levels.get("flame_ring", 1)))
            },
            {
                "show": self.player.skill_levels.get("arcane_volley", 0) > 0 or self.player.buffs["arcane_volley"] > 0,
                "label": self.tr("ui.buff.arcane", "Descarga"),
                "act_rem": self.player.buffs["arcane_volley"],
                "act_total": self.get_arcane_volley_duration_ms(max(1, self.player.skill_levels.get("arcane_volley", 1)))
            },
            {
                "show": self.player.skill_levels.get("storm_sparks", 0) > 0 or self.player.buffs["storm_sparks"] > 0,
                "label": self.tr("ui.buff.sparks", "Chispas"),
                "act_rem": self.player.buffs["storm_sparks"],
                "act_total": self.get_storm_sparks_duration_ms(max(1, self.player.skill_levels.get("storm_sparks", 1)))
            },
            {
                "show": self.player.skill_levels.get("blade_dance", 0) > 0 or self.player.buffs["blade_dance"] > 0,
                "label": self.tr("ui.buff.blade_dance", "Danza"),
                "act_rem": self.player.buffs["blade_dance"],
                "act_total": self.get_blade_dance_duration_ms(max(1, self.player.skill_levels.get("blade_dance", 1)))
            },
            {
                "show": self.player.upgrades["dash"],
                "label": self.tr("ui.buff.dash_invuln", "Invuln Dash"),
                "act_rem": self.player.buffs["dash_invuln"],
                "act_total": self.get_dash_invuln_ms(dash_lvl)
            },
            {
                "show": self.player.upgrades["adrenaline_rush"],
                "label": self.tr("ui.buff.adrenaline", "Adrenalina"),
                "act_rem": self.player.buffs["adrenaline"],
                "act_total": self.get_adrenaline_duration_ms(ad_lvl)
            }
        ]

        row_x = 16
        row_y = left_panel.bottom + 32
        row_h = 16
        bar_w = 190
        bar_h = 10
        drawn_any = False
        for item in timed_rows:
            if not item["show"]:
                continue
            if row_y + row_h > Data.HEIGHT - 10:
                break

            act_rem = max(0, float(item.get("act_rem", 0)))
            act_total = max(0.0, float(item.get("act_total", 0)))
            if act_total <= 0 or act_rem <= 0:
                continue
            drawn_any = True
            ratio = max(0.0, min(1.0, act_rem / max(1.0, act_total)))
            fill_color = (255, 170, 60)
            status = f"{act_rem/1000:.1f}s"
            label = self.font.render(item["label"], True, (60, 60, 60))
            self.screen.blit(label, (row_x, row_y - 2))

            bx = row_x + 94
            by = row_y + 1
            pygame.draw.rect(self.screen, Data.COLOR_OUTLINE, (bx, by, bar_w, bar_h))
            pygame.draw.rect(self.screen, (230, 230, 230), (bx + 1, by + 1, bar_w - 2, bar_h - 2))
            fw = int((bar_w - 2) * ratio)
            if fw > 0:
                pygame.draw.rect(self.screen, fill_color, (bx + 1, by + 1, fw, bar_h - 2))

            status_txt = self.font.render(status, True, (65, 65, 65))
            self.screen.blit(status_txt, (bx + bar_w + 8, row_y - 2))
            row_y += row_h

        if not drawn_any:
            none_txt = self.font.render(self.tr("ui.no_active_skills", "Sin habilidades temporales activas"), True, (110, 110, 110))
            self.screen.blit(none_txt, (16, left_panel.bottom + 34))

        keys = []
        if self.player.upgrades["dash"]: keys.append("SHIFT")
        if self.player.upgrades["clone"]: keys.append("C")
        if self.player.upgrades["freeze_time"]: keys.append("F")
        if self.player.upgrades["boomerang"]: keys.append("B")
        if self.player.upgrades["shockwave"]: keys.append("Q")
        if self.player.upgrades["adrenaline_rush"]: keys.append("E")
        if self.player.upgrades["giant_unlock"]: keys.append("G")
        if keys:
            txt = self.font.render(" | ".join(keys), True, (75, 75, 75))
            self.screen.blit(txt, (356, 132))

    def draw_upgrade_menu(self):
        overlay = pygame.Surface((Data.WIDTH, Data.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        title = self.title_font.render(self.tr("upgrade.level_reached", "¡NIVEL {level} ALCANZADO!", level=self.player.level), True, (255, 255, 0))
        self.screen.blit(title, (Data.WIDTH//2 - title.get_width()//2, 80))
        
        mx, my = pygame.mouse.get_pos()
        for i, upg in enumerate(self.upgrade_options):
            rect = pygame.Rect(Data.WIDTH//2 - 170, 200 + i*130, 340, 100)
            is_hover = rect.collidepoint(mx, my)

            rarity = upg.get("rarity", self.get_upgrade_rarity(upg["id"]))
            rarity_color = Data.UPGRADE_RARITY_COLORS.get(rarity, Data.COLOR_OUTLINE)
            pygame.draw.rect(self.screen, rarity_color, (rect.x-4, rect.y-4, rect.w+8, rect.h+8), border_radius=15)
            pygame.draw.rect(self.screen, (200, 255, 200) if is_hover else (255, 255, 255), rect, border_radius=12)

            next_lvl = self.player.skill_levels.get(upg["id"], 0) + 1
            dynamic_desc = self.get_upgrade_dynamic_desc(upg["id"], next_lvl)
            name = self.font.render(upg["name"], True, Data.COLOR_OUTLINE)
            desc = self.font.render(dynamic_desc, True, (80, 80, 80))
            lvl_txt = self.font.render(self.tr("upgrade.level", "Nivel {level}", level=next_lvl), True, (40, 120, 40))
            rarity_txt = self.font.render(rarity, True, rarity_color)
            self.screen.blit(name, (rect.centerx - name.get_width()//2, rect.y + 20))
            self.screen.blit(desc, (rect.centerx - desc.get_width()//2, rect.y + 55))
            self.screen.blit(lvl_txt, (rect.x + 12, rect.y + 10))
            self.screen.blit(rarity_txt, (rect.right - rarity_txt.get_width() - 12, rect.y + 10))

    def draw_grid(self, offset):
        step = 70
        ox, oy = int(offset.x % step), int(offset.y % step)
        for x in range(-ox, Data.WIDTH, step):
            pygame.draw.line(self.screen, Data.COLOR_GRID, (x, 0), (x, Data.HEIGHT))
        for y in range(-oy, Data.HEIGHT, step):
            pygame.draw.line(self.screen, Data.COLOR_GRID, (0, y), (Data.WIDTH, y))

    def run(self):
        while self.running:
            for event in pygame.event.get():
                # ESTA LÍNEA REPORTE TODO:
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    logger.debug(f"Evento detectado: {event}")

                if event.type == pygame.QUIT:
                    self.save_game()
                    self.save_settings()
                    if self.session_active and (not self.session_recorded):
                        self.finalize_session_record("quit")
                    logger.info("Cerrando el juego... ¡Adiós!")
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if event.key == pygame.K_F9 and keys[pygame.K_LCTRL] and keys[pygame.K_LSHIFT] and keys[pygame.K_LALT]:
                        self.admin_mode = not self.admin_mode
                        if not self.admin_mode:
                            self.admin_god_mode = False
                            self.creative_mode = False
                            self.admin_disable_player_shoot = False
                            self.admin_npc_free_mode = False
                            self.admin_npc_shoot_mode = False
                            self.enemy_target_mode = "player"
                            self.enemy_spawn_origin = "player"
                            self.admin_ignore_runtime_limits = False
                            self.close_console()
                        print(f"[Admin] admin_mode={'ON' if self.admin_mode else 'OFF'}")
                        continue
                    if self.admin_mode and event.key == pygame.K_t and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        self.toggle_console()
                        continue
                    if self.is_console_open:
                        if event.key == pygame.K_ESCAPE:
                            self.close_console()
                        elif event.key == pygame.K_BACKSPACE:
                            self.console_input = self.console_input[:-1]
                        elif event.key == pygame.K_RETURN:
                            self.execute_console_command(self.console_input)
                            self.console_input = ""
                        elif event.key == pygame.K_TAB:
                            pass
                        else:
                            if event.unicode and event.unicode.isprintable():
                                self.console_input += event.unicode
                        continue
                if event.type == pygame.KEYDOWN and self.state in ("PLAYING", "PAUSED"):
                    if self.admin_mode:
                        if event.key == pygame.K_F1:
                            self.admin_god_mode = not self.admin_god_mode
                            print(f"[Admin] god_mode={'ON' if self.admin_god_mode else 'OFF'}")
                        elif event.key == pygame.K_F2:
                            self.spawn_admin_enemy_at_cursor("normal")
                        elif event.key == pygame.K_F3:
                            self.spawn_admin_enemy_at_cursor("elite")
                        elif event.key == pygame.K_F4:
                            self.spawn_admin_enemy_at_cursor("boss")
                        elif event.key == pygame.K_F5 and self.player:
                            self.player.energy = min(self.player.max_energy, self.player.energy + 100)
                        elif event.key == pygame.K_F6 and self.player:
                            self.player.hp = Data.PLAYER_MAX_HP
                    if self.state == "PLAYING":
                        if event.key == pygame.K_1:
                            self.set_player_ink_type("fire")
                            continue
                        if event.key == pygame.K_2:
                            self.set_player_ink_type("cryo")
                            continue
                        if event.key == pygame.K_3:
                            self.set_player_ink_type("heavy")
                            continue
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "PLAYING":
                            self.state = "PAUSED"
                        else:
                            self.state = "PLAYING"
                    elif event.key == pygame.K_LSHIFT and self.player.upgrades["dash"] and self.player.dash_cooldown <= 0:
                        if self.state != "PLAYING":
                            continue
                        dash_lvl = max(1, self.player.skill_levels.get("dash", 1))
                        self.player.pos += self.player.last_move_dir * (160 + 25 * dash_lvl)
                        self.player.update_rect()
                        self.player.buffs["dash_invuln"] = self.get_dash_invuln_ms(dash_lvl)
                        self.player.dash_cooldown = Data.DASH_COOLDOWN_MS
                    elif event.key == pygame.K_c and self.player.upgrades["clone"] and self.player.clone_cooldown <= 0:
                        if self.state != "PLAYING":
                            continue
                        clone_lvl = max(1, self.player.skill_levels.get("clone", 1))
                        self.clone_pos = pygame.Vector2(self.player.rect.center)
                        self.clone_timer = self.get_clone_duration_ms(clone_lvl)
                        self.player.clone_cooldown = self.get_clone_cooldown_ms(clone_lvl)
                    elif event.key == pygame.K_f and self.player.upgrades["freeze_time"] and self.player.freeze_cooldown <= 0:
                        if self.state != "PLAYING":
                            continue
                        freeze_lvl = max(1, self.player.skill_levels.get("freeze_time", 1))
                        self.freeze_timer = self.get_freeze_duration_ms(freeze_lvl)
                        self.player.freeze_cooldown = self.get_freeze_cooldown_ms(freeze_lvl)
                    elif event.key == pygame.K_b and self.player.upgrades["boomerang"] and self.player.boomerang_cooldown <= 0:
                        if self.state != "PLAYING":
                            continue
                        boomerang_lvl = max(1, self.player.skill_levels.get("boomerang", 1))
                        self.cast_boomerang()
                        self.player.boomerang_cooldown = self.get_boomerang_cooldown_ms(boomerang_lvl)
                    elif event.key == pygame.K_q and self.player.upgrades["shockwave"] and self.player.shockwave_cooldown <= 0:
                        if self.state != "PLAYING":
                            continue
                        shock_lvl = max(1, self.player.skill_levels.get("shockwave", 1))
                        self.cast_shockwave()
                        self.player.shockwave_cooldown = self.get_shockwave_cooldown_ms(shock_lvl)
                    elif event.key == pygame.K_e and self.player.upgrades["adrenaline_rush"] and self.player.adrenaline_cooldown <= 0:
                        if self.state != "PLAYING":
                            continue
                        ad_lvl = max(1, self.player.skill_levels.get("adrenaline_rush", 1))
                        self.player.buffs["adrenaline"] = self.get_adrenaline_duration_ms(ad_lvl)
                        self.player.adrenaline_cooldown = self.get_adrenaline_cooldown_ms(ad_lvl)
                    elif event.key == pygame.K_g and self.player.upgrades["giant_unlock"] and self.player.giant_cooldown <= 0:
                        if self.state != "PLAYING":
                            continue
                        giant_lvl = max(1, self.player.skill_levels.get("giant_unlock", 1))
                        self.player.buffs["giant"] = self.get_giant_duration_ms(giant_lvl)
                        self.player.hp = min(Data.PLAYER_MAX_HP, self.player.hp + (15 + 8 * giant_lvl))
                        self.player.giant_cooldown = self.get_giant_cooldown_ms(giant_lvl)
                        self.play_pop_sfx()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.is_console_open:
                        continue
                    mx, my = event.pos
                    if self.state == "UPGRADE":
                        for i, upg in enumerate(self.upgrade_options):
                            rect = pygame.Rect(Data.WIDTH//2 - 170, 200 + i*130, 340, 100)
                            if rect.collidepoint(mx, my):
                                self.play_button_sfx()
                                self.apply_upgrade(upg)
                                break
                    elif self.state == "MENU":
                        if self.menu_panel == "MAIN":
                            buttons = [self.centered_button_rect(i, 4) for i in range(4)]
                            if buttons[0].collidepoint(mx, my):
                                self.play_button_sfx()
                                self.menu_panel = "PLAY"
                            elif buttons[1].collidepoint(mx, my):
                                self.play_button_sfx()
                                self.menu_panel = "CONFIG"
                            elif buttons[2].collidepoint(mx, my):
                                self.play_button_sfx()
                                self.menu_panel = "RECORDS"
                            elif buttons[3].collidepoint(mx, my):
                                self.play_button_sfx()
                                self.save_settings()
                                self.running = False
                        elif self.menu_panel == "PLAY":
                            buttons = [self.centered_button_rect(i, 3) for i in range(3)]
                            if buttons[0].collidepoint(mx, my):
                                self.play_button_sfx()
                                logger.info("Botón 'Nueva Partida' presionado. Iniciando motor...")
                                self.start_new_game()
                            elif buttons[1].collidepoint(mx, my):
                                self.play_button_sfx()
                                self.refresh_loadable_saves()
                                self.menu_panel = "LOAD_GAMES"
                            elif buttons[2].collidepoint(mx, my):
                                self.play_button_sfx()
                                self.menu_panel = "MAIN"
                        elif self.menu_panel == "LOAD_GAMES":
                            clicked = False
                            for i, save in enumerate(self.loadable_saves[:6]):
                                rect = self.load_entry_rect(i)
                                if rect.collidepoint(mx, my):
                                    self.play_button_sfx()
                                    if not self.load_game(snapshot_path=save["snapshot_path"]):
                                        self.menu_message = self.tr("menu.load.error", "No se pudo cargar la partida seleccionada")
                                        self.menu_message_time = pygame.time.get_ticks()
                                    clicked = True
                                    break
                            back_rect = pygame.Rect(Data.WIDTH // 2 - 170, 650, 340, 66)
                            if (not clicked) and back_rect.collidepoint(mx, my):
                                self.play_button_sfx()
                                self.menu_panel = "PLAY"
                        elif self.menu_panel == "CONFIG":
                            buttons = [self.centered_button_rect(i, 5) for i in range(5)]
                            if buttons[0].collidepoint(mx, my):
                                self.play_button_sfx()
                                self.menu_panel = "CONFIG_AUDIO"
                            elif buttons[1].collidepoint(mx, my):
                                self.play_button_sfx()
                                self.menu_panel = "CONFIG_STATS"
                            elif buttons[2].collidepoint(mx, my):
                                self.play_button_sfx()
                                self.cycle_language()
                            elif buttons[3].collidepoint(mx, my):
                                self.play_button_sfx()
                                self.record_enabled = not self.record_enabled
                                self.save_settings()
                                if self.record_enabled and self.state == "PLAYING" and self.session_active and self.recording_data is None:
                                    self.start_recording_session()
                            elif buttons[4].collidepoint(mx, my):
                                self.play_button_sfx()
                                self.menu_panel = "MAIN"
                        elif self.menu_panel == "CONFIG_AUDIO":
                            clicked = False
                            for i, (key, _) in enumerate(self.volume_items):
                                if self.config_minus_rect(i).collidepoint(mx, my):
                                    self.audio.set_volume(key, self.audio.get_volume(key) - 0.1)
                                    self.play_button_sfx()
                                    self.save_settings()
                                    clicked = True
                                    break
                                if self.config_plus_rect(i).collidepoint(mx, my):
                                    self.audio.set_volume(key, self.audio.get_volume(key) + 0.1)
                                    self.play_button_sfx()
                                    self.save_settings()
                                    clicked = True
                                    break
                            back_rect = pygame.Rect(Data.WIDTH // 2 - 170, 215 + len(self.volume_items) * 70 + 18, 340, 66)
                            if (not clicked) and back_rect.collidepoint(mx, my):
                                self.play_button_sfx()
                                self.menu_panel = "CONFIG"
                        elif self.menu_panel == "CONFIG_STATS":
                            back_rect = pygame.Rect(Data.WIDTH // 2 - 170, 215 + len(self.volume_items) * 70 + 18, 340, 66)
                            if back_rect.collidepoint(mx, my):
                                self.play_button_sfx()
                                self.menu_panel = "CONFIG"
                        elif self.menu_panel == "RECORDS":
                            back_rect = pygame.Rect(Data.WIDTH // 2 - 170, 650, 340, 66)
                            if back_rect.collidepoint(mx, my):
                                self.play_button_sfx()
                                self.menu_panel = "MAIN"
                    elif self.state == "PAUSED":
                        buttons = [self.centered_button_rect(i, 3) for i in range(3)]
                        if buttons[0].collidepoint(mx, my):
                            self.play_button_sfx()
                            self.state = "PLAYING"
                        elif buttons[1].collidepoint(mx, my):
                            self.play_button_sfx()
                            self.save_game()
                            logger.info("Partida guardada correctamente en disco.")
                            self.pause_message = self.tr("pause.saved_ok", "Partida guardada correctamente")
                            self.pause_message_time = pygame.time.get_ticks()
                        elif buttons[2].collidepoint(mx, my):
                            self.play_button_sfx()
                            self.save_game()
                            self.finalize_session_record("menu_exit")
                            self.state = "MENU"
                            self.menu_panel = "MAIN"
                    elif self.state == "DEAD":
                        labels = [self.tr("death.retry", "Reintentar"), self.tr("death.main_menu", "Menú principal")]
                        if not self.highlight_saved and self.record_enabled:
                            labels.insert(1, self.tr("death.save_replay", "Guardar Repetición"))
                        
                        buttons = [self.centered_button_rect(i, len(labels)) for i in range(len(labels))]

                        if buttons[0].collidepoint(mx, my): # Reintentar
                            self.play_button_sfx()
                            self.start_new_game()
                        
                        if not self.highlight_saved and self.record_enabled:
                            if buttons[1].collidepoint(mx, my): # Guardar Repetición
                                self.play_button_sfx()
                                self.save_highlight_gif()
                                self.highlight_saved = True
                            elif buttons[2].collidepoint(mx, my): # Menú Principal
                                self.play_button_sfx()
                                self.state = "MENU"
                                self.menu_panel = "MAIN"
                        elif buttons[1].collidepoint(mx, my): # Menú Principal (si no hay botón de guardar)
                            self.play_button_sfx()
                            self.state = "MENU"
                            self.menu_panel = "MAIN"
            self.update_music_for_state()
            self.update()
            self.draw()
            self.capture_video_frame(self.video_last_dt if self.video_last_dt > 0 else self.clock.get_time())
            self.clock.tick(Data.FPS)
        self.stop_video_recording()
        self.audio.stop()
        pygame.quit()

if __name__ == "__main__":
    Game().run()








