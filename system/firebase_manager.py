"""
Zentrale Firebase-Verfügbarkeitsprüfung für die gesamte Anwendung.

Diese Datei stellt eine globale Variable firebase_available bereit,
die einmalig beim Asset-Loading gesetzt wird und von allen anderen
Modulen verwendet werden kann.
"""

# Globale Variable für Firebase-Verfügbarkeit
firebase_available = False
_online_manager    = None

def initialize_firebase():
    """
    Prüft einmalig die Firebase-Verfügbarkeit beim Anwendungsstart.
    Setzt die globale Variable firebase_available.

    Returns:
        bool: True wenn Firebase verfügbar ist, False sonst
    """
    global firebase_available, _online_manager

    try:
        print("🔄 Checking Firebase availability...")
        from manager.highscore_manager import get_online_manager
        _online_manager = get_online_manager()

        if _online_manager and _online_manager.is_connected():
            firebase_available = True
            print("✅ Firebase is available and connected")
            return True
        else:
            firebase_available = False
            print("❌ Firebase is not available or not connected")
            return False

    except Exception as e:
        firebase_available = False
        _online_manager = None
        print(f"❌ Firebase initialization failed: {e}")
        return False

def get_firebase_manager():
    """
    Gibt den Firebase-Manager zurück, falls verfügbar.

    Returns:
        FirebaseManager or None: Manager-Instanz oder None
    """
    global firebase_available, _online_manager

    if firebase_available and _online_manager:
        return _online_manager
    return None

def is_firebase_available():
    """
    Prüft ob Firebase verfügbar ist (ohne erneute Initialisierung).

    Returns:
        bool: True wenn Firebase verfügbar ist
    """
    global firebase_available
    return firebase_available
