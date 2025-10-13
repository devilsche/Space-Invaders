# Fonts Directory

This directory contains TrueType fonts (.ttf) used in the game.

## Supported Fonts

The game will automatically search for and use the first available font:
- `arial.ttf` (Windows system font)
- `roboto.ttf` (Google font)
- `dejavusans.ttf` (Open source font)

If no font is found, the game falls back to pygame's default system font.

## Adding Custom Fonts

### Free Font Options:

1. **DejaVu Sans** (Recommended - Open Source)
   - Download: https://dejavu-fonts.github.io/
   - License: Free for any use
   - Great Unicode support (includes arrows: ↑↓←→)
   
2. **Roboto** (Google Font)
   - Download: https://fonts.google.com/specimen/Roboto
   - License: Apache License 2.0
   - Modern, clean design

3. **Noto Sans** (Google Font)
   - Download: https://fonts.google.com/noto/specimen/Noto+Sans
   - License: SIL Open Font License
   - Excellent Unicode coverage

4. **Liberation Sans** (Red Hat)
   - Download: https://github.com/liberationfonts/liberation-fonts
   - License: SIL Open Font License
   - Metric-compatible with Arial

### Installation:

1. Download a .ttf file from one of the above sources
2. Place it in this `assets/fonts/` directory
3. Rename it to one of the supported names (arial.ttf, roboto.ttf, dejavusans.ttf)
   OR update `assets/load_assets.py` to add your custom font name

### Windows Users:

You can also copy Arial from your Windows fonts folder:
```
C:\Windows\Fonts\arial.ttf
```
to:
```
assets/fonts/arial.ttf
```

## Usage in Code

Fonts are automatically loaded in `assets/load_assets.py`:

```python
# Access in your code via assets:
menu_font = assets["menu_font_24"]      # Size 24
menu_font = assets["menu_font_32"]      # Size 32
title_font = assets["title_font_48"]    # Size 48
title_font = assets["title_font_64"]    # Size 64
```

Or load custom sizes:
```python
from manager.asset_manager import AssetManager
manager = AssetManager()
custom_font = manager.load_font("assets/fonts/arial.ttf", 40)
```

## Font Sizes Available

Pre-loaded sizes:
- **24px** - Small text (controls, hints)
- **32px** - Menu options
- **48px** - Subtitles, important text
- **64px** - Title screens, headers

## Unicode Support

If you want to use special characters like arrows (↑↓←→), make sure your chosen font supports Unicode. 

Good options:
- ✅ DejaVu Sans (excellent Unicode support)
- ✅ Noto Sans (comprehensive coverage)
- ⚠️ Arial (basic Unicode, no fancy arrows)
- ❌ pygame default font (limited Unicode)

## License Notes

- **DejaVu Sans**: Free for any use (public domain derivative)
- **Roboto/Noto**: Apache 2.0 / OFL (free for commercial use)
- **Arial**: Licensed by Microsoft (OK to bundle if you own Windows)

**Recommendation**: Use **DejaVu Sans** for best compatibility and legal clarity.
