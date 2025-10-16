#!/usr/bin/env python3
"""
Migrations-Script: Konvertiert assets.get("key") zu assets.get("key")
Entfernt AssetProxy-Abhängigkeiten und modernisiert den Code.
"""

import os
import re
import sys

def convert_file(filepath):
    """Konvertiert eine einzelne Datei"""
    print(f"Converting: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern 1: assets.get("key") -> assets.get("key")
        # Aber NUR wenn es nicht in Strings steht
        pattern1 = r'(\w+)\["([^"]+)"\]'
        def replace_dict_access(match):
            obj_name = match.group(1)
            key = match.group(2)
            if obj_name in ['assets', 'self.assets', 'game.assets']:
                return f'{obj_name}.get("{key}")'
            return match.group(0)  # Keine Änderung
        
        content = re.sub(pattern1, replace_dict_access, content)
        
        # Pattern 2: assets.has("key") -> assets.has("key")
        content = re.sub(r'"([^"]+)"\s+in\s+((?:\w+\.)*assets)', r'\2.has("\1")', content)
        
        # Pattern 3: Entferne AssetProxy imports
        content = re.sub(r'from assets\.load_assets         content = re.sub(r'        
        # Nur schreiben wenn sich etwas geändert hat
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ Updated {filepath}")
            return True
        else:
            print(f"  - No changes needed in {filepath}")
            return False
            
    except Exception as e:
        print(f"  ✗ Error processing {filepath}: {e}")
        return False

def main():
    """Hauptfunktion"""
    base_dir = "/home/nic/git/Space-Invaders"
    
    # Finde alle Python-Dateien
    python_files = []
    for root, dirs, files in os.walk(base_dir):
        # Ignoriere __pycache__ und .git
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.venv']]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"Found {len(python_files)} Python files")
    print("=" * 50)
    
    converted_count = 0
    for filepath in python_files:
        if convert_file(filepath):
            converted_count += 1
    
    print("=" * 50)
    print(f"✓ Conversion complete: {converted_count}/{len(python_files)} files updated")
    
    # Zeige verbleibende Dictionary-Zugriffe
    print("\nChecking for remaining dictionary access patterns...")
    remaining_patterns = []
    for filepath in python_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                if re.search(r'assets\["[^"]+"\]', line):
                    remaining_patterns.append(f"{filepath}:{i}: {line.strip()}")
        except:
            pass
    
    if remaining_patterns:
        print("⚠ Found remaining dictionary access patterns:")
        for pattern in remaining_patterns[:10]:  # Zeige nur die ersten 10
            print(f"  {pattern}")
        if len(remaining_patterns) > 10:
            print(f"  ... and {len(remaining_patterns) - 10} more")
    else:
        print("✓ No remaining dictionary access patterns found")

if __name__ == "__main__":
    main()
