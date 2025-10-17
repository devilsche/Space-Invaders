import pygame

from assets.load_assets import *
import time
from manager.asset_manager import AssetManager

class Loading:
    """Loading Screen mit Progress Bar"""

    def __init__(self, screen):
        self.title_font   = None
        self.message_font = None
        self.screen       = screen
        self.assets       = AssetManager()

        self.current_width, self.current_height = screen.get_size()

        self.phase_colors = {
            'fonts'      : (100, 150, 255),  # Blau – neutral, UI-Text
            'ships'      : (80, 220, 120),   # Grün – Leben, Energie
            'settings'   : (160, 160, 160),  # Grau – System, neutral
            'enemies'    : (255, 80, 60),    # Rot-Orange – Gefahr
            'stages'     : (255, 130, 80),   # Orange – Fortschritt, Mission
            'weapons'    : (200, 80, 255),   # Violett – Macht, Energie
            'explosions' : (255, 50, 30),    # Rot – Hitze, Zerstörung
            'shields'    : (80, 255, 220),   # Türkis – Schutz, Plasma
            'powerups'   : (255, 100, 230),  # Pink – Belohnung, Bonus
            'backgrounds': (100, 130, 255),  # Hellblau – Tiefe, Atmosphäre
            'sounds'     : (255, 240, 100),  # Gelb – Aufmerksamkeit
            'database'   : (120, 255, 120),  # Hellgrün – Systemstatus, OK
            'done'       : (255, 215, 0)     # Gold – Erfolg, abgeschlossen
        }

    def run(self):
        self._draw('fonts', 0.02)
        self.assets = load_fonts( self.assets )
        time.sleep(2.5)
        self._update_fonts()

        self._draw('settings', 0.08)
        self.assets = load_settings( self.assets )
        time.sleep(1.5)

        self._draw('ships', 0.16)
        self.assets = load_ships( self.assets )
        time.sleep(0.5)

        self._draw('enemies', 0.36)
        self.assets = load_enemies( self.assets )
        time.sleep(0.3)

        self._draw('stages', 0.36)
        self.assets = load_stages( self.assets )
        time.sleep(0.73)

        self._draw('weapons', 0.53)
        self.assets = load_weapons( self.assets )
        time.sleep(0.83)

        self._draw('shields', 0.59)
        self.assets = load_shields( self.assets )
        time.sleep(1.3)

        self._draw('backgrounds', 0.64)
        self.assets = load_backgrounds( self.assets )
        time.sleep(1.3)

        self._draw('database', 0.95)
        self.assets = load_database( self.assets )
        time.sleep(2.3)

        self._draw('explosions', 0.95)
        self.assets = load_explosions( self.assets )
        time.sleep(1.3)

        self._draw('powerups', 0.98)
        self.assets = load_powerups( self.assets )
        time.sleep(1.)

        self._draw('done', 1.0, 'Loading complete!')
        time.sleep(1)

        return self.assets

    def _draw(self, phase, progress, message = "Loading..."):
        """
        Zeichnet Loading Screen mit Progress Bar

        Args:
            phase: 'sounds', 'fonts', 'images', 'firebase', 'done'
            progress: 0.0 bis 1.0 (Fortschritt)
            message: Status-Text unter der Bar
        """

        self.screen.fill((0, 0, 0))

        self._draw_title()
        self._draw_progress_bar(phase, progress)
        self._draw_message(phase, message)

        pygame.display.flip()
        pygame.event.pump()
        clock = pygame.time.Clock()
        clock.tick(60)

    def _draw_title(self):
        if self.title_font is None:
            self.title_font = pygame.font.Font(None, 72)

        title_surface = self.title_font.render( "NOVA STRIKE", True, (255, 255, 255))
        title_rect    = title_surface.get_rect(center=(self.current_width // 2, self.current_height // 3))

        self.screen.blit(title_surface, title_rect)

    def _draw_progress_bar(self, phase, progress):
        if self.message_font is None:
            self.message_font = pygame.font.Font(None, 24)

        bar_width  = 600
        bar_height = 40
        bar_x      = self.current_width // 2 - bar_width // 2
        bar_y      = self.current_height // 2
        bar_color  = self.phase_colors.get(phase, (150, 150, 150))

        pygame.draw.rect(self.screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))

        filled_width = int(bar_width * min(progress, 1.0))
        if filled_width > 0:
            pygame.draw.rect(self.screen, bar_color, (bar_x, bar_y, filled_width, bar_height))

        # Rahmen
        pygame.draw.rect(self.screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 2)

        # Prozent-Anzeige
        percent_text    = f"{int(progress * 100)}%"
        percent_surface = self.message_font.render(percent_text, True, (200, 200, 200))
        percent_rect    = percent_surface.get_rect(center=(self.current_width // 2, bar_y - 40))
        self.screen.blit(percent_surface, percent_rect)

    def _draw_message(self, phase, message):
        if self.message_font is None:
            self.message_font = pygame.font.Font(None, 24)

        bar_y     = self.current_height // 2
        bar_color = self.phase_colors.get(phase, (150, 150, 150))

        message_surface = self.message_font.render(message, True, (200, 200, 200))
        message_rect    = message_surface.get_rect(center=(self.current_width // 2, bar_y + 80))
        self.screen.blit(message_surface, message_rect)

        # Phase Name
        phase_name    = phase.upper()
        phase_surface = self.message_font.render(phase_name, True, bar_color)
        phase_rect    = phase_surface.get_rect(center=(self.current_width // 2, bar_y + 150))
        self.screen.blit(phase_surface, phase_rect)

    def _update_fonts(self):
        self.title_font   = self.assets.get("font_title_huge")
        self.message_font = self.assets.get("font_menu_small")




