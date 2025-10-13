# Font Installation für Space Invaders

## 📋 Benötigte Fonts

Du brauchst diese 3 Font-Dateien in `assets/fonts/`:

### 1. **Astalight** (Titel-Font)
- **Dateiname:** `astalight.ttf`
- **Verwendung:** Haupt-Titel, Screen-Titel
- **Download:** Suche nach "Astalight font" oder nutze ähnliche Display-Fonts

### 2. **White on Black** (Menü-Font)  
- **Dateiname:** `whiteonblack.ttf`
- **Verwendung:** Menü-Optionen, Navigation
- **Download:** Suche nach "White on Black font"

### 3. **Monofonto** (HUD/Gameplay-Font)
- **Dateiname:** `monofonto.ttf`
- **Verwendung:** HUD, Score, Debug-Info
- **Download:** Suche nach "Monofonto font" oder nutze andere Monospace-Fonts

## 🔧 Installation

1. **Fonts herunterladen** von den jeweiligen Websites oder Font-Plattformen:
   - https://www.dafont.com/
   - https://www.1001fonts.com/
   - https://fonts.google.com/

2. **Umbenennen** (falls nötig):
   - Stelle sicher, dass die Dateinamen GENAU stimmen:
     - `astalight.ttf`
     - `whiteonblack.ttf`
     - `monofonto.ttf`

3. **Platzieren** in:
   ```
   F:\git\Space-Invaders\assets\fonts\
   ```

4. **Spiel starten** - Fonts werden automatisch geladen!

## ✅ Verzeichnis-Struktur

Nach der Installation sollte es so aussehen:

```
assets/fonts/
├── astalight.ttf         ← Titel-Font
├── whiteonblack.ttf      ← Menü-Font
├── monofonto.ttf         ← HUD-Font
├── README.md
├── QUICK_START.md
└── example_usage.py
```

## 🎨 Font-Zuordnung

| Bereich | Font | Größen | Verwendung |
|---------|------|--------|------------|
| **Titel** | Astalight | 96px, 64px, 48px | Haupt-Titel, Screen-Titel |
| **Menü** | White on Black | 48px, 32px, 24px | Menü-Optionen, Controls |
| **HUD** | Monofonto | 32px, 24px, 20px, 16px | Score, Health, Debug |

## 🔄 Fallback

Falls eine Font-Datei nicht gefunden wird, nutzt das Spiel automatisch den **System-Font** als Fallback. Das Spiel funktioniert also auch ohne die Custom-Fonts!

## 🧪 Testen

Nach dem Hinzufügen der Fonts, starte das Spiel:

```bash
python main.py
```

In der Konsole solltest du sehen:
```
Menu assets loaded successfully
  - Title font: Astalight
  - Menu font: White on Black
```

Falls "System Font" angezeigt wird, wurden die .ttf Dateien nicht gefunden.

## 📝 Alternative Font-Namen

Falls du andere Font-Dateien verwenden möchtest, passe `config/fonts.py` an:

```python
FONTS = {
    "title": {
        "file": "assets/fonts/deine_titel_font.ttf",  # Ändere hier
        ...
    },
    "menu": {
        "file": "assets/fonts/deine_menu_font.ttf",   # Ändere hier
        ...
    },
    "hud": {
        "file": "assets/fonts/deine_hud_font.ttf",    # Ändere hier
        ...
    }
}
```

## 🆓 Freie Alternativen

Falls du die Original-Fonts nicht findest, hier sind ähnliche freie Alternativen:

### Statt Astalight (Display Font):
- **Audiowide** (Google Fonts) - Futuristisch
- **Orbitron** (Google Fonts) - Space-Theme
- **Bungee** (Google Fonts) - Bold Display

### Statt White on Black (Clean Sans):
- **Roboto** (Google Fonts) - Modern
- **Open Sans** (Google Fonts) - Lesbar
- **Exo 2** (Google Fonts) - Tech-Look

### Statt Monofonto (Monospace):
- **Roboto Mono** (Google Fonts) - Modern Monospace
- **Source Code Pro** (Google Fonts) - Developer Font
- **JetBrains Mono** (Google Fonts) - Clean Monospace

## ⚖️ Lizenz-Hinweis

Stelle sicher, dass du die Fonts legal verwenden darfst:
- ✅ Freie Fonts (OFL, MIT, Public Domain) sind OK
- ✅ Google Fonts sind alle frei nutzbar
- ⚠️ Kommerzielle Fonts: Prüfe die Lizenz!

## 🐛 Probleme?

**Font wird nicht gefunden:**
- Prüfe den Dateinamen (Groß-/Kleinschreibung!)
- Prüfe den Pfad: `assets/fonts/`
- Prüfe die Dateiendung: `.ttf` (nicht `.otf`)

**Font sieht falsch aus:**
- Falsche Font-Datei? Prüfe welche Font tatsächlich geladen wurde
- Größe anpassen in `config/fonts.py`

**Spiel startet nicht:**
- Fonts sind optional! Lösche `config/fonts.py` import bei Problemen
- Nutze System-Font als Fallback

## 💡 Tipp

Für den besten Space-Invaders-Look empfehle ich:
- **Titel:** Eine bold/futuristische Display-Font
- **Menü:** Eine klare, gut lesbare Sans-Serif
- **HUD:** Eine Monospace-Font für technischen Look
