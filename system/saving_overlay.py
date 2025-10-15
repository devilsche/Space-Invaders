# system/saving_overlay.py - Transparente Speicher-Animation Komponente
import pygame


class SavingOverlay:
    """Transparentes Overlay für Speicher-Animation"""
    
    def __init__(self):
        self.font = None
    
    def draw(self, screen, phase, progress, status_text):
        """
        Zeichnet eine kleine Progress Bar unten rechts.
        
        Args:
            screen: Pygame Surface
            phase: "local", "online", oder "done"
            progress: 0.0 bis 1.0 (Fortschritt)
            status_text: Text unter der Bar
        """
        cw, ch = screen.get_size()
        
        # Dimensionen (klein und kompakt)
        bar_width = 200
        bar_height = 8
        padding = 20
        
        # Position: Unten rechts
        x = cw - bar_width - padding
        y = ch - bar_height - 50
        
        # Farben basierend auf Phase
        bg_color = (40, 40, 40)
        if phase == "local":
            bar_color = (100, 200, 100)  # Grün
        elif phase == "online":
            bar_color = (100, 150, 255)  # Blau
        elif phase == "done":
            bar_color = (255, 200, 50)   # Gold
        else:
            bar_color = (150, 150, 150)  # Grau
        
        # Hintergrund
        pygame.draw.rect(screen, bg_color, (x, y, bar_width, bar_height))
        
        # Fortschrittsbalken
        filled_width = int(bar_width * min(progress, 1.0))
        if filled_width > 0:
            pygame.draw.rect(screen, bar_color, (x, y, filled_width, bar_height))
        
        # Rahmen
        pygame.draw.rect(screen, (100, 100, 100), (x, y, bar_width, bar_height), 1)
        
        # Status Text
        if self.font is None:
            try:
                self.font = pygame.font.Font("assets/fonts/monofonto rg.otf", 14)
            except:
                self.font = pygame.font.Font(None, 16)
        
        text_surface = self.font.render(status_text, True, (200, 200, 200))
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x + bar_width // 2, y + bar_height + 4)
        screen.blit(text_surface, text_rect)
