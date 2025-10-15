# system/victory_screen.py - Victory Screen after Boss Kill
import pygame

class VictoryScreen:
    """Victory Screen nach Level-Abschluss"""

    def handle_and_draw(self, screen, bg_scaled, score, total_kills,
                        projectile_manager, powerup_manager, explosion_manager,
                        player, shield, powerup_shield, player_dead):
        """
        Zeichnet und handhabt den Victory-Screen

        Returns:
            "replay": Wenn SPACE gedrückt
            "menu": Wenn ESC gedrückt
            "maximize": Wenn F11 gedrückt
            "fullscreen": Wenn ALT+ENTER gedrückt
            None: Sonst
        """
        # Hintergrund verdunkeln
        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))

        # Spielfeld mit Overlay zeichnen
        if bg_scaled:
            screen.blit(bg_scaled, (0, 0))
        else:
            screen.fill((0, 0, 0))

        projectile_manager.draw(screen)
        powerup_manager.draw(screen)
        explosion_manager.draw(screen)

        if not player_dead:
            player.draw(screen)
            if shield:
                shield.draw(screen)
            if powerup_shield:
                powerup_shield.draw(screen)

        screen.blit(overlay, (0, 0))

        # Victory Text
        cw, ch = screen.get_size()
        ui_scale = max(cw / 1920, ch / 1080) * 1.2

        # Große Schrift für Title
        try:
            title_font = pygame.font.Font("assets/fonts/Astralight.ttf", int(120 * ui_scale))
        except:
            title_font = pygame.font.Font(None, int(120 * ui_scale))

        title_text = title_font.render("VICTORY!", True, (255, 255, 100))
        title_rect = title_text.get_rect(center=(cw // 2 , ch // 4))

        # Schatten für Title
        shadow_text = title_font.render("VICTORY!", True, (0, 0, 0))
        shadow_rect = shadow_text.get_rect(center=(cw // 2 + 4, ch // 4 + 4))
        screen.blit(shadow_text, shadow_rect)
        screen.blit(title_text, title_rect)

        # Stats anzeigen
        stats_font = pygame.font.Font(None, int(50 * ui_scale))
        stats_y    = ch // 2

        stats = [
            f"Score: {score}",
            f"Total Kills: {total_kills}",
            f"Level Complete: 1"
        ]

        for i, stat in enumerate(stats):
            stat_text = stats_font.render(stat, True, (255, 255, 255))
            stat_rect = stat_text.get_rect(center=(cw // 2, stats_y + i * int(60 * ui_scale)))

            # Schatten
            shadow = stats_font.render(stat, True, (0, 0, 0))
            shadow_rect = shadow.get_rect(center=(cw // 2 + 2, stats_y + i * int(60 * ui_scale) + 2))
            screen.blit(shadow, shadow_rect)
            screen.blit(stat_text, stat_rect)

        # Controls
        try:
            controls_font = pygame.font.Font("assets/fonts/KGRedHands.ttf", int(24 * ui_scale))
        except:
            controls_font = pygame.font.Font(None, int(24 * ui_scale))
        controls_y    = ch - int(50 * ui_scale)

        controls_text = "[SPACE] Try Again - [ESC] Continue"
        controls = controls_font.render(controls_text, True, (200, 200, 200))
        controls_rect = controls.get_rect(center=(cw // 2, controls_y))
        screen.blit(controls, controls_rect)

        # Event Handling
        result = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    result = "replay"
                elif event.key == pygame.K_ESCAPE:
                    result = "menu"
                elif event.key == pygame.K_F11:
                    result = "maximize"
                elif event.key == pygame.K_RETURN and (pygame.key.get_pressed()[pygame.K_LALT] or pygame.key.get_pressed()[pygame.K_RALT]):
                    result = "fullscreen"

        pygame.display.flip()
        return result
