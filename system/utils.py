import json
import os
import sys
import pygame
from config.settings import GAME_CONFIG


def resource_path(relative_path):
    """
    Gibt den korrekten Pfad zu einer Ressource zurück.
    Funktioniert sowohl im Entwicklungsmodus als auch in PyInstaller-Bundles.
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller Bundle - Assets sind in temporärem Ordner
        return os.path.join(sys._MEIPASS, relative_path)
    # Entwicklungsmodus - normaler relativer Pfad
    return relative_path


REFERENCE_WIDTH  = GAME_CONFIG["REFERENCE_WIDTH"]
REFERENCE_HEIGHT = GAME_CONFIG["REFERENCE_HEIGHT"]

HIGHSCORE_FILE = "data/highscore.json"

# Firebase-Manager wird jetzt zentral verwaltet
def get_online_manager():
    """
    Holt den Firebase-Manager aus der zentralen Verwaltung.
    Keine Lazy-Loading mehr - Verfügbarkeit wurde beim Start geprüft.
    """
    from system.firebase_manager import get_firebase_manager
    return get_firebase_manager()

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
    """
    Lädt den höchsten Normal Mode Highscore.

    Priorität:
    1. Online von Firebase (wenn verbunden)
    2. Lokale Datei (neues Format - Liste von Scores)
    3. Lokale Datei (altes Format - {"highscore": 0})

    Returns:
        int: Der höchste Score
    """
    best_score = 0

    # 1. Versuche Online-Daten zu holen (nur wenn Firebase verfügbar)
    from system.firebase_manager import is_firebase_available
    if is_firebase_available():
        try:
            manager = get_online_manager()
            if manager:
                online_scores = manager.get_top_scores(stage=0, limit=1)
                if online_scores and len(online_scores) > 0:
                    best_score = online_scores[0].get('score', 0)
                    print(f"✓ Loaded highscore from Firebase: {best_score}")
                    return best_score
        except Exception as e:
            print(f"⚠ Could not load highscore from Firebase: {e}")

    # 2. Fallback: Lokale Datei laden
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                data = json.load(f)

                # Neues Format: Liste von Scores
                if isinstance(data, list) and len(data) > 0:
                    # Sortiere nach Score (primär) und Kills (sekundär)
                    sorted_scores = sorted(data, key=lambda x: (x.get("score", 0), x.get("kills", 0)), reverse=True)
                    best_score = sorted_scores[0].get("score", 0)
                    print(f"✓ Loaded highscore from local file (new format): {best_score}")
                    return best_score

                # Altes Format: {"highscore": 12345}
                elif isinstance(data, dict):
                    best_score = data.get("highscore", 0)
                    print(f"✓ Loaded highscore from local file (old format): {best_score}")
                    return best_score

        except Exception as e:
            print(f"⚠ Error loading local highscore: {e}")

    print(f"✓ No highscore found, starting with: {best_score}")
    return best_score

def load_normal_top10():
    """
    Lädt die Top 10 Normal Mode Highscores.

    Returns:
        list: Top 10 Scores sortiert nach Score (primär) und Kills (sekundär)
    """
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    # Neues Format: Liste von Einträgen
                    # Stelle sicher, dass alle Felder vorhanden sind
                    for entry in data:
                        if "kills" not in entry:
                            entry["kills"] = 0
                        if "level" not in entry:
                            entry["level"] = 1
                    return data[:10]  # Top 10
                else:
                    # Altes/Unbekanntes Format - ignorieren
                    print(f"[WARNING] Ignoring old/invalid highscore format in {HIGHSCORE_FILE}")
                    return []
        except Exception:
            return []
    return []


def save_normal_score(score, player_name, kills=0, level=1):
    """
    Speichert einen Normal Mode Score mit Name, Kills und Level.
    Speichert sowohl lokal als auch online (wenn verfügbar).

    Args:
        score: Der erreichte Score
        player_name: Name des Spielers
        kills: Anzahl der Kills
        level: Erreichtes Level

    Returns:
        tuple: (local_top_10, online_saved_successfully)
    """
    # 1. LOKAL SPEICHERN (immer, auch offline)
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    # Alte Format-Kompatibilität: {"highscore": 12345}
                    old_highscore = data.get("highscore", 0)
                    all_scores = []
                    if old_highscore > 0:
                        all_scores.append({"score": old_highscore, "name": "Player", "kills": 0, "level": 1})
                else:
                    all_scores = data if isinstance(data, list) else []
                    # Füge kills und level hinzu, falls nicht vorhanden (Kompatibilität)
                    for entry in all_scores:
                        if "kills" not in entry:
                            entry["kills"] = 0
                        if "level" not in entry:
                            entry["level"] = 1
        except Exception:
            all_scores = []
    else:
        all_scores = []

    # Füge neuen Score hinzu
    new_score = {
        "score": score,
        "name" : player_name,
        "kills": kills,
        "level": level
    }
    all_scores.append(new_score)

    # Behalte Top 10 - Sortiere nach Score (primär), dann nach Kills (sekundär)
    top_10 = sorted(all_scores, key=lambda x: (x["score"], x.get("kills", 0)), reverse=True)[:10]

    print(f"[save_normal_score] Saving to {HIGHSCORE_FILE}: {player_name} - {score} points, {kills} kills, level {level}")
    print(f"[save_normal_score] Top 10 list has {len(top_10)} entries")

    try:
        with open(HIGHSCORE_FILE, "w") as f:
            json.dump(top_10, f, indent=2)
        print(f"✓ Saved {len(top_10)} scores locally to {HIGHSCORE_FILE}")
    except Exception as e:
        print(f"✗ Failed to save locally: {e}")

    # 2. ONLINE SPEICHERN (nur wenn Firebase verfügbar)
    online_success = False
    from system.firebase_manager import is_firebase_available
    if is_firebase_available():
        manager = get_online_manager()
        if manager:
            try:
                # Firebase save_highscore nimmt andere Parameter - wir nutzen die gleiche Funktion
                # aber mit stage=0 für Normal Mode
                online_success = manager.save_highscore(
                    name=player_name,
                    time=score,  # Score als "time" speichern
                    kills=kills,  # Kills mit speichern
                    stage=0,     # stage=0 = Normal Mode
                    level=level  # Level mit speichern
                )
                if online_success:
                    print(f"✓ Highscore saved online: {player_name} - {score} points, {kills} kills, level {level}")
            except Exception as e:
                print(f"⚠ Failed to save online: {e}")

    return top_10, online_success

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

    # 2. ONLINE SPEICHERN (nur wenn Firebase verfügbar)
    online_success = False
    from system.firebase_manager import is_firebase_available
    if is_firebase_available():
        manager = get_online_manager()
        if manager:
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
    # Versuche online zu laden (nur wenn Firebase verfügbar)
    from system.firebase_manager import is_firebase_available
    if is_firebase_available():
        manager = get_online_manager()
        if manager:
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
