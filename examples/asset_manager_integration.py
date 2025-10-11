# examples/asset_manager_integration.py
"""
Beispiele für die Integration des AssetManagers in das bestehende Spiel
"""
import pygame
from manager import AssetManager


# ============================================================
# Beispiel 1: Minimale Integration (Abwärtskompatibel)
# ============================================================

def example_minimal_integration():
    """
    Zeigt die minimale Integration ohne Änderung des bestehenden Codes
    """
    from assets.asset_loader import load_assets_v2
    
    class Game:
        def __init__(self):
            pygame.init()
            
            # Einfach die neue Funktion verwenden
            # Der AssetManager verhält sich wie ein Dictionary!
            self.assets = load_assets_v2()
            
            # Bestehender Code funktioniert weiter
            player_img = self.assets['player_stage1']
            laser_sound = self.assets['laser_sound_start']
            
            print("✓ Minimale Integration erfolgreich!")
            self.assets.print_stats()


# ============================================================
# Beispiel 2: Schrittweise Migration
# ============================================================

def example_gradual_migration():
    """
    Zeigt schrittweise Migration mit parallelem Betrieb
    """
    from assets.load_assets import load_assets
    
    class Game:
        def __init__(self):
            pygame.init()
            
            # Behalte altes System
            self.assets_old = load_assets()
            
            # Initialisiere neuen Manager
            self.assets = AssetManager()
            
            # Migriere bestehende Assets
            for key, value in self.assets_old.items():
                self.assets[key] = value
            
            print(f"✓ {len(self.assets_old)} Assets migriert")
            
            # Ab jetzt beide Systeme parallel nutzbar
            # Altes System: self.assets_old['key']
            # Neues System: self.assets['key']
            
            self.assets.print_stats()


# ============================================================
# Beispiel 3: Optimierte Nutzung mit Lazy Loading
# ============================================================

def example_optimized_usage():
    """
    Zeigt optimierte Nutzung mit Lazy Loading und Preloading
    """
    class Game:
        def __init__(self):
            pygame.init()
            self.assets = AssetManager()
            
            # Registriere wichtige Assets für Lazy Loading
            self._register_core_assets()
            
            # Preload nur kritische Assets
            self._preload_menu_assets()
        
        def _register_core_assets(self):
            """Registriert alle Assets für Lazy Loading"""
            # Player Assets
            self.assets.register_asset('player_img', 'assets/images/player.png')
            
            # Enemy Assets
            self.assets.register_asset('enemy_basic', 'assets/images/enemy/basic.png')
            
            # Sounds
            self.assets.register_asset('laser_sound', 'assets/sound/laser_shoot.wav')
            
            print("✓ Core-Assets registriert")
        
        def _preload_menu_assets(self):
            """Lädt nur Menu-Assets beim Start"""
            # Diese werden sofort geladen
            self.assets.load_image('assets/images/background.png')
            
            print("✓ Menu-Assets vorgeladen")
        
        def start_level(self):
            """Lädt Level-spezifische Assets bei Bedarf"""
            # Diese werden erst jetzt geladen
            enemy_img = self.assets['enemy_basic']
            laser_sound = self.assets['laser_sound']
            
            print("✓ Level-Assets geladen")
            self.assets.print_stats()


# ============================================================
# Beispiel 4: Dynamisches Asset-Loading (für große Levels)
# ============================================================

def example_dynamic_loading():
    """
    Zeigt dynamisches Laden/Entladen für große Levels
    """
    class Game:
        def __init__(self):
            pygame.init()
            self.assets = AssetManager()
            self.current_level = None
        
        def load_level(self, level_num: int):
            """Lädt Level-spezifische Assets"""
            # Vorheriges Level entladen
            if self.current_level is not None:
                self._unload_level(self.current_level)
            
            # Neues Level laden
            self.current_level = level_num
            
            if level_num == 1:
                self.assets.load_image(f'assets/images/level{level_num}_bg.png')
                self.assets.load_image(f'assets/images/enemy_type1.png')
            elif level_num == 2:
                self.assets.load_image(f'assets/images/level{level_num}_bg.png')
                self.assets.load_image(f'assets/images/enemy_type2.png')
            
            print(f"✓ Level {level_num} Assets geladen")
            self.assets.print_stats()
        
        def _unload_level(self, level_num: int):
            """Entfernt Level-spezifische Assets"""
            # Entferne alte Assets um Speicher freizugeben
            self.assets.remove(f'level{level_num}_bg')
            self.assets.remove(f'enemy_type{level_num}')
            
            print(f"✓ Level {level_num} Assets entladen")


