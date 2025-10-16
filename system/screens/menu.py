# system/menu.py - Start/Pause Menu System
import pygame
import math
from config.settings import WIDTH, HEIGHT, FONT_SIZE
from system.utils import scale, scale_pos, scale_size

class GameMenu:
    """Start- und Pause-Menü mit Navigation"""

    def __init__(self):
        self.background_image         = None
        self.font                     = pygame.font.Font(None, FONT_SIZE)
        self.title_font               = pygame.font.Font(None, FONT_SIZE * 2)
        self.selected_option          = 0
        self.menu_options             = ["Start", "Highscores", "Quit"]
        self.mode_select_options      = ["Normal Mode", "Survivor Mode", "Back"]
        self.highscore_options        = ["Normal Mode", "Survivor Mode", "Back"]
        self.survivor_stage_options   = ["Rookie", "Veteran", "Elite", "Legend", "Back"]
        self.pause_options            = ["Resume", "Quit to Menu"]
        self.current_options          = self.menu_options
        self.is_pause_menu            = False
        self.is_mode_select           = False # Neuer State für Spielmodi-Auswahl
        self.is_highscore_menu        = False # Neuer State für Highscore-Menü
        self.is_survivor_stage_select = False # Neuer State für Survivor-Stage-Auswahl bei Highscores

        # Menü-Positionen werden in load_assets() gesetzt nach pygame.init()
        self.start_button_rect     = None
        self.quit_button_rect      = None
        self.resume_button_rect    = None
        self.quit_menu_button_rect = None

        # Farben für Rahmen
        self.selected_color = (255, 255, 100, 128) # Gelb   mit    Transparenz
        self.normal_color   = (255, 255, 255, 64 ) # Weiß   mit    Transparenz
        self.border_color   = (255, 255, 100     ) # Gelber Rahmen

        # Menu music channel
        self.menu_music_channel = None
        self.menu_music_playing = False

    def load_assets(self, assets):
        """Lade Menü-Assets"""
        try:
            self.background_image = pygame.image.load("assets/images/background.png").convert()
            # Skaliere auf Bildschirmgröße falls nötig
            self.assets = assets
            if self.background_image.get_size() != (WIDTH, HEIGHT):
                self.background_image = pygame.transform.scale(self.background_image, (WIDTH, HEIGHT))

            # Schriftarten laden - Verwende spezifische Fonts:
            # - Astalight für Titel
            # - White on Black für Menü
            # - KGRedHands für Controls
            self.font          = assets.get("menu_font_normal", pygame.font.Font(None, scale(FONT_SIZE + 20)))
            self.title_font    = assets.get("title_font_large", pygame.font.Font(None, scale(FONT_SIZE + 60)))
            self.controls_font = assets.get("controls_font_normal", pygame.font.Font(None, scale(FONT_SIZE + 10)))

            # Menü-Positionen definieren (nach pygame.init())
            # Diese Positionen müssen an das tatsächliche Startscreen-Bild angepasst werden
            self.start_button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)
            self.quit_button_rect  = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 120, 200, 50)

            # Pause-Menü Positionen
            self.resume_button_rect    = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)
            self.quit_menu_button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 120, 200, 50)

            print("Menu assets loaded successfully")
            # Check if fonts were loaded (using get instead of _cache)
            title_font_loaded = assets.get("title_font_large") is not None
            menu_font_loaded  = assets.get("menu_font_normal") is not None
            print(f"  - Title font: {'Astralight' if title_font_loaded else 'System Font'}")
            print(f"  - Menu font: {'White on Black' if menu_font_loaded else 'System Font'}")
        except Exception as e:
            print(f"Error loading menu assets: {e}")
            import traceback
            traceback.print_exc()
            # Fallback: Einfarbiger Hintergrund
            self.background_image = pygame.Surface((WIDTH, HEIGHT ))
            self.background_image.fill((20, 20, 50    )) # Dunkelblau
            self.font             = pygame.font.Font(None, scale(FONT_SIZE + 20))
            self.title_font       = pygame.font.Font(None, scale(FONT_SIZE + 60))
            self.controls_font    = pygame.font.Font(None, scale(FONT_SIZE + 10))

            # Fallback-Positionen
            self.start_button_rect     = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)
            self.quit_button_rect      = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 120, 200, 50)
            self.resume_button_rect    = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)
            self.quit_menu_button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 120, 200, 50)

    def set_pause_mode(self, is_pause=True):
        """Zwischen Start-Menü und Pause-Menü wechseln"""
        self.is_pause_menu            = is_pause
        self.is_mode_select           = False
        self.is_highscore_menu        = False
        self.is_survivor_stage_select = False

        if is_pause:
            self.current_options = self.pause_options
        else:
            self.current_options = self.menu_options
        self.selected_option = 0
        print(f"Set pause mode: {is_pause}, options: {self.current_options}, selected: {self.selected_option}")

    def set_mode_select(self, is_mode_select=True):
        """Wechsle zur Spielmodi-Auswahl"""
        self.is_mode_select           = is_mode_select
        self.is_pause_menu            = False
        self.is_highscore_menu        = False
        self.is_survivor_stage_select = False
        if is_mode_select:
            self.current_options = self.mode_select_options
        else:
            self.current_options = self.menu_options
        self.selected_option = 0
        print(f"Set mode select: {is_mode_select}, options: {self.current_options}, selected: {self.selected_option}")

    def set_highscore_menu(self, is_highscore=True):
        """Wechsle zum Highscore-Menü"""
        self.is_highscore_menu        = is_highscore
        self.is_mode_select           = False
        self.is_pause_menu            = False
        self.is_survivor_stage_select = False
        if is_highscore:
            self.current_options = self.highscore_options
        else:
            self.current_options = self.menu_options
        self.selected_option = 0
        print(f"Set highscore menu: {is_highscore}, options: {self.current_options}, selected: {self.selected_option}")

    def set_survivor_stage_select(self, is_stage_select=True):
        """Wechsle zur Survivor-Stage-Auswahl für Highscores"""
        self.is_survivor_stage_select = is_stage_select
        self.is_highscore_menu = False
        self.is_mode_select = False
        self.is_pause_menu = False
        if is_stage_select:
            self.current_options = self.survivor_stage_options
        else:
            self.current_options = self.highscore_options
        self.selected_option = 0
        print(f"Set survivor stage select: {is_stage_select}, options: {self.current_options}, selected: {self.selected_option}")

    def handle_input(self, event):
        """Verarbeite Menü-Eingaben"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.current_options)
                print(f"UP pressed - selected_option: {self.selected_option}, total options: {len(self.current_options)}")
                # Menu switch sound
                if hasattr(self, 'assets') and self.assets.get("menu_switch_sound"):
                    self.assets["menu_switch_sound"].play()
                return "navigate"
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.current_options)
                print(f"DOWN pressed - selected_option: {self.selected_option}, total options: {len(self.current_options)}")
                # Menu switch sound
                if hasattr(self, 'assets') and self.assets.get("menu_switch_sound"):
                    self.assets["menu_switch_sound"].play()
                return "navigate"
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                # Nur ENTER allein soll Menü auswählen, nicht Alt+ENTER (das ist für Vollbild)
                keys = pygame.key.get_pressed()
                if not (keys[pygame.K_LALT] or keys[pygame.K_RALT]):
                    action = self.get_selected_action()
                    print(f"ENTER pressed - action: {action}")
                    return action
        return None

    def get_selected_action(self):
        """Gib die gewählte Aktion zurück"""
        selected = self.current_options[self.selected_option]

        print(f"Selected option: {selected} in menu state - Pause: {self.is_pause_menu}, Mode Select: {self.is_mode_select}, Highscore Menu: {self.is_highscore_menu}, Survivor Stage Select: {self.is_survivor_stage_select}")


        if self.is_pause_menu:
            if selected == "Resume":
                return "resume"
            elif selected == "Quit to Menu":
                return "quit_to_menu"
        elif self.is_mode_select:
            if selected == "Normal Mode":
                return "start_game"
            elif selected == "Survivor Mode":
                return "start_survivor"
            elif selected == "Back":
                return "back_to_menu"
        elif self.is_highscore_menu:
            if selected == "Normal Mode":
                return "show_normal_highscores"
            elif selected == "Survivor Mode":
                return "show_survivor_stage_select"
            elif selected == "Back":
                return "back_to_menu"
        elif self.is_survivor_stage_select:
            if selected.startswith("Stage"):
                # Extrahiere Stage-Nummer (z.B. "Stage 1 - Rookie" -> 1)
                stage_num = int(selected.split()[1])
                return f"show_survivor_highscores_{stage_num}"
            elif selected == "Back":
                return "back_to_highscore_menu"
        else:
            # Hauptmenü
            if selected == "Start":
                return "show_mode_select"
            elif selected == "Highscores":
                return "show_highscores"
            elif selected == "Quit":
                return "quit_game"

        return None

    def draw_text_with_shadow(self, surface, text, font, x, y, color, shadow_color):
        """Zeichne Text mit Schatten für bessere Lesbarkeit"""
        # Schatten (leicht versetzt)
        shadow_surface = font.render(text, True, shadow_color)
        shadow_rect    = shadow_surface.get_rect(center=(x + 2, y + 2))
        surface.blit(shadow_surface, shadow_rect)

        # Haupttext
        text_surface = font.render(text, True, color)
        text_rect    = text_surface.get_rect(center=(x, y))
        surface.blit(text_surface, text_rect)

        return text_rect

    def draw(self, screen):
        """Zeichne das Menü mit Rahmen um die vorhandenen Optionen im Bild"""
        # Hintergrund zeichnen mit sanfter Zoom-Animation
        if self.background_image:
            current_size = screen.get_size()
            current_time = pygame.time.get_ticks()

            # Langsame Zoom-Animation zwischen 100% und 110%
            zoom_speed  = 0.0003  # Sehr langsam für sanfte Bewegung
            zoom_factor = 1.0 + (math.sin(current_time * zoom_speed) + 1) * 0.05  # 1.0 bis 1.1

            # Berechne Zielgröße mit Zoom
            target_width  = int(current_size[0] * zoom_factor)
            target_height = int(current_size[1] * zoom_factor)

            # Skaliere Hintergrund
            scaled_background = pygame.transform.scale(self.background_image, (target_width, target_height))

            # Zentriere das gezoomte Bild (so dass es über die Ränder hinausgeht)
            offset_x = (target_width - current_size[0]) // 2
            offset_y = (target_height - current_size[1]) // 2

            screen.blit(scaled_background, (-offset_x, -offset_y))

        if self.is_pause_menu:
            # Pause-Menü: Zeichne Rahmen um Resume/Quit Optionen
            self._draw_pause_menu(screen)
        elif self.is_mode_select:
            # Spielmodi-Auswahl
            self._draw_mode_select_menu(screen)
        elif self.is_highscore_menu:
            # Highscore-Menü
            self._draw_highscore_menu(screen)
        elif self.is_survivor_stage_select:
            # Survivor-Stage-Auswahl für Highscores
            self._draw_survivor_stage_menu(screen)
        else:
            # Start-Menü: Zeichne Rahmen um die Start/Quit Optionen im Bild
            self._draw_start_menu(screen)

    def _draw_start_menu(self, screen):
        """Zeichne eigenes Start-Menü mit Titel und Text-Optionen"""
        # Titel mit coolen Effekten zeichnen
        self._draw_title_with_effects(screen)

        # Menü-Optionen mit eigenem Text zeichnen - richtige Skalierung verwenden
        current_width = screen.get_width()
        current_height = screen.get_height()
        start_y = current_height // 2 - scale(20)  # 100px höher (war +80, jetzt -20)
        option_spacing = scale(70)  # Abstand zwischen den Optionen

        for i, option in enumerate(self.current_options):
            y_pos = start_y + (i * option_spacing)
            is_selected = (i == self.selected_option)

            # Text-Farbe basierend auf Auswahl
            if is_selected:
                text_color = (255, 255, 100)  # Helles Gelb für ausgewählte Option
                shadow_color = (100, 100, 0)  # Dunkler Schatten
                glow_color = (255, 255, 150)  # Leuchteffekt
            else:
                text_color = (200, 200, 200)  # Helles Grau für normale Optionen
                shadow_color = (50, 50, 50)   # Dunkler Schatten
                glow_color = None

            # Glüheffekt für ausgewählte Option
            if is_selected and glow_color:
                self._draw_text_glow(screen, option, self.font, current_width // 2, y_pos, glow_color)

            # Haupttext mit Schatten
            self.draw_text_with_shadow(
                screen, option, self.font,
                current_width // 2, y_pos,
                text_color, shadow_color
            )

        self._draw_controls_text(screen)

    def draw_controls_text(self, screen, text="[UP/DOWN] Navigate - [ENTER] Select - [ESC] Quit", y_position=None, color=None):
        """
        Zentrale Control-Text Anzeige für alle Screens

        Args:
            screen: Pygame Surface
            text: Control-Text
            y_position: Int - Y-Position (default: height - 60)
            color: Tuple - Text-Farbe (default: (255, 255, 255))
        """
        if self.controls_font:
            current_width  = screen.get_width()
            current_height = screen.get_height()

            if y_position is None:
                y_position = current_height - scale(60)
            if color is None:
                color = (255, 255, 255)

            self.draw_text_with_shadow(
                screen, text, self.controls_font,
                current_width // 2, y_position,
                color, (0, 0, 0)
            )

    def _draw_controls_text(self, screen, text="[UP/DOWN] Navigate - [ENTER] Select - [ESC] Quit"):
        """Legacy wrapper - ruft neue public Methode auf"""
        self.draw_controls_text(screen, text)

    def draw_title(self, screen, text, animated=False, color=None, y_position=None):
        """
        Zentrale Titel-Anzeige für alle Screens

        Args:
            screen: Pygame Surface
            text: Titel-Text
            animated: Bool - Mit Glow/Pulse Animation
            color: Tuple - Hauptfarbe (default: (255, 255, 100))
            y_position: Int - Y-Position (default: height // 4)
        """
        current_width = screen.get_width()
        current_height = screen.get_height()

        if y_position is None:
            y_position = current_height // 4
        if color is None:
            color = (255, 255, 100)

        if animated:
            # Nutze existierende Animation (TODO: Code extrahieren)
            # Für jetzt: Einfacher Titel
            pass

        # Einfacher Titel mit Schatten
        title_surface = self.title_font.render(text, True, color)
        title_rect = title_surface.get_rect(center=(current_width // 2, y_position))

        # Schatten
        shadow_surface = self.title_font.render(text, True, (0, 0, 0))
        shadow_rect = shadow_surface.get_rect(center=(current_width // 2 + 4, y_position + 4))
        screen.blit(shadow_surface, shadow_rect)
        screen.blit(title_surface, title_rect)

    def _draw_title_text( self, screen, text ):
        pass


    def _draw_mode_select_menu(self, screen):
        """Zeichne Spielmodi-Auswahlmenü"""
        # Titel mit Effekten
        current_width = screen.get_width()
        current_height = screen.get_height()

        if self.title_font:
            title_text = "SELECT GAME MODE"
            self.draw_text_with_shadow(
                screen, title_text, self.title_font,
                current_width // 2, current_height // 3,
                (100, 200, 255), (0, 0, 0)
            )

        # Menü-Optionen
        start_y = current_height // 2 + scale(20)
        option_spacing = scale(80)

        for i, option in enumerate(self.current_options):
            y_pos = start_y + (i * option_spacing)
            is_selected = (i == self.selected_option)

            # Text-Farbe basierend auf Auswahl
            if is_selected:
                text_color = (255, 255, 100)
                shadow_color = (100, 100, 0)
                glow_color = (255, 255, 150)
            else:
                text_color = (200, 200, 200)
                shadow_color = (50, 50, 50)
                glow_color = None

            # Glüheffekt für ausgewählte Option
            if is_selected and glow_color:
                self._draw_text_glow(screen, option, self.font, current_width // 2, y_pos, glow_color)

            # Haupttext mit Schatten
            self.draw_text_with_shadow(
                screen, option, self.font,
                current_width // 2, y_pos,
                text_color, shadow_color
            )

        self._draw_controls_text(screen)

    def _draw_pause_menu(self, screen):
        """Zeichne Pause-Menü mit Text-Overlay und Glow-Effekten"""
        # Semi-transparente Überlagerung - IMMER aktuelle Screen-Größe verwenden!
        current_width  = screen.get_width()
        current_height = screen.get_height()
        overlay = pygame.Surface((current_width, current_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Pause-Titel
        if self.title_font:
            pause_text = "GAME PAUSED"
            self.draw_text_with_shadow(
                screen, pause_text,
                self.title_font,
                current_width // 2,
                current_height // 3,
                (255, 255, 100),
                (0, 0, 0)
            )

        # Pause-Menü-Optionen mit eigenem Text und Glow-Effekt (wie im Start-Menü)
        current_width  = screen.get_width()
        current_height = screen.get_height()
        start_y        = current_height // 2 + scale(50)  # Position unter dem Titel
        option_spacing = scale(70)  # Abstand zwischen den Optionen

        for i, option in enumerate(self.current_options):
            y_pos = start_y + (i * option_spacing)
            is_selected = (i == self.selected_option)

            # Text-Farbe basierend auf Auswahl
            if is_selected:
                text_color = (255, 255, 100)  # Helles Gelb für ausgewählte Option
                shadow_color = (100, 100, 0)  # Dunkler Schatten
                glow_color = (255, 255, 150)  # Leuchteffekt
            else:
                text_color = (200, 200, 200)  # Helles Grau für normale Optionen
                shadow_color = (50, 50, 50)   # Dunkler Schatten
                glow_color = None

            # Glüheffekt für ausgewählte Option
            if is_selected and glow_color:
                self._draw_text_glow(screen, option, self.font, current_width // 2, y_pos, glow_color)

            # Haupttext mit Schatten
            self.draw_text_with_shadow(
                screen,
                option,
                self.font,
                current_width // 2,
                y_pos,
                text_color,
                shadow_color
            )

    def _draw_title_with_effects(self, screen):
        """Zeichne den Titel 'NOVA STRIKE' mit coolen Effekten"""
        title_text     = "NOVA STRIKE"
        current_height = screen.get_height()
        title_y        = current_height // 4

        if self.title_font:
            # Animierter Glüheffekt mit pulsierender Animation
            current_time = pygame.time.get_ticks()
            pulse_speed = 0.002  # Langsame, majestätische Pulsation für Titel

            # Sinus-basierte Pulsation für smooth Animation
            pulse_factor = (math.sin(current_time * pulse_speed) + 1) * 0.5  # 0.0 bis 1.0

            # Basis-Glow-Farben mit Animation
            base_glow_colors = [
                (100, 100, 255),   # Blauer Glow (äußerster)
                (150, 150, 255),   # Mittlerer Glow
                (200, 200, 255),   # Innerer Glow
            ]

            # Animierte Alpha-Werte basierend auf Pulsation
            base_alphas = [25, 45, 65]
            animated_glow_colors = []

            for i, (base_color, base_alpha) in enumerate(zip(base_glow_colors, base_alphas)):
                # Verschiedene Pulsations-Phasen für jeden Layer
                phase_offset = i * 0.5
                layer_pulse = (math.sin(current_time * pulse_speed + phase_offset) + 1) * 0.5

                # Alpha zwischen 50% und 150% des Basiswerts variieren
                animated_alpha = int(base_alpha * (0.5 + layer_pulse))
                animated_glow_colors.append((base_color[0], base_color[1], base_color[2], animated_alpha))

            # Mehrere Glow-Schichten zeichnen mit Animation
            for i, glow_color in enumerate(animated_glow_colors):
                # Größe der Glow-Schicht auch leicht animieren
                size_pulse = (math.sin(current_time * pulse_speed * 0.7 + i) + 1) * 0.1 + 0.9  # 0.9 bis 1.1
                offset = int(scale((len(animated_glow_colors) - i) * 3) * size_pulse)

                for dx in range(-offset, offset + 1, 2):
                    for dy in range(-offset, offset + 1, 2):
                        if dx*dx + dy*dy <= offset*offset:
                            glow_surface = self.title_font.render(title_text, True, glow_color[:3])
                            glow_surface.set_alpha(glow_color[3])
                            current_width = screen.get_width()
                            glow_rect = glow_surface.get_rect(center=(current_width // 2 + dx, title_y + dy))
                            screen.blit(glow_surface, glow_rect)

            # Schatten (mehrfach für Tiefe)
            shadow_offsets = [(scale(4), scale(4)), (scale(3), scale(3)), (scale(2), scale(2))]
            current_width = screen.get_width()
            for offset in shadow_offsets:
                shadow_surface = self.title_font.render(title_text, True, (0, 0, 0))
                shadow_surface.set_alpha(100)
                shadow_rect = shadow_surface.get_rect(center=(current_width // 2 + offset[0], title_y + offset[1]))
                screen.blit(shadow_surface, shadow_rect)

            # Haupttitel in hellem Weiß mit leichtem Blaustich und subtiler Farbanimation
            # Leichte Farbvariation für lebendigen Effekt
            color_pulse = (math.sin(current_time * pulse_speed * 0.5) + 1) * 0.1  # 0.0 bis 0.2
            title_color = (
                min(255, int(255 - color_pulse * 50)),  # Leichte Rot-Reduktion
                min(255, int(255 - color_pulse * 30)),  # Leichte Grün-Reduktion
                255  # Blau bleibt konstant
            )

            main_surface = self.title_font.render(title_text, True, title_color)
            main_rect = main_surface.get_rect(center=(current_width // 2, title_y))
            screen.blit(main_surface, main_rect)

    def _draw_text_glow(self, screen, text, font, x, y, glow_color):
        """Zeichne einen statischen Glüheffekt um Text"""
        # Statischer Glow ohne Animation - sieht professioneller aus
        glow_radius = scale(5)  # Etwas größerer Radius für bessere Sichtbarkeit

        for dx in range(-glow_radius, glow_radius + 1, 2):
            for dy in range(-glow_radius, glow_radius + 1, 2):
                distance = (dx*dx + dy*dy) ** 0.5
                if distance <= glow_radius:
                    # Stärkerer Alpha-Wert für bessere Lesbarkeit
                    alpha = int(20 * (1 - distance / glow_radius))

                    if alpha > 0:
                        glow_surface = font.render(text, True, glow_color)
                        glow_surface.set_alpha(alpha)
                        glow_rect = glow_surface.get_rect(center=(x + dx, y + dy))
                        screen.blit(glow_surface, glow_rect)

    def _draw_selection_box(self, screen, rect, is_selected):
        """Zeichne einen Auswahlrahmen um eine Option"""
        if is_selected:
            # Heller Rahmen für ausgewählte Option
            pygame.draw.rect(screen, self.border_color, rect, 3)
            # Leicht transparente Füllung
            fill_surface = pygame.Surface((rect.width, rect.height))
            fill_surface.set_alpha(32)
            fill_surface.fill(self.border_color)
            screen.blit(fill_surface, rect.topleft)
        else:
            # Dünner Rahmen für nicht-ausgewählte Option
            pygame.draw.rect(screen, (128, 128, 128), rect, 1)

    def _draw_highscore_menu(self, screen):
        """Zeichne Highscore-Menü mit Titel und Optionen"""
        # Titel
        current_width = screen.get_width()
        current_height = screen.get_height()

        title_text = "HIGHSCORES"
        title_surface = self.title_font.render(title_text, True, (255, 255, 100))
        title_rect = title_surface.get_rect(center=(current_width // 2, current_height // 4))

        # Schatten für Titel
        shadow_surface = self.title_font.render(title_text, True, (0, 0, 0))
        shadow_rect = shadow_surface.get_rect(center=(current_width // 2 + 4, current_height // 4 + 4))
        screen.blit(shadow_surface, shadow_rect)
        screen.blit(title_surface, title_rect)

        # Menü-Optionen
        start_y = current_height // 2 - scale(20)
        option_spacing = scale(70)

        for i, option in enumerate(self.current_options):
            y_pos = start_y + (i * option_spacing)
            is_selected = (i == self.selected_option)

            if is_selected:
                text_color = (255, 255, 100)
                shadow_color = (100, 100, 0)
            else:
                text_color = (200, 200, 200)
                shadow_color = (50, 50, 50)

            self.draw_text_with_shadow(screen, option, self.font, current_width // 2, y_pos, text_color, shadow_color)

    def _draw_survivor_stage_menu(self, screen):
        """Zeichne Survivor-Stage-Auswahl für Highscores"""
        # Titel
        current_width = screen.get_width()
        current_height = screen.get_height()

        title_text = "SURVIVOR HIGHSCORES"
        title_surface = self.title_font.render(title_text, True, (255, 100, 100))
        title_rect = title_surface.get_rect(center=(current_width // 2, current_height // 4))

        # Schatten für Titel
        shadow_surface = self.title_font.render(title_text, True, (0, 0, 0))
        shadow_rect = shadow_surface.get_rect(center=(current_width // 2 + 4, current_height // 4 + 4))
        screen.blit(shadow_surface, shadow_rect)
        screen.blit(title_surface, title_rect)

        # Menü-Optionen
        start_y = current_height // 2 - scale(80)
        option_spacing = scale(60)

        for i, option in enumerate(self.current_options):
            y_pos = start_y + (i * option_spacing)
            is_selected = (i == self.selected_option)

            if is_selected:
                text_color = (255, 255, 100)
                shadow_color = (100, 100, 0)
            else:
                text_color = (200, 200, 200)
                shadow_color = (50, 50, 50)

            self.draw_text_with_shadow(screen, option, self.font, current_width // 2, y_pos, text_color, shadow_color)

    def start_menu_music(self):
        """Starte Menu-Hintergrundmusik als Loop"""
        if not self.menu_music_playing and hasattr(self, 'assets'):
            sound = self.assets.get("menu_background_sound")
            if sound:
                try:
                    # Nutze einen eigenen Channel für Menu-Musik
                    if self.menu_music_channel is None:
                        self.menu_music_channel = pygame.mixer.Channel(29)
                    self.menu_music_channel.play(sound, loops=-1)  # Endlosschleife
                    self.menu_music_playing = True
                except Exception as e:
                    print(f"Failed to play menu music: {e}")

    def stop_menu_music(self):
        """Stoppe Menu-Hintergrundmusik"""
        if self.menu_music_playing and self.menu_music_channel:
            try:
                self.menu_music_channel.stop()
                self.menu_music_playing = False
            except Exception as e:
                print(f"Failed to stop menu music: {e}")
