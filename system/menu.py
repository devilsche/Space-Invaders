# system/menu.py - Start/Pause Menu System
import pygame
import math
from config.settings import WIDTH, HEIGHT, FONT_SIZE
from system.utils import scale, scale_pos, scale_size

class GameMenu:
    """Start- und Pause-Menü mit Navigation"""

    def __init__(self):
        self.background_image = None
        self.font = None
        self.title_font = None
        self.selected_option = 0
        self.menu_options = ["Start", "Quit"]  # Passend zum Startscreen-Bild
        self.pause_options = ["Resume", "Quit to Menu"]
        self.current_options = self.menu_options
        self.is_pause_menu = False

        # Menü-Positionen werden in load_assets() gesetzt nach pygame.init()
        self.start_button_rect = None
        self.quit_button_rect = None
        self.resume_button_rect = None
        self.quit_menu_button_rect = None

        # Farben für Rahmen
        self.selected_color = (255, 255, 100, 128)  # Gelb mit Transparenz
        self.normal_color = (255, 255, 255, 64)     # Weiß mit Transparenz
        self.border_color = (255, 255, 100)         # Gelber Rahmen

    def load_assets(self):
        """Lade Menü-Assets"""
        try:
            # Hintergrundbild laden - Verwende background.png statt startscreen.png
            self.background_image = pygame.image.load("assets/images/background.png").convert()
            # Skaliere auf Bildschirmgröße falls nötig
            if self.background_image.get_size() != (WIDTH, HEIGHT):
                self.background_image = pygame.transform.scale(self.background_image, (WIDTH, HEIGHT))

            # Schriftarten laden - Mit Skalierung für verschiedene Auflösungen
            self.font = pygame.font.Font(None, scale(FONT_SIZE + 20))  # Skalierte Menü-Schrift
            self.title_font = pygame.font.Font(None, scale(FONT_SIZE + 60))  # Skalierte Titel-Schrift

            # Menü-Positionen definieren (nach pygame.init())
            # Diese Positionen müssen an das tatsächliche Startscreen-Bild angepasst werden
            self.start_button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)
            self.quit_button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 120, 200, 50)

            # Pause-Menü Positionen
            self.resume_button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)
            self.quit_menu_button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 120, 200, 50)

            print("Menu assets loaded successfully")
        except Exception as e:
            print(f"Error loading menu assets: {e}")
            # Fallback: Einfarbiger Hintergrund
            self.background_image = pygame.Surface((WIDTH, HEIGHT))
            self.background_image.fill((20, 20, 50))  # Dunkelblau
            self.font = pygame.font.Font(None, scale(FONT_SIZE + 20))
            self.title_font = pygame.font.Font(None, scale(FONT_SIZE + 60))

            # Fallback-Positionen
            self.start_button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)
            self.quit_button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 120, 200, 50)
            self.resume_button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)
            self.quit_menu_button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 120, 200, 50)

    def set_pause_mode(self, is_pause=True):
        """Zwischen Start-Menü und Pause-Menü wechseln"""
        self.is_pause_menu = is_pause
        if is_pause:
            self.current_options = self.pause_options
        else:
            self.current_options = self.menu_options
        self.selected_option = 0  # Zurück zur ersten Option
        print(f"Set pause mode: {is_pause}, options: {self.current_options}, selected: {self.selected_option}")

    def handle_input(self, event):
        """Verarbeite Menü-Eingaben"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.current_options)
                print(f"UP pressed - selected_option: {self.selected_option}, total options: {len(self.current_options)}")
                return "navigate"
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.current_options)
                print(f"DOWN pressed - selected_option: {self.selected_option}, total options: {len(self.current_options)}")
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

        if self.is_pause_menu:
            if selected == "Resume":
                return "resume"
            elif selected == "Quit to Menu":
                return "quit_to_menu"
        else:
            if selected == "Start":
                return "start_game"
            elif selected == "Quit":
                return "quit_game"

        return None

    def draw_text_with_shadow(self, surface, text, font, x, y, color, shadow_color):
        """Zeichne Text mit Schatten für bessere Lesbarkeit"""
        # Schatten (leicht versetzt)
        shadow_surface = font.render(text, True, shadow_color)
        shadow_rect = shadow_surface.get_rect(center=(x + 2, y + 2))
        surface.blit(shadow_surface, shadow_rect)

        # Haupttext
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        surface.blit(text_surface, text_rect)

        return text_rect

    def draw(self, screen):
        """Zeichne das Menü mit Rahmen um die vorhandenen Optionen im Bild"""
        # Hintergrund zeichnen - skaliert auf aktuelle Bildschirmgröße
        if self.background_image:
            current_size = screen.get_size()
            if self.background_image.get_size() != current_size:
                scaled_background = pygame.transform.scale(self.background_image, current_size)
                screen.blit(scaled_background, (0, 0))
            else:
                screen.blit(self.background_image, (0, 0))

        if self.is_pause_menu:
            # Pause-Menü: Zeichne Rahmen um Resume/Quit Optionen
            self._draw_pause_menu(screen)
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
        start_y = current_height // 2 + scale(80)  # Position unter dem Titel
        option_spacing = scale(100)  # Mehr Abstand zwischen den Optionen
        
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
        
        # Steuerungshinweise - besser lesbar machen
        if self.font:
            controls_text = "↑↓ Navigate    ENTER Select    ESC Quit"
            current_width = screen.get_width()
            current_height = screen.get_height()
            control_font = pygame.font.Font(None, scale(FONT_SIZE + 10))  # Größere Schrift
            self.draw_text_with_shadow(
                screen, controls_text, control_font,
                current_width // 2, current_height - scale(60),  # Bessere Positionierung
                (255, 255, 255), (0, 0, 0)  # Weiß statt blau für bessere Lesbarkeit
            )

    def _draw_pause_menu(self, screen):
        """Zeichne Pause-Menü mit Text-Overlay und Glow-Effekten"""
        # Semi-transparente Überlagerung
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Pause-Titel
        if self.title_font:
            pause_text = "GAME PAUSED"
            current_width = screen.get_width()
            current_height = screen.get_height()
            self.draw_text_with_shadow(
                screen, pause_text, self.title_font,
                current_width // 2, current_height // 3,
                (255, 255, 100), (0, 0, 0)
            )

        # Pause-Menü-Optionen mit eigenem Text und Glow-Effekt (wie im Start-Menü)
        current_width = screen.get_width()
        current_height = screen.get_height()
        start_y = current_height // 2 + scale(50)  # Position unter dem Titel
        option_spacing = scale(100)  # Mehr Abstand zwischen den Optionen
        
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

    def _draw_title_with_effects(self, screen):
        """Zeichne den Titel 'SPACE INVADERS' mit coolen Effekten"""
        title_text = "SPACE INVADERS"
        current_height = screen.get_height()
        title_y = current_height // 4
        
        if self.title_font:
            # Animierter Glüheffekt mit pulsierender Animation
            current_time = pygame.time.get_ticks()
            pulse_speed = 0.003  # Geschwindigkeit der Pulsation
            
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
        """Zeichne einen animierten Glüheffekt um Text"""
        # Animation für Menü-Optionen
        current_time = pygame.time.get_ticks()
        menu_pulse = (math.sin(current_time * 0.005) + 1) * 0.3 + 0.4  # 0.4 bis 1.0
        
        # Animierte Glow-Farbe
        animated_glow = (
            int(glow_color[0] * menu_pulse),
            int(glow_color[1] * menu_pulse), 
            int(glow_color[2] * menu_pulse)
        )
        
        # Radius auch leicht animieren
        base_radius = scale(8)
        radius_pulse = (math.sin(current_time * 0.004) + 1) * 0.2 + 0.8  # 0.8 bis 1.2
        glow_radius = int(base_radius * radius_pulse)
        
        for dx in range(-glow_radius, glow_radius + 1, 2):
            for dy in range(-glow_radius, glow_radius + 1, 2):
                distance = (dx*dx + dy*dy) ** 0.5
                if distance <= glow_radius:
                    # Basis-Alpha mit Animation
                    base_alpha = 50 * (1 - distance / glow_radius)
                    animated_alpha = int(base_alpha * menu_pulse)
                    
                    if animated_alpha > 0:
                        glow_surface = font.render(text, True, animated_glow)
                        glow_surface.set_alpha(animated_alpha)
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
