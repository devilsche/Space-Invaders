# system/health_bar.py
import pygame

class HealthBar:
    """Health Bar Anzeige für den Spieler"""

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width  = width
        self.height = height

        # Farben
        self.bg_color = (60, 60, 60)        # Dunkler Hintergrund
        self.border_color = (200, 200, 200) # Heller Rahmen
        self.health_colors = {
            "high": (0, 255, 0),      # Grün bei >50%
            "medium": (255, 255, 0),  # Gelb bei 25-50%
            "low": (255, 100, 0),     # Orange bei 10-25%
            "critical": (255, 0, 0)   # Rot bei <10%
        }

        # Animation
        self.current_width   = width
        self.target_width    = width
        self.animation_speed = 3.0

    def get_health_color(self, health_percentage):
        """Bestimmt die Farbe basierend auf Health-Prozentsatz"""
        if health_percentage > 0.5:
            return self.health_colors["high"]
        elif health_percentage > 0.25:
            return self.health_colors["medium"]
        elif health_percentage > 0.1:
            return self.health_colors["low"]
        else:
            return self.health_colors["critical"]

    def update(self, health_percentage):
        """Aktualisiert die Health Bar Animation"""
        self.target_width = self.width * health_percentage

        # Smooth animation
        diff = self.target_width - self.current_width
        if abs(diff) > 0.5:
            self.current_width += diff * self.animation_speed * (1/60)  # 60 FPS angenommen
        else:
            self.current_width = self.target_width

    def draw(self, screen, health_percentage, current_health, max_health, label="HEALTH"):
        """Zeichnet die Health Bar"""
        # Hintergrund
        pygame.draw.rect(screen, self.bg_color, (self.x, self.y, self.width, self.height))

        # Health Bar (animiert)
        if self.current_width > 0:
            health_color = self.get_health_color(health_percentage)
            pygame.draw.rect(screen, health_color, (self.x, self.y, int(self.current_width), self.height))

        # Rahmen
        pygame.draw.rect(screen, self.border_color, (self.x, self.y, self.width, self.height), 2)

        # Health Text (optional)
        font = pygame.font.Font(None, 20)
        health_text = f"{int(current_health)}/{int(max_health)}"
        text_surface = font.render(health_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(midleft=(self.x + self.width + 15, self.y + self.height // 2))
        screen.blit(text_surface, text_rect)

        # Label (HEALTH oder SHIELD)
        label_font = pygame.font.Font(None, 16)
        label_surface = label_font.render(label, True, (200, 200, 200))
        label_rect = label_surface.get_rect(bottomleft=(self.x, self.y - 2))
        screen.blit(label_surface, label_rect)

        # Critical Health Warning
        if health_percentage < 0.25:
            # Blinkendes "LOW HEALTH" Warning
            import time
            if int(time.time() * 4) % 2:  # Blinkt 2x pro Sekunde
                warning_font = pygame.font.Font(None, 24)
                warning_text = "LOW HEALTH!" if health_percentage < 0.1 else "HEALTH LOW"
                warning_surface = warning_font.render(warning_text, True, self.health_colors["critical"])
                warning_rect = warning_surface.get_rect(topleft=(self.x, self.y + self.height + 10))
                screen.blit(warning_surface, warning_rect)
