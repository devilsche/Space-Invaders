import json
import os
import pygame
from config.settings import REFERENCE_WIDTH, REFERENCE_HEIGHT

HIGHSCORE_FILE = "data/highscore.json"

# Lazy import für Firebase (nur wenn verfügbar)
_online_manager = None

def get_online_manager():
    """Lazy-load Firebase Manager"""
    global _online_manager
    if _online_manager is None:
        try:
            from system.online_highscore import get_online_manager
            _online_manager = get_online_manager()
        except Exception as e:
            print(f"⚠ Firebase not available: {e}")
            _online_manager = False  # Mark as unavailable
    return _online_manager if _online_manager is not False else None

# Dynamische Bildschirmgrößen-Tracking (zur Laufzeit änderbar)
_current_width = None
_current_height = None

def update_screen_size(width, height):
    """Aktualisiert die aktuellen Bildschirmabmessungen zur Laufzeit"""
    global _current_width, _current_height
    _current_width = width
    _current_height = height
    print(f"Screen size updated to: {width}x{height}")

# Dynamische Skalierungs-Utilities
def get_current_scale_factors():
    """Berechnet aktuelle Skalierungsfaktoren basierend auf Bildschirmgröße"""
    global _current_width, _current_height
    
    # Verwende Runtime-Größe falls verfügbar, sonst Pygame-Surface
    if _current_width is not None and _current_height is not None:
        current_width, current_height = _current_width, _current_height
    else:
        screen = pygame.display.get_surface()
        if screen is None:
            return 1.0, 1.0, 1.0
        current_width, current_height = screen.get_size()

    scale_x = current_width / REFERENCE_WIDTH
    scale_y = current_height / REFERENCE_HEIGHT
    
    # Verwende einen aggressiveren Skalierungsfaktor um schwarze Ränder zu vermeiden
    # Verwende den Durchschnitt statt minimum für bessere Ausnutzung
    scale_factor = (scale_x + scale_y) / 2.0
    
    # Mindest-Skalierung für bessere Lesbarkeit
    scale_factor = max(scale_factor, 1.2)

    return scale_factor, scale_x, scale_y

def scale(value):
    """Skaliert einen Wert uniform basierend auf aktueller Bildschirmgröße"""
    scale_factor, _, _ = get_current_scale_factors()
    return int(value * scale_factor)

def scale_x(value):
    """Skaliert einen X-Wert basierend auf aktuellem Breiten-Verhältnis"""
    _, scale_x_factor, _ = get_current_scale_factors()
    return int(value * scale_x_factor)

def scale_y(value):
    """Skaliert einen Y-Wert basierend auf aktuellem Höhen-Verhältnis"""
    _, _, scale_y_factor = get_current_scale_factors()
    return int(value * scale_y_factor)

def scale_pos(x, y):
    """Skaliert eine Position (x, y)"""
    return (scale_x(x), scale_y(y))

def scale_size(width, height):
    """Skaliert eine Größe (width, height) uniform"""
    return (scale(width), scale(height))

def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                data = json.load(f)
                return data.get("highscore", 0)
        except Exception:
            return 0
    return 0

def save_highscore(value):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            json.dump({"highscore": value}, f)
    except Exception:
        pass

SURVIVOR_HIGHSCORE_FILE = "data/survivor_highscores.json"

def load_survivor_highscores(stage=1):
    """Lädt die Top 10 Survivor Zeiten für eine bestimmte Stage"""
    if os.path.exists(SURVIVOR_HIGHSCORE_FILE):
        try:
            with open(SURVIVOR_HIGHSCORE_FILE, "r") as f:
                all_scores = json.load(f)
                # Filteriere nach Stage
                stage_scores = [s for s in all_scores if s.get("stage", 1) == stage]
                return sorted(stage_scores, key=lambda x: x["time"], reverse=True)[:10]
        except Exception:
            return []
    return []

def save_survivor_score(time_seconds, kills, player_name, stage=1):
    """
    Speichert eine neue Survivor Zeit mit Name, Kills und Stage.
    Speichert sowohl lokal als auch online (wenn verfügbar).
    
    Returns:
        tuple: (local_top_10, online_saved_successfully)
    """
    # 1. LOKAL SPEICHERN (immer, auch offline)
    if os.path.exists(SURVIVOR_HIGHSCORE_FILE):
        try:
            with open(SURVIVOR_HIGHSCORE_FILE, "r") as f:
                all_scores = json.load(f)
        except Exception:
            all_scores = []
    else:
        all_scores = []
    
    # Füge neuen Score hinzu
    new_score = {
        "time": time_seconds,
        "kills": kills,
        "name": player_name,
        "stage": stage
    }
    all_scores.append(new_score)
    
    # Behalte Top 10 pro Stage (insgesamt max 40 Einträge)
    stage_scores = {}
    for score in all_scores:
        s = score.get("stage", 1)
        if s not in stage_scores:
            stage_scores[s] = []
        stage_scores[s].append(score)
    
    # Sortiere jede Stage und behalte Top 10
    final_scores = []
    for stage_num, scores in stage_scores.items():
        top_10 = sorted(scores, key=lambda x: x["time"], reverse=True)[:10]
        final_scores.extend(top_10)
    
    try:
        with open(SURVIVOR_HIGHSCORE_FILE, "w") as f:
            json.dump(final_scores, f, indent=2)
    except Exception:
        pass
    
    # 2. ONLINE SPEICHERN (wenn verfügbar)
    online_success = False
    manager = get_online_manager()
    if manager and manager.is_connected():
        try:
            online_success = manager.save_highscore(
                name=player_name,
                time=time_seconds,
                kills=kills,
                stage=stage
            )
            if online_success:
                print(f"✓ Highscore saved online: {player_name} - {time_seconds:.2f}s")
        except Exception as e:
            print(f"⚠ Failed to save online: {e}")
    
    # Gib die Top 10 für die aktuelle Stage zurück
    local_top_10 = sorted([s for s in final_scores if s.get("stage", 1) == stage], 
                          key=lambda x: x["time"], reverse=True)[:10]
    
    return local_top_10, online_success


def get_global_highscores(stage=None, limit=10):
    """
    Lädt globale Highscores von Firebase.
    Fallback zu lokalen Scores wenn offline.
    
    Args:
        stage: Filter by stage (None = all stages)
        limit: Maximum number of scores
        
    Returns:
        tuple: (scores_list, is_online)
    """
    manager = get_online_manager()
    
    # Versuche online zu laden
    if manager and manager.is_connected():
        try:
            scores = manager.get_top_scores(stage=stage, limit=limit)
            if scores:
                return scores, True
        except Exception as e:
            print(f"⚠ Failed to load online scores: {e}")
    
    # Fallback zu lokalen Scores
    local_scores = load_survivor_highscores()
    
    # Filter by stage if specified
    if stage is not None:
        local_scores = [s for s in local_scores if s.get("stage", 1) == stage]
    
    # Sort and limit
    local_scores = sorted(local_scores, key=lambda x: x["time"], reverse=True)[:limit]
    
    return local_scores, False
