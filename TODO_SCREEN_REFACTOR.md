# TODO: Screen System Refactoring

**Ziel:** Komplette Neustrukturierung des Screen-Systems für bessere Wartbarkeit und Übersichtlichkeit.

---

## ✅ Phase 1: Basis-Komponenten erstellen

### 1. Erstelle `config/stages.py`
**Status:** ⬜ Nicht gestartet

Neue Datei mit Stage-Konfiguration:

```python
# config/stages.py - Survivor Mode Stage Configuration

STAGE_NAMES = {
    1: "Rookie",
    2: "Veteran",
    3: "Elite",
    4: "Legend"
}

STAGE_SHIPS = {
    1: 1,  # Stage 1 → Ship 1
    2: 2,  # Stage 2 → Ship 2
    3: 3,  # Stage 3 → Ship 3
    4: 4   # Stage 4 → Ship 4
}

def get_stage_name(stage):
    """Gibt den Namen einer Stage zurück"""
    return STAGE_NAMES.get(stage, "Unknown")

def get_stage_ship(stage):
    """Gibt die Ship-ID für eine Stage zurück"""
    return STAGE_SHIPS.get(stage, 1)
```

**Danach:** Imports aktualisieren wo nötig (ship_select.py, game.py, menu.py)

---

### 2. Erstelle `system/saving_overlay.py`
**Status:** ⬜ Nicht gestartet

Transparente Komponente für Speicher-Animation.

**Klasse:** `SavingOverlay`

**Methoden:**
- `draw(screen, phase, progress, status_text)`
  - `phase`: 'local', 'online', 'done'
  - `progress`: 0.0 bis 1.0
  - `status_text`: z.B. 'Saving locally...'

**Features:**
- Zeichnet kleine Progress Bar (200x8px) unten rechts
- Transparentes Overlay über aktuellem Screen
- Farben: Grün (local), Blau (online), Gold (done)
- Font: monofonto rg.otf 14px

**Vorbild:** `draw_saving_progress()` aus `normal_mode_screens.py` (Zeilen 8-62)

---

### 3. GameMenu: Zentrale `draw_title()` Methode
**Status:** ⬜ Nicht gestartet

In `system/screens/menu.py` - GameMenu Klasse erweitern:

```python
def draw_title(self, screen, text, animated=False, color=None, y_position=None):
    """
    Zentrale Titel-Anzeige für alle Screens
    
    Args:
        screen: Pygame Surface
        text: Titel-Text
        animated: Bool - Mit Glow/Pulse Animation (wie NOVA STRIKE)
        color: Tuple - Hauptfarbe (default: (255, 255, 100))
        y_position: Int - Y-Position (default: height // 4)
    """
```

**Implementierung:**
- Falls `animated=True`: Nutze Code von `_draw_title_with_effects()` (Zeilen 414-496)
- Falls `animated=False`: Einfacher Titel mit Schatten
- Nutzt `self.title_font`
- Standard y_position: `screen.get_height() // 4`

---

### 4. GameMenu: Zentrale `draw_controls_text()` Methode anpassen
**Status:** ⬜ Nicht gestartet

In `system/screens/menu.py` - Methode `_draw_controls_text()` (Zeile 302) umbauen zu:

```python
def draw_controls_text(self, screen, text, y_position=None, color=None):
    """
    Zentrale Control-Text Anzeige für alle Screens
    
    Args:
        screen: Pygame Surface
        text: Control-Text (z.B. '[ENTER] Select - [ESC] Back')
        y_position: Int - Y-Position (default: height - 60)
        color: Tuple - Text-Farbe (default: (255, 255, 255))
    """
```

**Änderungen:**
- Entferne Unterstrich (wird public Methode)
- Mache y_position und color als optionale Parameter
- Default y_position: `screen.get_height() - scale(60)`
- Default color: `(255, 255, 255)`
- Nutzt `self.controls_font` und `draw_text_with_shadow()`

---

## ✅ Phase 2: Neue Screen-Dateien erstellen

### 5. Erstelle `system/screens/loading.py`
**Status:** ⬜ Nicht gestartet

Loading Screen beim Programmstart.

**Klasse:** `LoadingScreen`

