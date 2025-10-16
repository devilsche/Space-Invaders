# system/screens/top10_normal.py - Normal Mode Top 10 Screen
import pygame


class NormalTop10Screen:
    """Zeigt die Top 10 Highscores für Normal Mode"""

    def __init__(self):
        pass

    def handle_and_draw(self, screen, bg_scaled, top10_list, menu_ref, came_from='menu'):
        """
        Zeichnet die Top 10 Highscore Liste

        Args:
            screen: Pygame Screen
            bg_scaled: Skalierter Hintergrund
            top10_list: Liste der Top 10 Scores
            menu_ref: Referenz zu GameMenu für draw_title/controls
            came_from: 'menu' oder 'game' (für Controls)

        Returns:
            "menu": Zurück zum Menü
            "retry": Try Again (nur bei came_from='game')
            "quit": Programm beenden
            "maximize": F11 gedrückt
            "fullscreen": Alt+Enter gedrückt
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
            rank_font = pygame.font.Font("assets/fonts/monofonto rg.otf", int(32 * ui_scale))
        except:
            rank_font = pygame.font.Font(None, int(28 * ui_scale))

        # Titel mit GameMenu
        menu_ref.draw_title(screen, "TOP 10 HIGHSCORES", color=(255, 215, 0))

        # Header
        header_y = int(160 * ui_scale)
        col_rank_x = int(cw * 0.15)
        col_name_x = int(cw * 0.3)
        col_score_x = int(cw * 0.5)
        col_kills_x = int(cw * 0.65)
        col_level_x = int(cw * 0.8)

        header_color = (200, 200, 200)

        screen.blit(rank_font.render("RANK", True, header_color), (col_rank_x, header_y))
        screen.blit(rank_font.render("NAME", True, header_color), (col_name_x, header_y))
        screen.blit(rank_font.render("SCORE", True, header_color), (col_score_x, header_y))
        screen.blit(rank_font.render("KILLS", True, header_color), (col_kills_x, header_y))
        screen.blit(rank_font.render("LEVEL", True, header_color), (col_level_x, header_y))

        # Entries
        start_y     = int(220 * ui_scale)
        line_height = int(50 * ui_scale)

        for i, entry in enumerate(top10_list[:10]):
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

        # Controls abhängig von came_from
        if came_from == 'game':
            controls_text = "[ENTER] Try Again - [ESC] Menu"
        else:
            controls_text = "[ESC] Back to Menu"

        menu_ref.draw_controls_text(screen, controls_text)

        # Event Handling
        result = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and came_from == 'game':
                    result = "retry"  # Try Again
                elif event.key == pygame.K_ESCAPE:
                    result = "menu"
                elif event.key == pygame.K_F11:
                    result = "maximize"
                elif event.key == pygame.K_RETURN and (pygame.key.get_pressed()[pygame.K_LALT] or pygame.key.get_pressed()[pygame.K_RALT]):
                    result = "fullscreen"

        pygame.display.flip()
        return result
