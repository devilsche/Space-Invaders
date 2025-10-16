#!/usr/bin/env python
"""
Test-Skript für den AssetManager
Zeigt Verwendung und testet Funktionalität
"""
import pygame
import sys
import os

# Füge Parent-Verzeichnis zum Path hinzu
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manager import AssetManager
from assets.asset_loader import load_assets_v2


def test_basic_usage():
    """Test: Basis-Funktionalität"""
    print("\n=== Test 1: Basis-Funktionalität ===")
    
    pygame.init()
    manager = AssetManager()
    
    # Test: Bild laden
    try:
        img = manager.load_image("assets/images/background.png")
        print(f"✓ Bild geladen: {img.get_size()}")
    except Exception as e:
        print(f"✗ Fehler beim Laden: {e}")
    
    # Test: Sound laden
    try:
        sound = manager.load_sound("assets/sound/laser_shoot.wav")
        print(f"✓ Sound geladen: {sound is not None}")
    except Exception as e:
        print(f"✗ Fehler beim Laden: {e}")
    
    manager.print_stats()


def test_caching():
    """Test: Caching-Mechanismus"""
    print("\n=== Test 2: Caching ===")
    
    pygame.init()
    manager = AssetManager()
    
    # Erstes Laden
    img1 = manager.load_image("assets/images/background.png")
    stats1 = manager.get_stats()
    
    # Zweites Laden (sollte aus Cache kommen)
    img2 = manager.load_image("assets/images/background.png")
    stats2 = manager.get_stats()
    
    print(f"✓ Erstes Laden: {stats1['loaded']} neu geladen")
    print(f"✓ Zweites Laden: {stats2['cached']} aus Cache")
    print(f"✓ Identisches Objekt: {img1 is img2}")
    
    manager.print_stats()


def test_dictionary_syntax():
    """Test: Dictionary-ähnliche Syntax"""
    print("\n=== Test 3: Dictionary-Syntax ===")
    
    pygame.init()
    manager = AssetManager()
    
    # Setzen
    test_surf = pygame.Surface((64, 64))
    test_surf.fill((255, 0, 0))
    manager['test_image'] = test_surf
    
    # Abrufen
    retrieved = manager['test_image']
    
    # Prüfen
    exists = 'test_image' in manager
    
    print(f"✓ Setzen: {test_surf is not None}")
    print(f"✓ Abrufen: {retrieved is not None}")
    print(f"✓ Existenz-Check: {exists}")
    print(f"✓ Identisch: {test_surf is retrieved}")


def test_animation_loading():
    """Test: Animation-Laden"""
    print("\n=== Test 4: Animation ===")
    
    pygame.init()
    manager = AssetManager()
    
    try:
        # Versuche eine Explosion zu laden
        frames = manager.load_animation(
            "assets/images/exp2.png",
            cols=4, rows=4,
            frame_width=128, frame_height=128,
            scale=0.5
        )
        
        print(f"✓ Animation geladen: {len(frames)} Frames")
        print(f"✓ Frame-Größe: {frames[0].get_size()}")
    except Exception as e:
        print(f"✗ Fehler beim Laden: {e}")
    
    manager.print_stats()


def test_error_handling():
    """Test: Error Handling"""
    print("\n=== Test 5: Error Handling ===")
    
    pygame.init()
    manager = AssetManager()
    
    # Versuche nicht-existierende Datei zu laden
    img = manager.load_image("not_existing_file.png")
    print(f"✓ Fallback-Bild erhalten: {img is not None}")
    print(f"✓ Fallback-Größe: {img.get_size()}")
    
    stats = manager.get_stats()
    print(f"✓ Fehler gezählt: {stats['failed']}")
    
    manager.print_stats()


def test_migration():
    """Test: Migration vom alten System"""
    print("\n=== Test 6: Migration ===")
    
    pygame.init()
    
    try:
        # Lade mit neuer Funktion
        manager = load_assets_v2()
        
        # Prüfe bekannte Assets
        has_player = 'player_stage1' in manager
        has_laser = 'laser_img' in manager
        
        print(f"✓ Player-Asset gefunden: {has_player}")
        print(f"✓ Laser-Asset gefunden: {has_laser}")
        
        manager.print_stats()
    except Exception as e:
        print(f"✗ Fehler bei Migration: {e}")


def test_lazy_loading():
    """Test: Lazy Loading"""
    print("\n=== Test 7: Lazy Loading ===")
    
    pygame.init()
    manager = AssetManager()
    
    # Registriere Asset ohne es zu laden
    manager.register_asset('lazy_bg', 'assets/images/background.png')
    
    stats_before = manager.get_stats()
    print(f"✓ Registriert (nicht geladen): {stats_before['registered']}")
    
    # Jetzt laden
    img = manager['lazy_bg']
    
    stats_after = manager.get_stats()
    print(f"✓ Jetzt geladen: {stats_after['loaded']}")
    print(f"✓ Bild erhalten: {img is not None}")


def test_memory_management():
    """Test: Speicherverwaltung"""
    print("\n=== Test 8: Speicherverwaltung ===")
    
    pygame.init()
    manager = AssetManager()
    
    # Lade mehrere Assets
    for i in range(5):
        surf = pygame.Surface((100, 100))
        manager[f'test_{i}'] = surf
    
    stats_before = manager.get_stats()
    print(f"✓ Assets vor Clear: {stats_before['total_cached']}")
    
    # Cache leeren
    manager.clear_cache()
    
    stats_after = manager.get_stats()
    print(f"✓ Assets nach Clear: {stats_after['total_cached']}")


def run_all_tests():
    """Führt alle Tests aus"""
    print("\n" + "="*50)
    print("  AssetManager - Test Suite")
    print("="*50)
    
    tests = [
        test_basic_usage,
        test_caching,
        test_dictionary_syntax,
        test_animation_loading,
        test_error_handling,
        test_migration,
        test_lazy_loading,
        test_memory_management
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n✗ Test fehlgeschlagen: {test.__name__}")
            print(f"   Fehler: {e}")
            failed += 1
    
    print("\n" + "="*50)
    print(f"  Ergebnis: {passed} Tests bestanden, {failed} fehlgeschlagen")
    print("="*50 + "\n")


if __name__ == "__main__":
    run_all_tests()
