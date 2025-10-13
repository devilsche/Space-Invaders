# Font Integration - Quick Start Guide

## ✅ Was wurde implementiert:

1. **AssetManager erweitert**
   - Neue `load_font()` Methode in `manager/asset_manager.py`
   - Unterstützt TrueType (.ttf) und System-Fonts
   - Automatisches Caching und Fehlerbehandlung

2. **Assets loader aktualisiert**
   - `assets/load_assets.py` lädt jetzt automatisch Fonts
   - Sucht nach: arial.ttf, roboto.ttf, dejavusans.ttf
   - Fallback auf System-Font wenn keine .ttf gefunden

3. **Vordefinierte Font-Größen**
   - `menu_font_24` - Kleine Texte (Controls)
   - `menu_font_32` - Menü-Optionen
   - `title_font_48` - Untertitel
   - `title_font_64` - Titel-Screens

## 🚀 Sofort loslegen:

### Schritt 1: Font-Datei hinzufügen (Optional)

Wenn du Unicode-Pfeile (↑↓) willst, lade eine .ttf Datei herunter:

**Empfohlen: DejaVu Sans** (Open Source)
- Download: https://dejavu-fonts.github.io/
- Datei: DejaVuSans.ttf
- Umbenennen zu: `arial.ttf` oder `dejavusans.ttf`
- Platzieren in: `assets/fonts/`

### Schritt 2: Menu aktualisieren

In `system/menu.py`, ändere die `load_assets()` Methode:

```python
def load_assets(self, assets):
    """Lädt Assets für das Menü"""
    # ALT:
    # self.font = pygame.font.Font(None, FONT_SIZE)
    # self.title_font = pygame.font.Font(None, FONT_SIZE * 2)
    
    # NEU:
    self.font = assets.get("menu_font_32")
    self.title_font = assets.get("title_font_64")
    self.controls_font = assets.get("menu_font_24")  # Für kleinere Texte
    
    # ... rest bleibt gleich
```

### Schritt 3: Unicode-Pfeile verwenden (Optional)

Wenn du DejaVu Sans installiert hast:

```python
# In _draw_start_menu():
controls_text = "↑↓ Navigate    ENTER Select    ESC Quit"
```

Falls kein Unicode-Font:
```python
# Fallback (funktioniert immer):
controls_text = "UP/DOWN Navigate    ENTER Select    ESC Quit"
```

## 📖 Code-Beispiele:

### Font direkt laden:
```python
from manager.asset_manager import AssetManager
manager = AssetManager()

# TrueType Font
custom_font = manager.load_font("assets/fonts/roboto.ttf", 40)

# System Font
system_font = manager.load_font(None, 36)
```

### Font aus Assets abrufen:
```python
def draw_menu(self, screen, assets):
    menu_font = assets["menu_font_32"]
    title_font = assets["title_font_64"]
    
    # Text rendern
    text = menu_font.render("Start Game", True, (255, 255, 255))
    screen.blit(text, (100, 100))
```

### Verschiedene Größen einer Font:
```python
# Alle Größen in einer Schleife laden:
sizes = [16, 24, 32, 48, 64, 96]
fonts = {}

for size in sizes:
    fonts[size] = manager.load_font("assets/fonts/arial.ttf", size)
```

## 🎨 Best Practices:

1. **Fonts cachen**: Lade Fonts nur einmal beim Start
2. **Größen limitieren**: Nutze 4-5 Standard-Größen statt viele verschiedene
3. **Fallback**: Immer System-Font als Fallback
4. **Performance**: Großer Text (>64px) kann langsam sein
5. **Unicode**: Teste ob dein Font die Zeichen unterstützt

## ⚠️ Troubleshooting:

**Problem**: Vierecke statt Pfeile
- **Lösung**: Font unterstützt kein Unicode → Nutze Text statt Symbole ODER lade DejaVu Sans

**Problem**: Font lädt nicht
- **Lösung**: Pfad prüfen, Dateiname prüfen (case-sensitive auf Linux!)

**Problem**: Font sieht "blocky" aus
- **Lösung**: Nutze pygame.font.Font() nicht direkt - nutze AssetManager

**Problem**: Langsames Rendering
- **Lösung**: Render Text einmal, speichere Surface, wiederhole Blit

## 📚 Weitere Ressourcen:

- `assets/fonts/README.md` - Ausführliche Doku
- `assets/fonts/example_usage.py` - Code-Beispiele
- pygame Font Doku: https://www.pygame.org/docs/ref/font.html

## ✨ Fertig!

Deine Fonts sind jetzt integriert und einsatzbereit! 🎮
