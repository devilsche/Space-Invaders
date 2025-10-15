# system/normal_mode_screens.py - Normal Mode specific screens
import pygame
import time
from system.utils import save_normal_score, get_online_manager


def draw_saving_progress(screen, phase="local", progress=0.0, status_text="Saving..."):
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
    
    # Farben
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
    try:
        font = pygame.font.Font("assets/fonts/monofonto rg.otf", 14)
    except:
        font = pygame.font.Font(None, 16)
    
    text_surface = font.render(status_text, True, (200, 200, 200))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x + bar_width // 2, y + bar_height + 4)
    screen.blit(text_surface, text_rect)


def save_with_progress_animation(screen, bg_scaled, score, player_name, kills=0, level=1):
    """
    Speichert Normal Mode Score mit animierter Progress Bar.
    
    Returns:
        tuple: (local_top_10, online_saved_successfully)
    """
    clock = pygame.time.Clock()
    
    # Phase 1: Lokales Speichern (schnell)
    for progress in [0.3, 0.6, 1.0]:
        # Hintergrund neu zeichnen
        if bg_scaled:
            screen.blit(bg_scaled, (0, 0))
        else:
            screen.fill((0, 0, 0))
        
        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Progress Bar zeichnen
        draw_saving_progress(screen, "local", progress, "Saving locally...")
        pygame.display.flip()
        clock.tick(60)  # 60 FPS
    
    # Tatsächlich lokal speichern
    local_top_10, online_saved = save_normal_score(score, player_name, kills, level)
    
    # Phase 2: Online Speichern (falls verbunden)
    if online_saved or get_online_manager().is_connected():
        for progress in [0.3, 0.6, 1.0]:
            if bg_scaled:
                screen.blit(bg_scaled, (0, 0))
            else:
                screen.fill((0, 0, 0))
            
            overlay = pygame.Surface(screen.get_size())
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            draw_saving_progress(screen, "online", progress, "Uploading online...")
            pygame.display.flip()
            clock.tick(60)
    
    # Phase 3: Fertig!
    for _ in range(15):  # 0.25 Sekunden anzeigen
        if bg_scaled:
            screen.blit(bg_scaled, (0, 0))
        else:
            screen.fill((0, 0, 0))
        
        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        status = "✓ Saved!" if online_saved else "✓ Saved locally"
        draw_saving_progress(screen, "done", 1.0, status)
        pygame.display.flip()
        clock.tick(60)
    
    return local_top_10, online_saved