**Methoden:**
- `draw(screen, phase, progress, message)`
  - Phases: 'assets', 'fonts', 'images', 'firebase', 'done'
  - Progress Bar mittig (400x20px)
  - Message unter der Bar
  - Farben je nach Phase

**Workflow in main.py:**
1. `pygame.init()`
2. Erstelle LoadingScreen
3. Für jede Lade-Phase:
   - Zeige Progress
   - Lade Assets/Fonts/etc.
   - Update Progress
4. 'done' → Fade zu Menu (0.5s)

**Wichtig:** `pygame.display.flip()` nach jedem `draw()`

---

### 6. Erstelle `system/screens/game_over.py`
**Status:** ⬜ Nicht gestartet

Game Over Screen mit integriertem Name Input.

**Klasse:** `GameOverScreen`

**Init:**
```python
self.player_name = ''
self.menu = None  # Referenz zu GameMenu für draw_title()
self.allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_')
```

**Methoden:**
- `handle_and_draw(screen, bg_scaled, stats_dict, menu_ref)`
  - `stats_dict = {'Score': 1000, 'Kills': 50, 'Level': 5, 'Time': '02:15.34'}`
  - Transparenter Hintergrund (alpha 200)
  - `menu_ref.draw_title(screen, 'GAME OVER', color=(255,100,100))`
  - Zeige alle Stats aus dict
  - Name Input Box mit Cursor
  - `menu_ref.draw_controls_text(screen, '[ENTER] Save - [ESC] Skip')`

**Event Handling:**
- ENTER: Name speichern (oder 'Player'), return 'submit'
- ESC: return 'skip'
- BACKSPACE: Zeichen löschen
- Buchstaben/Zahlen/_: Hinzufügen (max 15 Zeichen)
- Nur erlaubte Zeichen (`self.allowed_chars`)

**Vorbild:** `NormalModeNameInputScreen` (normal_mode_screens.py Zeilen 138-268)

---

### 7. Erstelle `system/screens/top10_normal.py`
**Status:** ⬜ Nicht gestartet

Normal Mode Top 10 Screen.

**Klasse:** `NormalTop10Screen`

**Init:**
```python
self.menu = None  # Referenz zu GameMenu
```

**Methoden:**
- `handle_and_draw(screen, bg_scaled, top10_list, menu_ref, came_from='menu')`
  - `menu_ref.draw_title(screen, 'TOP 10 HIGHSCORES', color=(255,215,0))`
  - Tabelle: RANK | NAME | SCORE | KILLS | LEVEL
  - Top 3: Gold/Silber/Bronze Farben
  - Controls abhängig von `came_from`:
    - `came_from='menu'`: '[ESC] Back to Menu'
    - `came_from='game'`: '[ENTER] Try Again - [ESC] Menu'

**Event Handling:**
- `came_from='menu'`: ESC → return 'menu'
- `came_from='game'`:
  - ENTER → return 'retry'
  - ESC → return 'menu'

**Vorbild:** `NormalModeTop10Screen` (normal_mode_screens.py Zeilen 271-378)

---

### 8. Erstelle `system/screens/top10_survivor.py`
**Status:** ⬜ Nicht gestartet

Survivor Mode Top 10 Screen.

**Klasse:** `SurvivorTop10Screen`

**Init:**
```python
self.menu = None  # Referenz zu GameMenu
```

**Methoden:**
- `handle_and_draw(screen, bg_scaled, top10_list, stage, menu_ref, came_from='menu')`
  - Import: `from config.stages import get_stage_name`
  - `stage_name = get_stage_name(stage)`
  - `menu_ref.draw_title(screen, f'TOP 10 - {stage_name.upper()}', color=(255,100,100))`
  - Tabelle: RANK | NAME | TIME | KILLS
  - Time Format: MM:SS.ms
  - Controls abhängig von `came_from`:
    - `came_from='menu'`: '[ESC] Back to Menu'
    - `came_from='game'`: '[ENTER] Try Again - [ESC] Menu'

**Event Handling:**
- `came_from='menu'`: ESC → return 'menu'
- `came_from='game'`:
  - ENTER → return 'retry'
  - ESC → return 'menu'

