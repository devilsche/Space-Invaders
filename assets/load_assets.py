# assets/load_assets.py
import pygame
from config.ships import SHIP_CONFIG
from config.enemy import ENEMY_CONFIG
from config.projectiles import PROJECTILES_CONFIG
from config import WIDTH, HEIGHT

def _raw(path): return pygame.image.load(path).convert_alpha()

def _trim(s: pygame.Surface):
    r = s.get_bounding_rect()
    return s.subsurface(r).copy() if r.size != s.get_size() else s

def _scaled(path, size=None, trim=True):
    img = _raw(path)
    if trim: img = _trim(img)
    if size: img = pygame.transform.smoothscale(img, size)
    return img

def _slice(sheet, cols, rows, fw, fh, scale=1.0, colorkey_from=(0,0)):
    # für exp2.png ohne Alpha: ColorKey entfernen
    if sheet.get_bitsize() == 24:  # kein Alpha → convert()
        ck = sheet.get_at(colorkey_from)
        sheet = sheet.convert()
    frames = []
    for r in range(rows):
        for c in range(cols):
            s = sheet.subsurface(pygame.Rect(c*fw, r*fh, fw, fh)).copy()
            if s.get_bitsize() == 24:  # ColorKey setzen
                s.set_colorkey(sheet.get_at((0,0)))
                s = s.convert_alpha()
            if scale != 1.0:
                s = pygame.transform.smoothscale(s, (int(fw*scale), int(fh*scale)))
            frames.append(s)
    return frames

def load_assets():
    a = {}

    # Hintergrund optional
    try:
        a["background_img"] = _scaled("assets/images/background.png", (WIDTH, HEIGHT), trim=False)
    except Exception:
        a["background_img"] = None

    # Player je Stage
    for stage, cfg in SHIP_CONFIG.items():
        a[f"player_stage{stage}"] = _scaled(cfg["img"], cfg["size"])

    # Enemies
    for name, ecfg in ENEMY_CONFIG.items():
        a[f"enemy_{name}"] = _scaled(ecfg["img"], ecfg["size"])

    # Projektile-Bilder + Sounds + Explosionen
    def _try_sound(p):
        try: return pygame.mixer.Sound(p)
        except Exception: return None

    for w, pcfg in PROJECTILES_CONFIG.items():
        # Bild
        a[f"{w}_img"] = _scaled(pcfg["img"], pcfg.get("size"))

        # Sounds nach standardisierten Keys
        if pcfg.get("sound_start"):   a[f"{w}_sound_start"]   = _try_sound(pcfg["sound_start"])
        if pcfg.get("sound_hit"):     a[f"{w}_sound_hit"]     = _try_sound(pcfg["sound_hit"])
        if pcfg.get("sound_destroy"): a[f"{w}_sound_destroy"] = _try_sound(pcfg["sound_destroy"])
        if pcfg.get("sound_fly"):     a[f"{w}_sound_fly"]     = _try_sound(pcfg["sound_fly"])

        # Explosion-Frames pro Waffe
        ex = pcfg.get("explosion")
        if ex:
            sheet = pygame.image.load(ex["sheet"])
            frames = _slice(sheet, ex["cols"], ex["rows"], ex["fw"], ex["fh"], ex.get("scale",1.0))
            a[f"expl_{w}"]      = frames
            a[f"expl_{w}_fps"]  = ex.get("fps", 24)
            a[f"expl_{w}_keep"] = ex.get("keep", None)

    # Musikpfade optional
    a["music_paths"] = {"raining_bits": "assets/music/raining_bits.ogg"}

    return a
