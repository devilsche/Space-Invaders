# system/ship_select.py - Ship Selection Screen for Survivor Mode
import pygame
from config.ship import SHIP_CONFIG
from system.utils import resource_path

class ShipSelectScreen:
    """Schiffsauswahl-Screen für den Survivor-Modus"""

    def __init__(self):
        self.selected_stage = 1
        self.show_info      = False
        # Caches (werden bei Bedarf initialisiert)
        self._cached_fonts = None
        self._cached_fonts_scale = None
        self._cached_ships = {}  # stage -> scaled Surface
        self._cached_ships_scale = None

    def _get_fonts(self, ui_scale):
        """Fonts cachen - nur neu laden wenn sich ui_scale ändert"""
        if self._cached_fonts is not None and self._cached_fonts_scale == ui_scale:
            return self._cached_fonts
        try:
            fonts = {
                "title":    pygame.font.Font(resource_path("assets/fonts/Astralight.ttf")    , int(120 * ui_scale)),
                "subtitle": pygame.font.Font(resource_path("assets/fonts/White On Black.ttf"), int(50 * ui_scale)),
                "info":     pygame.font.Font(resource_path("assets/fonts/monofonto rg.otf")  , int(32 * ui_scale)),
                "weapon":   pygame.font.Font(resource_path("assets/fonts/monofonto rg.otf")  , int(24 * ui_scale)),
                "control":  pygame.font.Font(resource_path("assets/fonts/KGRedHands.ttf")    , int(24 * ui_scale)),
                "desc":     pygame.font.Font(resource_path("assets/fonts/monofonto rg.otf")  , int(24 * ui_scale)),
            }
        except:
            fonts = {
                "title":    pygame.font.Font(None, int(120 * ui_scale)),
                "subtitle": pygame.font.Font(None, int(50 * ui_scale)),
                "info":     pygame.font.Font(None, int(32 * ui_scale)),
                "weapon":   pygame.font.Font(None, int(24 * ui_scale)),
                "control":  pygame.font.Font(None, int(24 * ui_scale)),
                "desc":     pygame.font.Font(None, int(24 * ui_scale)),
            }
        self._cached_fonts = fonts
        self._cached_fonts_scale = ui_scale
        return fonts

    def _get_ship_image(self, stage, ui_scale, assets=None):
        """Ship-Bilder cachen - nutzt AssetManager wenn verfügbar"""
        if self._cached_ships_scale != ui_scale:
            self._cached_ships.clear()
            self._cached_ships_scale = ui_scale
        if stage not in self._cached_ships:
            config = SHIP_CONFIG[stage]
            preview_size = (config["size"][0] * 3, config["size"][1] * 3)
            ship_img = None
            # Zuerst aus AssetManager (funktioniert immer, auch mit PyInstaller)
            if assets:
                cached = assets.get(f"player_stage{stage}")
                if cached:
                    ship_img = pygame.transform.scale(cached, preview_size)
            # Fallback: von Disk laden
            if ship_img is None:
                try:
                    raw = pygame.image.load(config["img"]).convert_alpha()
                    ship_img = pygame.transform.scale(raw, preview_size)
                except:
                    ship_img = pygame.Surface((60, 60))
                    ship_img.fill((100, 100, 255))
            self._cached_ships[stage] = ship_img
        return self._cached_ships[stage]

    def handle_and_draw(self, screen, bg_scaled, assets=None):
        """
        Zeichnet und handhabt den Schiffsauswahl-Screen

        Args:
            screen: Pygame screen surface
            bg_scaled: Skalierter Hintergrund
            assets: Asset dictionary (optional, für Sound-Effekte)

        Returns:
            int: Ausgewählte Stage-Nummer wenn ENTER gedrückt, None sonst
            "back": Wenn ESC gedrückt
        """
        # Hintergrund zeichnen
        if bg_scaled:
            screen.blit(bg_scaled, (0, 0))
        else:
            screen.fill((0, 0, 0))

        # Overlay für bessere Lesbarkeit
        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        cw, ch = screen.get_size()
        ui_scale = max(cw / 1920, ch / 1080) * 1.2

        # Fonts aus Cache laden
        fonts = self._get_fonts(ui_scale)

        # Info-Overlay anzeigen (wenn "i" gedrückt wurde)
        if self.show_info:
            self._draw_info_overlay(
                screen, cw, ch, ui_scale,
                fonts["subtitle"], fonts["desc"], fonts["control"]
            )

            # Event Handling für Info-Screen
            result = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
                        self.show_info = False

            pygame.display.flip()
            return result

        # Hauptscreen zeichnen
        self._draw_main_screen(
            screen, cw, ch, ui_scale,
            fonts["title"], fonts["subtitle"], fonts["info"],
            fonts["weapon"], fonts["control"], fonts["desc"],
            assets
        )

        # Event Handling
        result = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    self.show_info = True
                elif event.key == pygame.K_F11:
                    result = "maximize"
                elif event.key == pygame.K_RETURN and (pygame.key.get_pressed()[pygame.K_LALT] or pygame.key.get_pressed()[pygame.K_RALT]):
                    result = "fullscreen"
                elif event.key == pygame.K_LEFT:
                    # Play menu switch sound
                    if assets and assets.get("menu_switch_sound"):
                        assets.get("menu_switch_sound").play()
                    self.selected_stage -= 1
                    if self.selected_stage < 1:
                        self.selected_stage = 4
                elif event.key == pygame.K_RIGHT:
                    # Play menu switch sound
                    if assets and assets.get("menu_switch_sound"):
                        assets.get("menu_switch_sound").play()
                    self.selected_stage += 1
                    if self.selected_stage > 4:
                        self.selected_stage = 1
                elif event.key == pygame.K_RETURN:
                    result = self.selected_stage
                elif event.key == pygame.K_ESCAPE:
                    result = "back"

        pygame.display.flip()
        return result

    def _draw_info_overlay(self, screen, cw, ch, ui_scale, title_font, desc_font, control_font):
        """Zeichnet das Info-Overlay mit Survivor-Mode-Beschreibung"""
        # Dunkles Overlay
        info_overlay = pygame.Surface(screen.get_size())
        info_overlay.set_alpha(220)
        info_overlay.fill((0, 0, 0))
        screen.blit(info_overlay, (0, 0))

        # Info-Box
        box_width  = int(cw * 0.7)
        box_height = int(ch * 0.65)
        box_x = (cw - box_width) // 2
        box_y = (ch - box_height) // 2

        # Box Rahmen
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(screen, (30, 30, 30), box_rect)
        pygame.draw.rect(screen, (100, 200, 255), box_rect, int(4 * ui_scale))

        # Title
        info_title      = title_font.render("SURVIVOR MODE", True, (255, 100, 100))
        info_title_rect = info_title.get_rect(center=(cw // 2, box_y + int(60 * ui_scale)))
        screen.blit(info_title, info_title_rect)

        # Beschreibung
        desc_y = box_y + int(130 * ui_scale)
        desc_lines = [
            "Welcome to Survivor Mode - the ultimate test of skill!",
            "",
            "RULES:",
            "• You have only 1 HP - one hit and it's game over",
            "• No shields available - pure skill required",
            "• Survive as long as possible against endless waves",
            "• Enemy spawning increases over time",
            "• Your survival time and kills are tracked",
            "",
            "OBJECTIVE:",
            "Stay alive as long as you can and climb the leaderboard!",
            "",
            "Good luck, pilot!"
        ]

        for i, line in enumerate(desc_lines):
            if line:
                color = (255, 200, 100) if line.startswith("•") else (200, 200, 200)
                if "RULES:" in line or "OBJECTIVE:" in line:
                    color = (100, 200, 255)
                text = desc_font.render(line, True, color)
            else:
                continue
            text_rect = text.get_rect(center=(cw // 2, desc_y + i * int(35 * ui_scale)))
            screen.blit(text, text_rect)

        # Close Anweisung
        close_text = control_font.render("Press 'i' or ESC to close", True, (150, 150, 150))
        close_rect = close_text.get_rect(center=(cw // 2, box_y + box_height + int(40 * ui_scale)))
        screen.blit(close_text, close_rect)

    def _draw_main_screen(self, screen, cw, ch, ui_scale, title_font, subtitle_font,
                          info_font, weapon_font, control_font, desc_font, assets=None):
        """Zeichnet den Hauptscreen mit Schiffsauswahl"""
        # Title
        title_y = int(ch * 0.08)
        title_text = title_font.render("SELECT YOUR SHIP", True, (100, 200, 255))
        title_rect = title_text.get_rect(center=(cw // 2, title_y))
        shadow_text = title_font.render("SELECT YOUR SHIP", True, (0, 0, 0))
        shadow_rect = shadow_text.get_rect(center=(cw // 2 + 3, title_y + 3))
        screen.blit(shadow_text, shadow_rect)
        screen.blit(title_text, title_rect)

        # Info Button Hinweis
        info_hint = desc_font.render("Press 'i' for Survivor Mode info", True, (150, 200, 255))
        info_hint_rect = info_hint.get_rect(center=(cw // 2, int(140 * ui_scale)))
        screen.blit(info_hint, info_hint_rect)

        # Schiffe nebeneinander anzeigen
        stages = [1, 2, 3, 4]
        ship_spacing = cw // (len(stages) + 1)
        start_y = int(300 * ui_scale)

        for i, stage in enumerate(stages):
            x_pos = ship_spacing * (i + 1)
            config = SHIP_CONFIG[stage]

            # Ship Image aus Cache laden
            ship_img = self._get_ship_image(stage, ui_scale, assets)

            ship_rect = ship_img.get_rect(center=(x_pos, start_y))

            # Auswahlrahmen
            is_selected = (stage == self.selected_stage)
            if is_selected:
                padding = int(20 * ui_scale)
                frame_rect = ship_rect.inflate(padding * 2, padding * 2)
                pygame.draw.rect(screen, (255, 215, 0), frame_rect, int(4 * ui_scale))

                glow_rect = frame_rect.inflate(int(10 * ui_scale), int(10 * ui_scale))
                glow_surf = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (255, 215, 0, 80), glow_surf.get_rect(), int(6 * ui_scale))
                screen.blit(glow_surf, glow_rect.topleft)
            else:
                padding = int(15 * ui_scale)
                frame_rect = ship_rect.inflate(padding * 2, padding * 2)
                pygame.draw.rect(screen, (100, 100, 100), frame_rect, int(2 * ui_scale))

            screen.blit(ship_img, ship_rect)

            # Stage Name
            stage_name = ["Rookie", "Veteran", "Elite", "Legend"][stage - 1]
            stage_text = subtitle_font.render( f"{stage_name}", True, (255, 255, 255) if is_selected else (150, 150, 150))
            stage_rect = stage_text.get_rect(center=(x_pos, start_y + int(150 * ui_scale)))
            screen.blit(stage_text, stage_rect)

            # Stats
            info_y = start_y + int(210 * ui_scale)

            # Speed
            speed_text = info_font.render(f"Speed: {config['speed']}", True, (100, 255, 100) if is_selected else (80, 200, 80))
            speed_rect = speed_text.get_rect(center=(x_pos, info_y))
            screen.blit(speed_text, speed_rect)

            # Shield Info
            shield_y = info_y + int(35 * ui_scale)
            shield_available = config.get("shield", 0) == 1
            shield_text = info_font.render("Shield: " + ("YES" if shield_available else "NO"), True, (100, 255, 255) if (is_selected and shield_available) else (80, 150, 150))
            shield_rect = shield_text.get_rect(center=(x_pos, shield_y))
            screen.blit(shield_text, shield_rect)

            # Waffen-Info
            weapon_y = shield_y + int(50 * ui_scale)
            weapons = config["weapons"]

            weapon_lines = []
            if weapons.get("laser", 0) > 0:
                weapon_lines.append(f"Laser x{weapons['laser']}")
            if weapons.get("rocket", 0) > 0:
                weapon_lines.append(f"Rocket x{weapons['rocket']}")
            if weapons.get("homing_rocket", 0) > 0:
                weapon_lines.append(f"Homing x{weapons['homing_rocket']}")
            if weapons.get("blaster", 0) > 0:
                weapon_lines.append(f"Blaster x{weapons['blaster']}")
            if weapons.get("nuke", 0) > 0:
                weapon_lines.append(f"Nuke x{weapons['nuke']}")

            for j, line in enumerate(weapon_lines):
                weapon_text = weapon_font.render(line, True,
                                                (255, 200, 100) if is_selected else (180, 150, 80))
                weapon_rect = weapon_text.get_rect(center=(x_pos, weapon_y + j * int(28 * ui_scale)))
                screen.blit(weapon_text, weapon_rect)

        # Controls Anzeige
        controls_y = ch - int(80 * ui_scale)
        controls_text = control_font.render("[LEFT/RIGHT] Select Ship - [ENTER] Start - [ESC] Back to Menu",
                                           True, (200, 200, 200))
        controls_rect = controls_text.get_rect(center=(cw // 2, controls_y))
        screen.blit(controls_text, controls_rect)
