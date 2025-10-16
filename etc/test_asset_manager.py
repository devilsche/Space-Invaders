#!/usr/bin/env python3
"""
Test des AssetManagers ohne Spiel zu starten
"""

import pygame
pygame.init()

from ..assets.load_assets import load_assets

print("Testing AssetManager...")

try:
    assets = load_assets()
    print(f"✓ Assets loaded successfully: {type(assets)}")
    
    # Test einige Asset-Zugriffe
    bg = assets.get("background_img")
    print(f"✓ Background: {type(bg)}")
    
    shield_frames = assets.get("shield_frames")
    print(f"✓ Shield frames: {type(shield_frames)}")
    
    shield_fps = assets.get("shield_fps")
    print(f"✓ Shield FPS: {shield_fps}")
    
    # Test has/contains
    has_bg = assets.has("background_img")
    print(f"✓ Has background: {has_bg}")
    
    contains_bg = "background_img" in assets
    print(f"✓ Contains background: {contains_bg}")
    
    # Test nicht-existierendes Asset
    missing = assets.get("missing_asset", "default")
    print(f"✓ Missing asset with default: {missing}")
    
    print("✅ All tests passed!")
    
except Exception as e:
    import traceback
    print(f"❌ Error: {e}")
    traceback.print_exc()