class NormalModeNameInputScreen:
    """Namenseingabe-Screen für Normal Mode Highscore"""

    def __init__(self):
        self.player_name = ""

    def handle_and_draw(self, screen, bg_scaled, score, kills=0, level=1):
        """
        Zeichnet und handhabt die Namenseingabe

        Args:
            screen: Pygame Screen
            bg_scaled: Skalierter Hintergrund
            score: Erreichter Score
            kills: Anzahl der Kills
            level: Erreichtes Level

        Returns:
            "submit": Wenn Name eingegeben und ENTER gedrückt
            "skip": Wenn ESC gedrückt (nicht speichern)
            None: Sonst
        """
        # Hintergrund verdunkeln
        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))

        # Spielfeld mit Overlay zeichnen
        if bg_scaled:
            screen.blit(bg_scaled, (0, 0))
        else:
            screen.fill((0, 0, 0))

        screen.blit(overlay, (0, 0))

        cw, ch = screen.get_size()
        ui_scale = max(cw / 1920, ch / 1080) * 1.2

        # Fonts
        try:
            title_font       = pygame.font.Font("assets/fonts/Astralight.ttf"    , int(100 * ui_scale))
            stats_font       = pygame.font.Font("assets/fonts/monofonto rg.otf"  , int(60  * ui_scale))
            prompt_font      = pygame.font.Font("assets/fonts/White On Black.ttf", int(40  * ui_scale))
            name_font        = pygame.font.Font("assets/fonts/monofonto rg.otf"  , int(70  * ui_scale))
            instruction_font = pygame.font.Font("assets/fonts/White On Black.ttf", int(28  * ui_scale))
        except:
            title_font       = pygame.font.Font(None, int(80 * ui_scale))
            stats_font       = pygame.font.Font(None, int(50 * ui_scale))
            prompt_font      = pygame.font.Font(None, int(40 * ui_scale))
            name_font        = pygame.font.Font(None, int(60 * ui_scale))
            instruction_font = pygame.font.Font(None, int(30 * ui_scale))

        # Title
        title_text = title_font.render("GAME OVER", True, (255, 100, 100))
        title_rect = title_text.get_rect(center=(cw // 2, ch // 4))

        shadow_text = title_font.render("GAME OVER", True, (0, 0, 0))
        shadow_rect = shadow_text.get_rect(center=(cw // 2 + 3, ch // 4 + 3))
        screen.blit(shadow_text, shadow_rect)
        screen.blit(title_text, title_rect)

        # Score, Kills und Level
        score_text = stats_font.render(f"SCORE: {score:,}", True, (255, 255, 100))
        score_rect = score_text.get_rect(center=(cw // 2, ch // 2 - int(130 * ui_scale)))
        screen.blit(score_text, score_rect)

        kills_text = stats_font.render(f"KILLS: {kills}", True, (255, 100, 100))
        kills_rect = kills_text.get_rect(center=(cw // 2, ch // 2 - int(70 * ui_scale)))
        screen.blit(kills_text, kills_rect)

        level_text = stats_font.render(f"LEVEL: {level}", True, (100, 255, 255))
        level_rect = level_text.get_rect(center=(cw // 2, ch // 2 - int(10 * ui_scale)))
        screen.blit(level_text, level_rect)

        # Prompt
        prompt_text = prompt_font.render("Enter Your Name:", True, (200, 200, 200))
        prompt_rect = prompt_text.get_rect(center=(cw // 2, ch // 2 + int(50 * ui_scale)))
        screen.blit(prompt_text, prompt_rect)

        # Name Input mit Cursor
        display_name = self.player_name + "|"
        if not self.player_name:
            display_name = "Player|"
        
        name_text = name_font.render(display_name, True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(cw // 2, ch // 2 + int(110 * ui_scale)))

        # Box um Namen
        padding = int(20 * ui_scale)
        box_rect = name_rect.inflate(padding * 2, padding)
        pygame.draw.rect(screen, (50, 50, 50), box_rect)
        pygame.draw.rect(screen, (150, 150, 150), box_rect, 2)
        screen.blit(name_text, name_rect)

        # Instruktion
        instruction_text = instruction_font.render("Press ENTER to save, ESC to skip", True, (150, 150, 150))
        instruction_rect = instruction_text.get_rect(center=(cw // 2, ch - int(100 * ui_scale)))
        screen.blit(instruction_text, instruction_rect)

        # Event Handling
        result = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if not self.player_name:
                        self.player_name = "Player"
                    _, online_saved = save_with_progress_animation(
                        screen, bg_scaled, score, self.player_name, kills, level
                    )
                    self.player_name = ""
                    result = "submit"
                elif event.key == pygame.K_ESCAPE:
                    # ESC = Nicht speichern
                    self.player_name = ""
                    result = "skip"
                elif event.key == pygame.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                elif event.key == pygame.K_F11:
                    result = "maximize"
                elif event.key == pygame.K_RETURN and (pygame.key.get_pressed()[pygame.K_LALT] or pygame.key.get_pressed()[pygame.K_RALT]):
                    result = "fullscreen"
                else:
                    if len(self.player_name) < 15 and event.unicode.isprintable():
                        self.player_name += event.unicode

        pygame.display.flip()
        return result


class NormalModeTop10Screen:
    """Zeigt die Top 10 Highscores für Normal Mode"""

    def __init__(self):
        pass

    def handle_and_draw(self, screen, bg_scaled, top_10_list):
        """
        Zeichnet die Top 10 Highscore Liste

        Args:
            screen: Pygame Screen
            bg_scaled: Skalierter Hintergrund
            top_10_list: Liste der Top 10 Scores

        Returns:
            "menu": Zurück zum Menü
            "quit": Spiel beenden
        """
        # Hintergrund
        if bg_scaled:
            screen.blit(bg_scaled, (0, 0))
        else:
            screen.fill((0, 0, 0))

        # Overlay
        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        cw, ch = screen.get_size()
        ui_scale = max(cw / 1920, ch / 1080) * 1.2

        # Fonts
        try:
            title_font = pygame.font.Font("assets/fonts/Astralight.ttf", int(80 * ui_scale))
            rank_font = pygame.font.Font("assets/fonts/monofonto rg.otf", int(32 * ui_scale))
            instruction_font = pygame.font.Font("assets/fonts/White On Black.ttf", int(28 * ui_scale))
        except:
            title_font = pygame.font.Font(None, int(70 * ui_scale))
            rank_font = pygame.font.Font(None, int(28 * ui_scale))
            instruction_font = pygame.font.Font(None, int(24 * ui_scale))

        # Title
        title_text = title_font.render("TOP 10 HIGHSCORES", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(cw // 2, int(80 * ui_scale)))
        screen.blit(title_text, title_rect)

        # Header
        header_y = int(160 * ui_scale)
        col_rank_x = int(cw * 0.15)
        col_name_x = int(cw * 0.3)
        col_score_x = int(cw * 0.5)
        col_kills_x = int(cw * 0.65)
        col_level_x = int(cw * 0.8)

        header_font = rank_font
        header_color = (200, 200, 200)
        
        screen.blit(header_font.render("RANK", True, header_color), (col_rank_x, header_y))
        screen.blit(header_font.render("NAME", True, header_color), (col_name_x, header_y))
        screen.blit(header_font.render("SCORE", True, header_color), (col_score_x, header_y))
        screen.blit(header_font.render("KILLS", True, header_color), (col_kills_x, header_y))
        screen.blit(header_font.render("LEVEL", True, header_color), (col_level_x, header_y))

        # Entries
        start_y = int(220 * ui_scale)
        line_height = int(50 * ui_scale)

        for i, entry in enumerate(top_10_list[:10]):
            y = start_y + i * line_height
            
            # Farbe basierend auf Rang
            if i == 0:
                color = (255, 215, 0)  # Gold
            elif i == 1:
                color = (192, 192, 192)  # Silber
            elif i == 2:
                color = (205, 127, 50)  # Bronze
            else:
                color = (255, 255, 255)  # Weiß

            rank_text = rank_font.render(f"#{i+1}", True, color)
            name_text = rank_font.render(entry.get("name", "Unknown"), True, color)
            score_text = rank_font.render(f"{entry.get('score', 0):,}", True, (255, 255, 100))
            kills_text = rank_font.render(str(entry.get("kills", 0)), True, (255, 100, 100))
            level_text = rank_font.render(str(entry.get("level", 1)), True, (100, 255, 255))

            screen.blit(rank_text, (col_rank_x, y))
            screen.blit(name_text, (col_name_x, y))
            screen.blit(score_text, (col_score_x, y))
            screen.blit(kills_text, (col_kills_x, y))
            screen.blit(level_text, (col_level_x, y))

        # Instruktionen (zwei Zeilen)
        instruction_font_small = pygame.font.Font(None, int(28 * ui_scale))
        instruction1_text = instruction_font.render("Press ENTER to try again  |  ESC for menu", True, (200, 200, 200))
        instruction1_rect = instruction1_text.get_rect(center=(cw // 2, ch - int(100 * ui_scale)))
        screen.blit(instruction1_text, instruction1_rect)

        # Event Handling
        result = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    result = "retry"  # Try Again
                elif event.key == pygame.K_ESCAPE:
                    result = "menu"
                elif event.key == pygame.K_F11:
                    result = "maximize"
                elif event.key == pygame.K_RETURN and (pygame.key.get_pressed()[pygame.K_LALT] or pygame.key.get_pressed()[pygame.K_RALT]):
                    result = "fullscreen"

        pygame.display.flip()
        return result
