# manager/asset_manager.py
"""
AssetManager - Zentralisierte Verwaltung aller Spiel-Assets
Unterstützt: Bilder, Sounds, Musik, Animationen, Fonts
Features: Lazy Loading, Caching, Error Handling, Type Safety
"""
import pygame
import os
from typing import Any
from enum import Enum
import logging

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AssetType(Enum):
    """Enum für Asset-Typen"""
    IMAGE = "image"
    SOUND = "sound"
    MUSIC = "music"
    ANIMATION = "animation"
    FONT = "font"


class AssetManager:
    """
    Zentraler Asset-Manager mit Caching und Lazy Loading

    Features:
    - Automatisches Caching bereits geladener Assets
    - Lazy Loading (Assets werden erst bei Bedarf geladen)
    - Error Handling mit Fallback-Assets
    - Type-safe Asset-Zugriff
    - Memory Management
    """

    def __init__(self):
        self._cache: dict[str, Any] = {}
        self._asset_paths: dict[str, str] = {}
        self._loaded = False

        # Statistiken
        self._stats = {
            'loaded'       : 0,
            'cached'       : 0,
            'failed'       : 0,
            'memory_usage' : 0
        }

        # Fallback-Assets für Fehlerbehandlung
        self._fallbacks = {}
        self._init_fallbacks()

    def _init_fallbacks(self):
        """Initialisiert Fallback-Assets für Fehlerbehandlung"""
        # Erstelle ein einfaches Fallback-Bild (rotes Rechteck)
        fallback_surf = pygame.Surface((32, 32))
        fallback_surf.fill((255, 0, 0))
        self._fallbacks[AssetType.IMAGE] = fallback_surf

        # Fallback für Sounds (leerer Sound)
        try:
            # Erstelle einen stummen Sound
            self._fallbacks[AssetType.SOUND] = None
        except:
            pass

    def register_asset(self, key: str, path: str, asset_type: AssetType = AssetType.IMAGE):
        """
        Registriert einen Asset-Pfad für späteres Laden

        Args:
            key: Eindeutiger Schlüssel für das Asset
            path: Dateipfad zum Asset
            asset_type: Typ des Assets (IMAGE, SOUND, etc.)
        """
        self._asset_paths[key] = (path, asset_type)
        logger.debug(f"Registriert: {key} -> {path} ({asset_type.value})")

    def load_image(
        self,
        path: str,
        size: tuple[int, int] | None = None,
        convert_alpha: bool = True,
        trim: bool = False
    ) -> pygame.Surface:
        """
        Lädt ein Bild mit optionaler Größenanpassung

        Args:
            path: Pfad zum Bild
            size: Optionale Zielgröße (width, height)
            convert_alpha: Ob convert_alpha() aufgerufen werden soll
            trim: Ob transparente Bereiche entfernt werden sollen

        Returns:
            pygame.Surface: Das geladene Bild
        """
        cache_key = f"{path}_{size}_{trim}"

        # Prüfe Cache
        if cache_key in self._cache:
            self._stats['cached'] += 1
            return self._cache[cache_key]

        try:
            # Lade Bild
            img = pygame.image.load(path)

            if convert_alpha:
                img = img.convert_alpha()
            else:
                img = img.convert()

            # Trimmen wenn gewünscht
            if trim:
                img = self._trim_surface(img)

            # Skalieren wenn gewünscht
            if size:
                img = pygame.transform.smoothscale(img, size)

            # Cache speichern
            self._cache[cache_key] = img
            self._stats['loaded'] += 1

            logger.debug(f"Bild geladen: {path}")
            return img

        except Exception as e:
            logger.error(f"Fehler beim Laden von {path}: {e}")
            self._stats['failed'] += 1
            return self._fallbacks[AssetType.IMAGE]

    def load_sound(self, path: str, volume: float = 1.0) -> pygame.mixer.Sound | None:
        """
        Lädt einen Sound-Effekt

        Args:
            path: Pfad zum Sound
            volume: Lautstärke (0.0 - 1.0)

        Returns:
            pygame.mixer.Sound oder None bei Fehler
        """
        cache_key = f"sound_{path}"

        # Prüfe Cache
        if cache_key in self._cache:
            self._stats['cached'] += 1
            return self._cache[cache_key]

        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(volume)

            # Cache speichern
            self._cache[cache_key] = sound
            self._stats['loaded'] += 1

            logger.debug(f"Sound geladen: {path}")
            return sound

        except Exception as e:
            logger.error(f"Fehler beim Laden von {path}: {e}")
            self._stats['failed'] += 1
            return None

    def load_animation(
        self,
        sheet_path: str,
        cols: int,
        rows: int,
        frame_width: int,
        frame_height: int,
        scale: float = 1.0
    ) -> list[pygame.Surface]:
        """
        Lädt eine Animation aus einem Spritesheet

        Args:
            sheet_path: Pfad zum Spritesheet
            cols: Anzahl Spalten
            rows: Anzahl Zeilen
            frame_width: Breite eines Frames
            frame_height: Höhe eines Frames
            scale: Skalierungsfaktor

        Returns:
            Liste von pygame.Surface (Frames)
        """
        cache_key = f"anim_{sheet_path}_{cols}_{rows}_{scale}"

        # Prüfe Cache
        if cache_key in self._cache:
            self._stats['cached'] += 1
            return self._cache[cache_key]

        try:
            sheet  = pygame.image.load(sheet_path).convert_alpha()
            frames = []

            target_w = int(frame_width * scale)
            target_h = int(frame_height * scale)

            for row in range(rows):
                for col in range(cols):
                    rect = pygame.Rect(
                        col * frame_width,
                        row * frame_height,
                        frame_width,
                        frame_height
                    )
                    frame = sheet.subsurface(rect).copy()

                    if scale != 1.0:
                        frame = pygame.transform.smoothscale(frame, (target_w, target_h))

                    frames.append(frame)

            # Cache speichern
            self._cache[cache_key] = frames
            self._stats['loaded'] += 1

            logger.debug(f"Animation geladen: {sheet_path} ({len(frames)} Frames)")
            return frames

        except Exception as e:
            logger.error(f"Fehler beim Laden der Animation {sheet_path}: {e}")
            self._stats['failed'] += 1
            # Fallback: Eine Liste mit einem Fallback-Frame
            return [self._fallbacks[AssetType.IMAGE]]

    def load_spritesheet(
        self,
        path:       str,
        cols:       int,
        rows:       int,
        frame_size: tuple[int, int],
        scale:      float = 1.0
    ) -> list[pygame.Surface]:
        """
        Lädt ein Spritesheet und schneidet es in Frames.
        Alias für load_animation mit tuple-basierter Frame-Größe.

        Args:
            path: Pfad zum Spritesheet
            cols: Anzahl Spalten
            rows: Anzahl Zeilen
            frame_size: (width, height) eines Frames
            scale: Skalierungsfaktor

        Returns:
            Liste von pygame.Surface (Frames)
        """
        return self.load_animation(
            sheet_path   = path,
            cols         = cols,
            rows         = rows,
            frame_width  = frame_size[0],
            frame_height = frame_size[1],
            scale        = scale
        )

    def get(self, key: str) -> Any:
        """
        Holt ein Asset aus dem Cache (mit Lazy Loading)

        Args:
            key: Asset-Schlüssel

        Returns:
            Das gecachte Asset oder lädt es bei Bedarf
        """
        # Wenn bereits im Cache, zurückgeben
        if key in self._cache:
            return self._cache[key]

        # Wenn registriert aber noch nicht geladen, jetzt laden
        if key in self._asset_paths:
            path, asset_type = self._asset_paths[key]

            if asset_type == AssetType.IMAGE:
                return self.load_image(path)
            elif asset_type == AssetType.SOUND:
                return self.load_sound(path)
            else:
                logger.warning(f"Asset-Typ {asset_type} noch nicht implementiert")
                return None

        logger.warning(f"Asset nicht gefunden: {key}")
        return None

    def set(self, key: str, value: Any):
        """
        Speichert ein Asset direkt im Cache

        Args:
            key: Asset-Schlüssel
            value: Asset-Wert
        """
        self._cache[key] = value
        logger.debug(f"Asset direkt gesetzt: {key}")

    def has(self, key: str) -> bool:
        """Prüft ob ein Asset existiert (im Cache oder registriert)"""
        return key in self._cache or key in self._asset_paths

    def clear_cache(self):
        """Leert den gesamten Cache (gibt Speicher frei)"""
        self._cache.clear()
        logger.info("Asset-Cache geleert")

    def remove(self, key: str):
        """Entfernt ein spezifisches Asset aus dem Cache"""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Asset entfernt: {key}")

    def get_stats(self) -> dict[str, int]:
        """Gibt Statistiken über geladene Assets zurück"""
        return {
            **self._stats,
            'total_cached' : len(self._cache),
            'registered'   : len(self._asset_paths)
        }

    def print_stats(self):
        """Gibt Statistiken auf der Konsole aus"""
        stats = self.get_stats()
        print("\n=== Asset Manager Statistiken ===")
        print(f"Registriert: {stats['registered']}")
        print(f"Im Cache: {stats['total_cached']}")
        print(f"Neu geladen: {stats['loaded']}")
        print(f"Aus Cache: {stats['cached']}")
        print(f"Fehler: {stats['failed']}")
        print("=" * 35)

    @staticmethod
    def _trim_surface(surface: pygame.Surface) -> pygame.Surface:
        """Entfernt transparente Ränder von einer Surface"""
        rect = surface.get_bounding_rect()
        if rect.size != surface.get_size():
            return surface.subsurface(rect).copy()
        return surface

    def __getitem__(self, key: str) -> Any:
        """Ermöglicht dict-ähnlichen Zugriff: manager['key']"""
        return self.get(key)

    def __setitem__(self, key: str, value: Any):
        """Ermöglicht dict-ähnlichen Zugriff: manager['key'] = value"""
        self.set(key, value)

    def __contains__(self, key: str) -> bool:
        """Ermöglicht 'in' Operator: 'key' in manager"""
        return self.has(key)
