"""
Beispiel: Wie man Fonts in der Menu-Klasse verwendet

Nachdem Fonts in assets/load_assets.py geladen wurden, kannst du sie so verwenden:
"""

# In system/menu.py:

class GameMenu:
    def __init__(self):
        # ... existierender Code ...
        pass
    
    def load_assets(self, assets):
        """Lädt Assets für das Menü"""
        # Statt pygame.font.Font direkt zu nutzen:
        # self.font = pygame.font.Font(None, FONT_SIZE)
        # self.title_font = pygame.font.Font(None, FONT_SIZE * 2)
        
        # Verwende die vorgeladenen Fonts aus assets:
        self.font = assets.get("menu_font_32", pygame.font.Font(None, 32))
        self.title_font = assets.get("title_font_64", pygame.font.Font(None, 64))
        
        # Für Controls-Text mit kleinerer Schrift:
        self.controls_font = assets.get("menu_font_24", pygame.font.Font(None, 24))
        
        # ... rest des Codes ...

# In _draw_start_menu() oder _draw_pause_menu():
    def _draw_start_menu(self, screen):
        """Zeichne Start-Menü"""
        # ... existierender Code ...
        
        # Steuerungshinweise mit kleinerem Font
        if self.controls_font:
            controls_text = "UP/DOWN Navigate    ENTER Select    ESC Quit"
            # Oder mit Unicode wenn Font es unterstützt:
            # controls_text = "↑↓ Navigate    ENTER Select    ESC Quit"
            
            current_width = screen.get_width()
            current_height = screen.get_height()
            
            self.draw_text_with_shadow(
                screen, controls_text, self.controls_font,
                current_width // 2, current_height - scale(60),
                (255, 255, 255), (0, 0, 0)
            )

# Eigene Fonts zur Laufzeit laden:
def load_custom_font(assets):
    """Beispiel: Lade einen benutzerdefinierten Font"""
    from manager.asset_manager import AssetManager
    
    manager = AssetManager()
    
    # Option 1: TrueType Font
    custom_font = manager.load_font("assets/fonts/roboto.ttf", 40)
    
    # Option 2: System Font
    system_font = manager.load_font(None, 36)
    
    # Im assets-Proxy speichern
    assets["custom_font_40"] = custom_font
    assets["system_font_36"] = system_font
    
    return custom_font

# Verschiedene Font-Größen für verschiedene Zwecke:
FONT_SIZES = {
    "tiny": 16,       # Debug-Info
    "small": 24,      # Controls, Hints
    "normal": 32,     # Menu-Optionen
    "large": 48,      # Subtitles
    "huge": 64,       # Titel
    "massive": 96     # Special Effects
}

# Alle Größen laden:
def load_all_font_sizes(font_path="assets/fonts/arial.ttf"):
    """Lädt alle Font-Größen"""
    from manager.asset_manager import AssetManager
    manager = AssetManager()
    
    fonts = {}
    for name, size in FONT_SIZES.items():
        fonts[name] = manager.load_font(font_path, size)
    
    return fonts

# Beispiel für animierte Text-Effekte:
class AnimatedText:
    """Text mit Animations-Effekten"""
    
    def __init__(self, text, font, pos, color):
        self.text = text
        self.font = font
        self.pos = pos
        self.color = color
        self.scale = 1.0
        self.alpha = 255
    
    def update(self, dt):
        """Animiere den Text"""
        # Pulsieren
        import math
        self.scale = 1.0 + 0.1 * math.sin(pygame.time.get_ticks() / 200)
    
    def draw(self, screen):
        """Zeichne den animierten Text"""
        # Render text
        text_surf = self.font.render(self.text, True, self.color)
        
        # Skalieren
        if self.scale != 1.0:
            w, h = text_surf.get_size()
            new_w = int(w * self.scale)
            new_h = int(h * self.scale)
            text_surf = pygame.transform.scale(text_surf, (new_w, new_h))
        
        # Alpha
        text_surf.set_alpha(self.alpha)
        
        # Zentriert zeichnen
        rect = text_surf.get_rect(center=self.pos)
        screen.blit(text_surf, rect)

# Testen ob Font Unicode unterstützt:
def test_unicode_support(font):
    """Teste ob Font Unicode-Zeichen unterstützt"""
    test_chars = "↑↓←→✓✗⚠♠♥♦♣"
    
    for char in test_chars:
        try:
            surf = font.render(char, True, (255, 255, 255))
            # Wenn das Zeichen als Box erscheint, ist es nicht unterstützt
            if surf.get_width() < 5:  # Zu schmal = nicht unterstützt
                print(f"Zeichen '{char}' nicht unterstützt")
            else:
                print(f"Zeichen '{char}' OK")
        except:
            print(f"Zeichen '{char}' Fehler")

# Font-Metrik-Info:
def get_font_metrics(font):
    """Hole Font-Metrik-Informationen"""
    return {
        "height": font.get_height(),
        "ascent": font.get_ascent(),
        "descent": font.get_descent(),
        "linesize": font.get_linesize(),
        "bold": font.get_bold(),
        "italic": font.get_italic()
    }