**Vorbild:** `_show_survivor_highscore_view()` (game.py Zeilen 1772-1857)

---

## ✅ Phase 3: game.py Integration

### 9. Aktualisiere `game.py`: online_available beim Start
**Status:** ⬜ Nicht gestartet

In `game/game.py` `__init__` Methode:

**1. Füge Attribute hinzu:**
```python
self.online_available = False
self.current_screen = 'loading'  # Tracking des aktuellen Screens
self.came_from = None  # Woher kamen wir (für Navigation)
```

**2. Online-Check EINMAL beim Start (nach Asset-Laden):**
```python
# Prüfe Firebase-Verbindung EINMAL
try:
    from system.online_highscore import get_online_manager
    manager = get_online_manager()
    self.online_available = manager.is_connected()
    if self.online_available:
        print('✓ Online mode available')
    else:
        print('⚠ Playing in offline mode')
except Exception as e:
    print(f'⚠ Firebase unavailable: {e}')
    self.online_available = False
```

---

### 10. game.py: Integriere LoadingScreen
**Status:** ⬜ Nicht gestartet

In `game/game.py` - Umbauen der Initialisierung:

**1. Import hinzufügen:**
```python
from system.screens.loading import LoadingScreen
```

**2. In `__init__` VOR Asset-Laden:**
```python
self.loading_screen = LoadingScreen()
self.current_screen = 'loading'
```

**3. Asset-Laden mit Progress-Updates:**
- Phase 'assets': load_assets() mit Progress-Callback
- Phase 'fonts': Font-Laden anzeigen
- Phase 'images': Bilder-Laden anzeigen
- Phase 'firebase': online_available Check
- Phase 'done': 0.5s warten, dann zu 'menu'

**4. Jeder Schritt ruft auf:**
```python
self.loading_screen.draw(self.screen, phase, progress, message)
pygame.display.flip()
```

---

### 11. game.py: Ersetze Name Input Screens durch GameOverScreen
**Status:** ⬜ Nicht gestartet

In `game/game.py`:

**1. Entferne alte Imports:**
```python
# ENTFERNEN:
from system.screens.normal_mode_screens import NormalModeNameInputScreen
from system.screens.survivor_screens import SurvivorNameInputScreen
```

**2. Neuer Import:**
```python
from system.screens.game_over import GameOverScreen
```

**3. In `__init__`:**
```python
# ERSETZEN:
self.game_over_screen = GameOverScreen()
# self.normal_mode_name_input_screen = ... # ENTFERNEN
# self.survivor_name_input_screen = ... # ENTFERNEN
```

**4. States ändern:**
- 'normal_name_input' → 'game_over' (mit mode='normal')
- 'survivor_name_input' → 'game_over' (mit mode='survivor')

**5. Aufruf:**
```python
stats_dict = {'Score': self.score, 'Kills': self.kills, 'Level': self.level}
action = self.game_over_screen.handle_and_draw(self.screen, self._bg_scaled, stats_dict, self.menu)
```

---

### 12. game.py: Integriere SavingOverlay
**Status:** ⬜ Nicht gestartet

In `game/game.py`:

**1. Import:**
```python
from system.saving_overlay import SavingOverlay
```

**2. In `__init__`:**
```python
self.saving_overlay = SavingOverlay()
```

**3. Nach Name Input ('submit'):**
```python
# Zeige Speicher-Animation
for phase in ['local', 'online', 'done']:
    for progress in [0.3, 0.6, 1.0]:
        # Game Over Screen weiter zeigen (als Hintergrund)
        self.game_over_screen.handle_and_draw(...)
        
        # Overlay darüber
        status = 'Saving locally...' if phase == 'local' else 'Uploading...' if phase == 'online' else '✓ Saved!'
        self.saving_overlay.draw(self.screen, phase, progress, status)
        
        pygame.display.flip()
        self.clock.tick(60)

# Dann zu Top 10
```

**4. Speichern:**
- Nutze `self.online_available` um zu entscheiden ob online gespeichert wird
- Kein erneuter `is_connected()` Check

---

### 13. game.py: Ersetze Top 10 Screens
**Status:** ⬜ Nicht gestartet

