# AssetManager - Dokumentation

## Übersicht

Der AssetManager ist ein zentralisiertes System zur Verwaltung aller Spiel-Assets (Bilder, Sounds, Animationen).

## Features

- ✅ **Caching**: Automatisches Caching bereits geladener Assets
- ✅ **Lazy Loading**: Assets werden erst bei Bedarf geladen
- ✅ **Error Handling**: Fallback-Assets bei Ladefehlern
- ✅ **Type Safety**: Typsichere Asset-Zugriffe
- ✅ **Statistiken**: Performance-Monitoring und Debug-Infos
- ✅ **Dictionary-kompatibel**: Funktioniert wie ein Dictionary

## Verwendung

### Basis-Nutzung

```python
from manager import AssetManager

# AssetManager erstellen
manager = AssetManager()

# Bild laden
player_img = manager.load_image("assets/images/player.png", size=(64, 64))

# Sound laden
laser_sound = manager.load_sound("assets/sounds/laser.wav", volume=0.8)

# Animation laden
explosion_frames = manager.load_animation(
    "assets/images/explosion.png",
    cols=4, rows=4,
    frame_width=64, frame_height=64,
    scale=1.5
)
```

### Dictionary-ähnliche Syntax

```python
# Setzen
manager['player_img'] = player_img

# Abrufen
img = manager['player_img']

# Prüfen
if 'player_img' in manager:
    print("Asset existiert!")
```

### Migration vom alten System

```python
from assets.asset_loader import load_assets_v2

# Option 1: Neue Loader-Funktion
manager = load_assets_v2()

# Option 2: Bestehende Game-Instanz migrieren
from assets.asset_loader import migrate_to_asset_manager
manager = migrate_to_asset_manager(game)
```

### Statistiken abrufen

```python
# Statistiken anzeigen
manager.print_stats()

# Oder programmatisch abrufen
stats = manager.get_stats()
print(f"Geladene Assets: {stats['loaded']}")
print(f"Gecachte Zugriffe: {stats['cached']}")
```

## Schrittweise Migration

### Schritt 1: AssetManager parallel nutzen

```python
# In game.py __init__
from manager import AssetManager
from assets.load_assets import load_assets

# Behalte altes System
self.assets = load_assets()

# Füge neuen Manager hinzu
self.asset_manager = AssetManager()

# Migriere Assets
for key, value in self.assets.items():
    self.asset_manager[key] = value
```

### Schritt 2: Neue Assets mit Manager laden

```python
# Neue Assets direkt mit Manager laden
new_enemy_img = self.asset_manager.load_image(
    "assets/images/new_enemy.png",
    size=(48, 48)
)
self.asset_manager['enemy_new'] = new_enemy_img
```

### Schritt 3: Altes System ersetzen

```python
# Ersetze nach und nach
# ALT: img = self.assets['player_img']
# NEU: img = self.asset_manager['player_img']
```

## Best Practices

### 1. Lazy Loading für große Assets

```python
# Registriere Asset-Pfade
manager.register_asset('boss_img', 'assets/images/boss.png')

# Wird erst geladen, wenn benötigt
boss_img = manager['boss_img']
```

### 2. Cache-Management

```python
# Cache leeren wenn Speicher knapp
manager.clear_cache()

# Einzelnes Asset aus Cache entfernen
manager.remove('old_asset')
```

### 3. Error Handling

```python
# AssetManager gibt automatisch Fallback-Assets zurück
img = manager.load_image('not_existing.png')  # Gibt rotes Rechteck zurück
```

## API-Referenz

### Hauptmethoden

#### `load_image(path, size=None, convert_alpha=True, trim=False)`
Lädt ein Bild mit optionaler Größenanpassung.

#### `load_sound(path, volume=1.0)`
Lädt einen Sound-Effekt.

#### `load_animation(sheet_path, cols, rows, frame_width, frame_height, scale=1.0)`
Lädt eine Animation aus einem Spritesheet.

#### `get(key)`
Holt ein Asset aus dem Cache (mit Lazy Loading).

#### `set(key, value)`
Speichert ein Asset im Cache.

#### `has(key)`
Prüft ob ein Asset existiert.

#### `get_stats()`
Gibt Statistiken zurück.

#### `clear_cache()`
Leert den gesamten Cache.

## Performance-Tipps

1. **Registriere Assets früh**: Nutze `register_asset()` beim Start
2. **Nutze Caching**: Lade identische Assets nur einmal
3. **Überwache Statistiken**: Prüfe regelmäßig mit `get_stats()`
4. **Verwende trim**: Spare Speicher durch `trim=True`

## Beispiel: Vollständige Integration

```python
# game.py
from assets.asset_loader import load_assets_v2

class Game:
    def __init__(self):
        pygame.init()
        
        # Nutze neuen AssetManager
        self.assets = load_assets_v2()
        
        # Assets wie gewohnt verwenden
        self.player_img = self.assets['player_stage1']
        self.laser_sound = self.assets['laser_sound_start']
        
        # Statistiken beim Beenden ausgeben
        atexit.register(self.assets.print_stats)
```

## Troubleshooting

### Problem: Asset nicht gefunden
```python
# Prüfe ob Asset existiert
if 'my_asset' in manager:
    asset = manager['my_asset']
else:
    print("Asset nicht gefunden!")
```

### Problem: Zu viel Speicher
```python
# Cache regelmäßig leeren
if manager.get_stats()['total_cached'] > 1000:
    manager.clear_cache()
```

### Problem: Langsames Laden
```python
# Assets vorregistrieren und parallel laden
for key, path in asset_paths.items():
    manager.register_asset(key, path)
```
