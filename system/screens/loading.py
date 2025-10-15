# system/screens/loading.py - Loading Screen beim Programmstart
import pygame


class LoadingScreen:
    """Loading Screen mit Progress Bar"""
    
    def __init__(self):
        self.title_font = None
        self.message_font = None
        self.phase_colors = {
            'assets': (100, 200, 100),    # Grün
            'fonts': (100, 150, 255),      # Blau
            'images': (255, 150, 100),     # Orange
            'firebase': (200, 100, 255),   # Lila
            'done': (255, 215, 0)          # Gold
        }
    
    def draw(self, screen, phase, progress, message):
        """
        Zeichnet Loading Screen mit Progress Bar
        
        Args:
            screen: Pygame Surface
            phase: 'assets', 'fonts', 'images', 'firebase', 'done'
            progress: 0.0 bis 1.0 (Fortschritt)
            message: Status-Text unter der Bar
        """
        # Schwarzer Hintergrund
        screen.fill((0, 0, 0))
        
        cw, ch = screen.get_size()
        
        # Fonts laden (nur einmal)
        if self.title_font is None:
            try:
                self.title_font = pygame.font.Font("assets/fonts/Astralight.ttf", 80)
                self.message_font = pygame.font.Font("assets/fonts/White On Black.ttf", 32)
            except:
                self.title_font = pygame.font.Font(None, 80)
                self.message_font = pygame.font.Font(None, 32)
        
        # Titel
        title_text = "NOVA STRIKE"
        title_surface = self.title_font.render(title_text, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(cw // 2, ch // 3))
        screen.blit(title_surface, title_rect)
        
        # Progress Bar - mittig
        bar_width = 400
        bar_height = 20
        bar_x = cw // 2 - bar_width // 2
        bar_y = ch // 2
        
        # Farbe basierend auf Phase
        bar_color = self.phase_colors.get(phase, (150, 150, 150))
        
        # Hintergrund
        pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
        
        # Fortschrittsbalken
        filled_width = int(bar_width * min(progress, 1.0))
        if filled_width > 0:
            pygame.draw.rect(screen, bar_color, (bar_x, bar_y, filled_width, bar_height))
        
        # Rahmen
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Prozent-Anzeige
        percent_text = f"{int(progress * 100)}%"
        percent_surface = self.message_font.render(percent_text, True, (200, 200, 200))
        percent_rect = percent_surface.get_rect(center=(cw // 2, bar_y - 40))
        screen.blit(percent_surface, percent_rect)
        
        # Status Message
        message_surface = self.message_font.render(message, True, (200, 200, 200))
        message_rect = message_surface.get_rect(center=(cw // 2, bar_y + 60))
        screen.blit(message_surface, message_rect)
        
        # Phase Name
        phase_name = phase.upper()
        phase_surface = pygame.font.Font(None, 24).render(phase_name, True, bar_color)
        phase_rect = phase_surface.get_rect(center=(cw // 2, bar_y + 100))
        screen.blit(phase_surface, phase_rect)
