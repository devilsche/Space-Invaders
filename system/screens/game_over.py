# system/screens/game_over.py - Game Over Screen mit Name Input
import pygame
from system.utils import scale


class GameOverScreen:
    """Game Over Screen mit integriertem Name Input"""

    def __init__(self, assets=None):
        self.player_name   = ''
        self.allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_')
        self.assets        = assets  # Speichere Assets-Referenz

    def handle_and_draw(self, screen, bg_scaled, stats_dict, menu_ref):
        """
        Zeichnet Game Over Screen mit Name Input

        Args:
            screen: Pygame Screen
            bg_scaled: Skalierter Hintergrund
            stats_dict: Dict mit Stats (Score, Kills, Level, Time optional)
            menu_ref: Referenz zu GameMenu für draw_title/controls

        Returns:
            "submit": Name eingegeben und ENTER gedrückt
            "skip": ESC gedrückt (nicht speichern)
            "quit": Programm beenden
            "maximize": F11 gedrückt
            "fullscreen": Alt+Enter gedrückt
            None: Noch in Eingabe
        """
        # Hintergrund verdunkeln (transparent)
        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))

        # Spielfeld mit Overlay zeichnen
        if bg_scaled:
            screen.blit(bg_scaled, (0, 0))
        else:
            screen.fill((0, 0, 0))

        screen.blit(overlay, (0, 0))

        cw, ch      = screen.get_size()
        ui_scale    = max(cw / 1920, ch / 1080) * 1.2
        stats_font  = self.assets.get('font_mono_medium')
        prompt_font = self.assets.get('font_subtitle_medium')
        name_font   = self.assets.get('font_mono_large')

        # Titel mit GameMenu
        menu_ref.draw_title(screen, "GAME OVER", color=(255, 100, 100), y_position=60)

        # Stats anzeigen
        start_y = ch // 2 - int(130 * ui_scale)
        line_spacing = int(60 * ui_scale)

        # Score (immer vorhanden)
        if 'Score' in stats_dict:
            score_text = stats_font.render(f"SCORE: {stats_dict['Score']:,}", True, (255, 255, 100))
            score_rect = score_text.get_rect(center=(cw // 2, start_y))
            screen.blit(score_text, score_rect)
            start_y += line_spacing

        # Kills (immer vorhanden)
        if 'Kills' in stats_dict:
            kills_text = stats_font.render(f"KILLS: {stats_dict['Kills']}", True, (255, 100, 100))
            kills_rect = kills_text.get_rect(center=(cw // 2, start_y))
            screen.blit(kills_text, kills_rect)
            start_y += line_spacing

        # Level (Normal Mode)
        if 'Level' in stats_dict:
            level_text = stats_font.render(f"LEVEL: {stats_dict['Level']}", True, (100, 255, 255))
            level_rect = level_text.get_rect(center=(cw // 2, start_y))
            screen.blit(level_text, level_rect)
            start_y += line_spacing

        # Time (Survivor Mode)
        if 'Time' in stats_dict:
            time_text = stats_font.render(f"TIME: {stats_dict['Time']}", True, (100, 255, 255))
            time_rect = time_text.get_rect(center=(cw // 2, start_y))
            screen.blit(time_text, time_rect)
            start_y += line_spacing

        # Prompt
        prompt_text = prompt_font.render("Enter Your Name:", True, (200, 200, 200))
        prompt_rect = prompt_text.get_rect(center=(cw // 2, ch // 2 + int(80 * ui_scale)))
        screen.blit(prompt_text, prompt_rect)

        # Name Input mit Cursor
        display_name = self.player_name + "|"
        if not self.player_name:
            display_name = "|"

        name_text = name_font.render(display_name, True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(cw // 2, ch // 2 + int(110 * ui_scale)))

        # Box um Namen
        padding = int(20 * ui_scale)
        box_rect = name_rect.inflate(padding * 2, padding)
        pygame.draw.rect(screen, (50, 50, 50), box_rect)
        pygame.draw.rect(screen, (150, 150, 150), box_rect, 2)
        screen.blit(name_text, name_rect)

        # Controls mit GameMenu
        menu_ref.draw_controls_text(screen, "[ENTER] Save - [ESC] Skip")

        # Event Handling
        result = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Wenn leer, setze "Player"
                    if not self.player_name:
                        self.player_name = "Player"

                    # SPEICHERE DEN SCORE JETZT!
                    score = stats_dict.get('Score', 0)
                    kills = stats_dict.get('Kills', 0)
                    level = stats_dict.get('Level', 1)

                    from system.utils import save_normal_score
                    save_normal_score(score, self.player_name, kills, level)

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
                    # Nur erlaubte Zeichen: a-zA-Z0-9_
                    if len(self.player_name) < 15 and event.unicode in self.allowed_chars:
                        self.player_name += event.unicode

        pygame.display.flip()
        return result

    def get_player_name(self):
        """Gibt den eingegebenen Namen zurück"""
        return self.player_name if self.player_name else "Player"

    def reset(self):
        """Setzt den Namen zurück"""
        self.player_name = ""
