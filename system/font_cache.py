# system/font_cache.py - Font Helper mit Scaling Support
"""
Zentrale Font-Verwaltung mit Scaling-Support.
Verwendet gecachte Fonts aus assets und skaliert sie bei Bedarf.
"""
import pygame


def get_font(assets, font_key, scale_factor=1.0):
    """
    Holt einen Font aus Assets und skaliert ihn optional.
    
    Args:
        assets: Asset-Dictionary
        font_key: Key des Fonts (z.B. 'font_title_large')
        scale_factor: Skalierungsfaktor (default: 1.0)
        
    Returns:
        pygame.Font-Objekt (skaliert falls scale_factor != 1.0)
    """
    base_font = assets.get(font_key)
    
    if base_font is None:
        # Fallback
        return pygame.font.Font(None, int(32 * scale_factor))
    
    # Wenn keine Skalierung nötig, gib Original zurück
    if scale_factor == 1.0:
        return base_font
    
    # Für skalierte Fonts: Erstelle neuen Font mit skalierter Größe
    # (pygame.Font hat keine Methode zur Größenabfrage, daher speichern wir Original-Größen)
    size = base_font.get_height()  # Ungefähre Größe
    scaled_size = int(size * scale_factor)
    
    # Versuche den ursprünglichen Font-Pfad zu verwenden
    # Achtung: Wenn der Font aus assets kommt, müssen wir den Pfad kennen
    # Für jetzt: Erstelle neuen Font basierend auf Font-Typ
    
    try:
        # Versuche Pfad aus Font zu extrahieren (funktioniert nur bei benutzerdefinierten Fonts)
        if 'Astralight' in font_key or 'title' in font_key:
            return pygame.font.Font("assets/fonts/Astralight.ttf", scaled_size)
        elif 'subtitle' in font_key or 'White' in str(base_font):
            return pygame.font.Font("assets/fonts/White On Black.ttf", scaled_size)
        elif 'mono' in font_key:
            return pygame.font.Font("assets/fonts/monofonto rg.otf", scaled_size)
        elif 'controls' in font_key:
            return pygame.font.Font("assets/fonts/KGRedHands.ttf", scaled_size)
        else:
            return pygame.font.Font(None, scaled_size)
    except:
        return pygame.font.Font(None, scaled_size)


def get_scaled_fonts(assets, ui_scale):
    """
    Gibt ein Dict mit allen häufig genutzten Fonts in der richtigen Größe zurück.
    
    Args:
        assets: Asset-Dictionary
        ui_scale: UI-Skalierungsfaktor
        
    Returns:
        Dict mit Font-Keys und skalierten Fonts
    """
    return {
        'title': get_font(assets, 'font_title_large', ui_scale),
        'subtitle': get_font(assets, 'font_subtitle_medium', ui_scale),
        'stats': get_font(assets, 'font_mono_medium', ui_scale),
        'name': get_font(assets, 'font_mono_large', ui_scale),
        'prompt': get_font(assets, 'font_subtitle_medium', ui_scale),
        'rank': get_font(assets, 'font_mono_normal', ui_scale),
        'controls': get_font(assets, 'font_controls_normal', ui_scale),
    }
