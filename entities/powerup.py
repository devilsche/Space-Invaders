import pygame
import math
from config.powerup import POWERUP_CONFIG
from config.shield import SHIELD_CONFIG

class PowerUp:
    def __init__(self, x, y, powerup_type, assets):
        self.type = powerup_type
        self.config = POWERUP_CONFIG[powerup_type]

        # Bild laden und skalieren
        raw_img = pygame.image.load(self.config["img"]).convert_alpha()
        self.img = pygame.transform.smoothscale(raw_img, self.config["size"])
        self.rect = self.img.get_rect(center=(x, y))

        # Bewegung
        self.fall_speed = self.config["fall_speed"]
        self.spawn_time = pygame.time.get_ticks()
        self.duration = self.config["duration"]

        # Animation
        self.float_offset = 0
        self.float_speed = 0.05
        self.alpha = 255
        self.base_y = y  # Merke ursprüngliche Y-Position für Schweben

    def update(self):
        """Aktualisiert Position und Animation"""
        # Kontinuierlich nach unten fallen
        self.base_y += self.fall_speed

        # Schwebe-Animation (unabhängig vom Fallen)
        self.float_offset += self.float_speed
        float_y = math.sin(self.float_offset) * 2  # Reduzierter Schwebe-Effekt

        # Endposition = Fallposition + Schwebe-Offset
        self.rect.y = int(self.base_y + float_y)

        # Verblassen über Zeit
        now = pygame.time.get_ticks()
        time_alive = now - self.spawn_time

        if time_alive > self.duration * 0.7:  # Ab 70% der Lebensdauer verblassen
            fade_progress = (time_alive - self.duration * 0.7) / (self.duration * 0.3)
            self.alpha = max(50, int(255 * (1 - fade_progress)))

    def draw(self, screen):
        """Zeichnet das Power-Up mit Alpha-Blending"""
        if self.alpha < 255:
            # Temporäres Surface für Alpha-Blending
            temp_surface = self.img.copy()
            temp_surface.set_alpha(self.alpha)
            screen.blit(temp_surface, self.rect)
        else:
            screen.blit(self.img, self.rect)

    def is_expired(self):
        """Prüft ob Power-Up abgelaufen ist"""
        return pygame.time.get_ticks() - self.spawn_time > self.duration

    def offscreen(self):
        """Prüft ob Power-Up vom Bildschirm gefallen ist"""
        from config import HEIGHT
        return self.rect.top > HEIGHT

    def apply_effect(self, player):
        """Wendet Power-Up Effekt auf Player an"""
        if self.type in ["health", "repair"]:
            heal_percentage = self.config["heal_percentage"]
            heal_amount = int(player.max_health * heal_percentage)
            player.heal(heal_amount)
            return f"+{heal_amount} Health! ({int(heal_percentage*100)}%)"
        elif self.type == "shield":
            # Shield-Dauer aus Shield-Config[2] (PowerUp Shield) basierend auf Player Stage
            shield_config = SHIELD_CONFIG[2]["shield"]
            duration = shield_config["duration_by_stage"].get(player.stage, 8000)
            return {"type": "shield", "duration": duration, "config": shield_config}

        return "Power-Up!"

    def get_points(self):
        """Gibt Bonus-Punkte zurück"""
        return self.config["points"]
