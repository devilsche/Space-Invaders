# assets/asset_loader.py
"""
Integration zwischen dem alten load_assets() und dem neuen AssetManager
Bietet Abwärtskompatibilität während der Migration
"""
from manager.asset_manager import AssetManager
from assets.load_assets import load_assets as legacy_load_assets


def load_assets_v2() -> AssetManager:
    """
    Lädt Assets mit dem neuen AssetManager
    Kompatibel mit dem alten Dictionary-basiertem System
    
    Returns:
        AssetManager mit allen geladenen Assets
    """
    manager = AssetManager()
    
    # Lade Assets mit der alten Methode
    legacy_assets = legacy_load_assets()
    
    # Übertrage alle Assets in den Manager
    for key, value in legacy_assets.items():
        manager.set(key, value)
    
    # Gib Statistiken aus
    manager.print_stats()
    
    return manager


def migrate_to_asset_manager(game_instance):
    """
    Hilfsfunktion zur Migration eines bestehenden Spiels
    
    Args:
        game_instance: Instanz der Game-Klasse mit .assets Dictionary
        
    Returns:
        AssetManager mit migrierten Assets
    """
    manager = AssetManager()
    
    if hasattr(game_instance, 'assets') and isinstance(game_instance.assets, dict):
        for key, value in game_instance.assets.items():
            manager.set(key, value)
        
        print(f"✓ {len(game_instance.assets)} Assets zum AssetManager migriert")
    
    return manager