In `game/game.py`:

**1. Entferne alte Imports:**
```python
# ENTFERNEN:
from system.screens.normal_mode_screens import NormalModeTop10Screen
```

**2. Neue Imports:**
```python
from system.screens.top10_normal import NormalTop10Screen
from system.screens.top10_survivor import SurvivorTop10Screen
```

**3. In `__init__`:**
```python
self.top10_normal_screen = NormalTop10Screen()
self.top10_survivor_screen = SurvivorTop10Screen()
```

**4. Bei Aufruf:**
```python
# Normal Mode:
action = self.top10_normal_screen.handle_and_draw(
    self.screen, self._bg_scaled, top10_data, 
    self.menu, came_from=self.came_from
)

# Survivor Mode:
action = self.top10_survivor_screen.handle_and_draw(
    self.screen, self._bg_scaled, top10_data,
    self.survivor_selected_stage, self.menu,
    came_from=self.came_from
)
```

**5. Tracking:**
- Setze `self.came_from = 'game'` wenn aus Spiel
- Setze `self.came_from = 'menu'` wenn aus Menu

---

### 14. game.py: Cleanup - Entferne alte Screen-Logik
**Status:** ⬜ Nicht gestartet

In `game/game.py` aufräumen:

**1. ENTFERNEN:**
- `_show_survivor_highscore_view()` Methode (Zeilen ~1772-1857)
- Alte State-Handler für 'normal_name_input', 'survivor_name_input'
- `save_with_progress_animation()` Aufrufe
- Direkte `draw_saving_progress()` Aufrufe

**2. VEREINFACHEN:**
- `_handle_menu()` nur noch Menu-Actions
- Keine Screen-Drawing-Logik mehr in game.py
- Nur `Screen.handle_and_draw()` Aufrufe

**3. States bereinigen:**
- 'loading' → LoadingScreen
- 'menu' → GameMenu
- 'playing' → Spiel
- 'game_over' → GameOverScreen
- 'top10_normal' → NormalTop10Screen
- 'top10_survivor' → SurvivorTop10Screen
- 'ship_select' → ShipSelectScreen
- 'victory' → VictoryScreen

---

## ✅ Phase 4: Aufräumen und Testen

### 15. Lösche alte Screen-Dateien
**Status:** ⬜ Nicht gestartet

Aufräumen nach Migration:

**1. LÖSCHEN (nach Tests):**
- `system/screens/normal_mode_screens.py` (ersetzt durch game_over.py und top10_normal.py)
- `system/screens/survivor_screens.py` (ersetzt durch game_over.py und top10_survivor.py)

**2. BEHALTEN:**
- `system/screens/menu.py` (erweitert)
- `system/screens/ship_select.py` (bleibt)
- `system/screens/victory.py` (bleibt)

**3. NEU:**
- `system/screens/loading.py`
- `system/screens/game_over.py`
- `system/screens/top10_normal.py`
- `system/screens/top10_survivor.py`
- `system/saving_overlay.py`
- `config/stages.py`

**⚠️ VORSICHT:** Erst nach vollständigem Test löschen!

---

### 16. Aktualisiere `__init__.py` in system/screens
**Status:** ⬜ Nicht gestartet

`system/screens/__init__.py` updaten:

```python
# system/screens/__init__.py - Screen System Module

from .menu import GameMenu
from .ship_select import ShipSelectScreen
from .game_over import GameOverScreen
from .top10_normal import NormalTop10Screen
from .top10_survivor import SurvivorTop10Screen
from .victory import VictoryScreen
from .loading import LoadingScreen

__all__ = [
    'GameMenu',
    'ShipSelectScreen',
    'GameOverScreen',
    'NormalTop10Screen',
    'SurvivorTop10Screen',
    'VictoryScreen',
    'LoadingScreen'
]
```

---

### 17. Teste alle Screens und Workflows
**Status:** ⬜ Nicht gestartet

Vollständiger Test-Durchlauf:

#### 1. **Programmstart:**
- [ ] Loading Screen zeigt alle Phasen
- [ ] Geht zu Hauptmenü