# ============================================================
# Beispiel 5: Performance-Monitoring
# ============================================================

def example_performance_monitoring():
    """
    Zeigt Performance-Monitoring und automatische Optimierung
    """
    class Game:
        def __init__(self):
            pygame.init()
            self.assets = AssetManager()
            self.frame_count = 0
        
        def update(self):
            """Game-Update mit Performance-Check"""
            self.frame_count += 1
            
            # Alle 600 Frames (ca. 10 Sekunden bei 60 FPS)
            if self.frame_count % 600 == 0:
                self._check_performance()
        
        def _check_performance(self):
            """Prüft Asset-Performance und optimiert bei Bedarf"""
            stats = self.assets.get_stats()
            
            print(f"\n--- Performance Check (Frame {self.frame_count}) ---")
            print(f"Gecachte Assets: {stats['total_cached']}")
            print(f"Cache-Hit-Rate: {stats['cached']} / {stats['loaded'] + stats['cached']}")
            
            # Wenn zu viele Assets im Cache
            if stats['total_cached'] > 100:
                print("⚠ Zu viele Assets im Cache - starte Cleanup")
                # Behalte nur die wichtigsten Assets
                self._cleanup_unused_assets()
        
        def _cleanup_unused_assets(self):
            """Entfernt selten genutzte Assets"""
            # Implementierung abhängig von deinen Needs
            # Beispiel: Entferne Assets die > 5 Minuten nicht genutzt wurden
            pass


# ============================================================
# Beispiel 6: Custom Asset Types
# ============================================================

def example_custom_asset_types():
    """
    Zeigt Erweiterung des AssetManagers für eigene Asset-Typen
    """
    class ExtendedAssetManager(AssetManager):
        """Erweiterter AssetManager mit zusätzlichen Funktionen"""
        
        def load_tileset(self, path: str, tile_size: int) -> list:
            """Lädt ein Tileset und teilt es in einzelne Tiles"""
            cache_key = f"tileset_{path}_{tile_size}"
            
            if cache_key in self._cache:
                return self._cache[cache_key]
            
            try:
                sheet = pygame.image.load(path).convert_alpha()
                width, height = sheet.get_size()
                
                tiles = []
                for y in range(0, height, tile_size):
                    for x in range(0, width, tile_size):
                        tile = sheet.subsurface(
                            pygame.Rect(x, y, tile_size, tile_size)
                        ).copy()
                        tiles.append(tile)
                
                self._cache[cache_key] = tiles
                self._stats['loaded'] += 1
                
                return tiles
            except Exception as e:
                print(f"Fehler beim Laden des Tilesets: {e}")
                return []
        
        def load_font(self, path: str, size: int) -> pygame.font.Font:
            """Lädt eine Font-Datei"""
            cache_key = f"font_{path}_{size}"
            
            if cache_key in self._cache:
                return self._cache[cache_key]
            
            try:
                font = pygame.font.Font(path, size)
                self._cache[cache_key] = font
                self._stats['loaded'] += 1
                return font
            except Exception as e:
                print(f"Fehler beim Laden der Font: {e}")
                return pygame.font.Font(None, size)


# ============================================================
# Test-Runner
# ============================================================

def run_examples():
    """Führt alle Beispiele aus"""
    print("\n" + "="*60)
    print("  AssetManager - Integration Examples")
    print("="*60)
    
    examples = [
        ("Minimale Integration", example_minimal_integration),
        ("Schrittweise Migration", example_gradual_migration),
        ("Optimierte Nutzung", example_optimized_usage),
        ("Dynamisches Loading", example_dynamic_loading),
        ("Performance-Monitoring", example_performance_monitoring),
    ]
    
    for name, example_func in examples:
        print(f"\n\n{'='*60}")
        print(f"  {name}")
        print('='*60)
        try:
            example_func()
        except Exception as e:
            print(f"✗ Fehler: {e}")


if __name__ == "__main__":
    run_examples()
