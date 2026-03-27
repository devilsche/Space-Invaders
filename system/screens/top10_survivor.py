# system/screens/top10_survivor.py - Survivor Mode Top 10 Screen
import pygame
from config.stages import get_stage_name


class SurvivorTop10Screen:
    """Zeigt die Top 10 Highscores für Survivor Mode (für eine bestimmte Stage)"""

    def __init__(self, assets=None):
        self.assets = assets  # Speichere Assets-Referenz für Font-Caching

    def handle_and_draw(self, screen, bg_scaled, top10_list, stage, menu_ref, came_from='menu', source_label=None):
        """
        Zeichnet die Top 10 Highscore Liste für eine Stage

        Args:
            screen: Pygame Screen
            bg_scaled: Skalierter Hintergrund
            top10_list: Liste der Top 10 Scores
            stage: Stage-Nummer (1-4)
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

        # Fonts - verwende gecachte Fonts aus assets
        if self.assets:
            rank_font = self.assets.get('font_mono_normal', pygame.font.Font(None, 32))
            subtitle_font = self.assets.get('font_subtitle_large', pygame.font.Font(None, 50))
        else:
            try:
                rank_font = pygame.font.Font("assets/fonts/monofonto rg.otf", 32)
                subtitle_font = pygame.font.Font("assets/fonts/White On Black.ttf", 50)
            except:
                rank_font = pygame.font.Font(None, 32)
                subtitle_font = pygame.font.Font(None, 50)

        # Titel mit GameMenu
        stage_name = get_stage_name(stage)
        menu_ref.draw_title(screen, "SURVIVOR MODE", color=(255, 100, 100))

        # Subtitle mit Stage-Namen
        subtitle_text = subtitle_font.render(f"TOP 10 - {stage_name.upper()}", True, (255, 255, 255))
        subtitle_rect = subtitle_text.get_rect(center=(cw // 2, ch // 2 - int(180 * ui_scale)))
        screen.blit(subtitle_text, subtitle_rect)

        # Header
        header_y = int(ch // 2 - int(130 * ui_scale))
        col_rank_x = int(cw * 0.2)
        col_name_x = int(cw * 0.35)
        col_time_x = int(cw * 0.55)
        col_kills_x = int(cw * 0.75)

        header_color = (200, 200, 200)

        screen.blit(rank_font.render("RANK", True, header_color), (col_rank_x, header_y))
        screen.blit(rank_font.render("NAME", True, header_color), (col_name_x, header_y))
        screen.blit(rank_font.render("TIME", True, header_color), (col_time_x, header_y))
        screen.blit(rank_font.render("KILLS", True, header_color), (col_kills_x, header_y))

        # Entries
        start_y = header_y + int(60 * ui_scale)
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

            # Time formatieren: MM:SS.ms
            time_val = entry.get("time", 0)
            mins = int(time_val // 60)
            secs = int(time_val % 60)
            ms = int((time_val % 1) * 100)
            time_str = f"{mins:02d}:{secs:02d}.{ms:02d}"

            rank_text = rank_font.render(f"#{i+1}", True, color)
            name_text = rank_font.render(entry.get("name", "Unknown"), True, color)
            time_text = rank_font.render(time_str, True, (100, 255, 255))
            kills_text = rank_font.render(str(entry.get("kills", 0)), True, (255, 100, 100))

            screen.blit(rank_text, (col_rank_x, y))
            screen.blit(name_text, (col_name_x, y))
            screen.blit(time_text, (col_time_x, y))
            screen.blit(kills_text, (col_kills_x, y))

        # Source-Label anzeigen (LOCAL/ONLINE)
        if source_label:
            source_color = (100, 255, 100) if source_label == "ONLINE" else (200, 200, 200)
            source_text = rank_font.render(f"[ {source_label} ]", True, source_color)
            source_rect = source_text.get_rect(center=(cw // 2, subtitle_rect.bottom + int(10 * ui_scale)))
            screen.blit(source_text, source_rect)

        # Controls abhängig von came_from
        if came_from == 'game':
            controls_text = "[ENTER] Try Again - [ESC] Menu"
        else:
            tab_text = "[TAB] Local/Online - " if source_label else ""
            controls_text = f"{tab_text}[ESC] Back to Menu"

        menu_ref.draw_controls_text(screen, controls_text)

        # Event Handling
        result = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    result = "toggle_source"
                elif event.key == pygame.K_RETURN and came_from == 'game':
                    result = "retry"
                elif event.key == pygame.K_ESCAPE:
                    if came_from == 'game':
                        result = "menu"
                    else:
                        result = "back_to_highscore_menu"
                elif event.key == pygame.K_F11:
                    result = "maximize"
                elif event.key == pygame.K_RETURN and (pygame.key.get_pressed()[pygame.K_LALT] or pygame.key.get_pressed()[pygame.K_RALT]):
                    result = "fullscreen"

        pygame.display.flip()
        return result