#### 2. **Normal Mode:**
- [ ] Start → Spiel → Tod
- [ ] Game Over (Name Input) → Speichern
- [ ] Saving Overlay (local/online/done)
- [ ] Top 10 anzeigen
- [ ] Try Again funktioniert
- [ ] Menu funktioniert

#### 3. **Survivor Mode:**
- [ ] Start → Ship Select → Spiel → Tod
- [ ] Game Over (Name Input) → Speichern
- [ ] Saving Overlay (local/online/done)
- [ ] Top 10 (Stage X) anzeigen
- [ ] Try Again funktioniert
- [ ] Menu funktioniert

#### 4. **Highscores vom Menu:**
- [ ] Menu → Highscores → Normal → Top 10 → Back
- [ ] Menu → Highscores → Survivor → Stage Select → Top 10 (Stage X) → Back

#### 5. **Online/Offline:**
- [ ] Mit Firebase: Online speichern funktioniert
- [ ] Ohne Firebase: Nur lokal speichern
- [ ] online_available wird nur EINMAL geprüft

#### 6. **Navigation:**
- [ ] came_from korrekt gesetzt
- [ ] Controls zeigen richtige Optionen je nach came_from
- [ ] Try Again startet richtig
- [ ] Alle ESC/ENTER Kombinationen funktionieren

#### 7. **Visuals:**
- [ ] Transparente Overlays (Game Over, Saving)
- [ ] Titel-Animationen funktionieren
- [ ] Control-Texte sind konsistent
- [ ] Progress Bars zeigen korrekt an
- [ ] Farben sind konsistent

---

### 18. Commit und Push
**Status:** ⬜ Nicht gestartet

Nach erfolgreichem Test:

```bash
git add .
git commit -m "refactor: Restructure screen system

- Added config/stages.py for stage configuration
- Created saving_overlay.py as transparent component
- Centralized title/controls drawing in GameMenu
- Added loading screen for startup
- Unified game_over screen with name input
- Split top10 screens (normal/survivor)
- Removed old screen files
- Cleaned up game.py (only game logic)

Breaking Changes:
- Screen initialization changed
- State names updated
- Import paths changed"

git push
```

**Erstelle Patch Notes:** `patch-notes/v1.9.0_2025-10-16_screen-system-refactor.md`

---

## 📊 Fortschritt

- **Phase 1 (Basis):** 0/4 ⬜⬜⬜⬜
- **Phase 2 (Screens):** 0/4 ⬜⬜⬜⬜
- **Phase 3 (Integration):** 0/6 ⬜⬜⬜⬜⬜⬜
- **Phase 4 (Cleanup):** 0/4 ⬜⬜⬜⬜

**Gesamt:** 0/18 (0%)

---

## 🎯 Ziel-Architektur

```
system/
├── screens/
│   ├── __init__.py          # Exports
│   ├── menu.py              # Haupt/Pause/Highscore-Menüs + Zentrale draw_title/controls
│   ├── loading.py           # Loading Screen beim Start
│   ├── game_over.py         # Game Over + Name Input (transparent)
│   ├── top10_normal.py      # Normal Mode Top 10
│   ├── top10_survivor.py    # Survivor Mode Top 10
│   ├── ship_select.py       # Schiffsauswahl
│   └── victory.py           # Victory Screen
├── saving_overlay.py        # Speicher-Animation (Komponente)
└── ...

config/
├── stages.py                # Stage-Namen und Ship-Zuordnung
└── ...

game/
└── game.py                  # NUR Spiellogik, keine Screen-Details
```

---

## 💡 Wichtige Prinzipien

1. **Separation of Concerns:** game.py enthält NUR Spiellogik
2. **Single Responsibility:** Jeder Screen macht genau eine Sache
3. **DRY (Don't Repeat Yourself):** Zentrale draw_title/controls Methoden
4. **Komponenten vs. Screens:** Overlays sind Komponenten, keine Screens
5. **Klare Navigation:** came_from Parameter für kontextabhängige Controls
6. **Performance:** online_available nur EINMAL beim Start prüfen
7. **Konsistenz:** Alle Screens nutzen gleiche Basis-Methoden

---

**Viel Erfolg! 🚀**
