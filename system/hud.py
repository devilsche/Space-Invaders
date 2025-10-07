# system/hud.py
import pygame

class HUD:
    """HUD-System für Weapon/Power-Up Status-Anzeige"""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Dynamische Skalierung basierend auf Bildschirmgröße
        base_width = 1920
        scale_factor = max(screen_width / base_width, 1.2)  # Mindestens 20% größer
        
        self.icon_size = int(48 * scale_factor)  # Skalierte Icon-Größe
        self.icon_spacing = int(8 * scale_factor)
        self.margin = int(10 * scale_factor)

        # Position unten links
        self.start_x = self.margin
        self.start_y = screen_height - self.icon_size - self.margin

        # Icon-Positionen
        self.icons = {}
        self.icon_order = ["rocket", "homing_rocket", "blaster", "nuke", "shield"]

        for i, weapon in enumerate(self.icon_order):
            x = self.start_x + i * (self.icon_size + self.icon_spacing)
            y = self.start_y
            self.icons[weapon] = {
                "pos": (x, y),
                "available": False,
                "cooldown_progress": 1.0,  # 1.0 = bereit, 0.0 = gerade verwendet
                "last_used": 0
            }

        # Power-Up Status (unten rechts)
        self.powerup_icons = {}
        self.powerup_order = ["double_laser", "super_shield", "speed_boost"]
        self.powerup_icon_size = int(48 * scale_factor)  # Skalierte PowerUp-Icon-Größe
        self.powerup_spacing = int(8 * scale_factor)
        
        # Position unten rechts
        powerup_start_x = screen_width - self.margin - self.powerup_icon_size
        powerup_start_y = screen_height - self.powerup_icon_size - self.margin
        
        for i, powerup in enumerate(self.powerup_order):
            x = powerup_start_x - i * (self.powerup_icon_size + self.powerup_spacing)
            y = powerup_start_y
            # Standard-Werte, werden später überschrieben
            if powerup == "double_laser":
                total_time = 15000  # 15s
            elif powerup == "super_shield":
                total_time = 8000   # 8s
            elif powerup == "speed_boost":
                total_time = 10000  # 10s
            else:
                total_time = 8000   # Default
                
            self.powerup_icons[powerup] = {
                "pos": (x, y),
                "active": False,
                "remaining_time": 0,
                "total_time": total_time,
                "duration_progress": 0.0  # 1.0 = gerade gestartet, 0.0 = fast abgelaufen
            }

    def make_grayscale(self, surf):
        """Konvertiert Surface zu Graustufen - wie in test.py"""
        try:
            # Versuche die numpy-Version aus test.py
            import numpy as np
            rgb = pygame.surfarray.array3d(surf).astype(np.float32)
            gray = (0.2126*rgb[:,:,0] + 0.7152*rgb[:,:,1] + 0.0722*rgb[:,:,2]).astype(np.uint8)
            gray3 = np.dstack([gray, gray, gray])
            gs = pygame.surfarray.make_surface(gray3).convert_alpha()
            # Alpha übernehmen, falls vorhanden
            try:
                a = pygame.surfarray.array_alpha(surf)
                pygame.surfarray.pixels_alpha(gs)[:,:] = a
            except ValueError:
                pass
            return gs
        except:
            # Fallback: Pixel-für-Pixel Graustufen ohne numpy
            width, height = surf.get_size()
            gray_surf = pygame.Surface((width, height), pygame.SRCALPHA)

            for x in range(width):
                for y in range(height):
                    try:
                        r, g, b, a = surf.get_at((x, y))
                        # Luminanz-Formel für Graustufen
                        gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)
                        gray_surf.set_at((x, y), (gray, gray, gray, a))
                    except:
                        continue
            return gray_surf

    def blit_color_from_bottom_feather(self, screen, color, gray, pos, p, feather=6):
        """Zeichnet Icon mit Cooldown-Progress von unten nach oben"""
        p = max(0.0, min(1.0, p))
        x, y = pos
        w, h = color.get_size()
        screen.blit(gray, pos)
        hh = int(h * p)
        if hh <= 0:
            return
        # Vollfarbbereich
        core = max(0, hh - feather)
        if core > 0:
            src = pygame.Rect(0, h - hh, w, core)
            screen.blit(color, (x, y + h - hh), src)
        # Übergangsstreifen
        if hh > core and feather > 0:
            band_h = min(feather, hh)
            src2 = pygame.Rect(0, h - (hh - core), w, band_h)
            band = color.subsurface(src2).copy()
            # vertikaler Alpha-Gradient
            grad = pygame.Surface((w, band_h), pygame.SRCALPHA)
            for i in range(band_h):
                a = int(255 * (i+1) / band_h)
                grad.fill((255,255,255,a), pygame.Rect(0,i,w,1))
            band.blit(grad, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(band, (x, y + h - (hh - core)))

    def load_icons(self, assets):
        """Lädt und skaliert die Icons"""
        self.icon_images = {}
        self.icon_images_gray = {}
        self.powerup_images = {}

        icon_mapping = {
            "rocket": "rocket.png",
            "homing_rocket": "homingRocket.png",  # Eigenes Homing Rocket Icon
            "blaster": "blaster.png",  # Eigenes Blaster Icon
            "nuke": "nuke.png",
            "shield": "shield.png"
        }

        for weapon, filename in icon_mapping.items():
            try:
                icon_path = f"assets/images/icon/{filename}"
                img = pygame.image.load(icon_path)
                # Auf 48x48 skalieren
                scaled_img = pygame.transform.smoothscale(img, (self.icon_size, self.icon_size))

                # Spezielle Färbung für verschiedene Waffen (nur noch für Nuke und Shield)
                if weapon == "nuke":
                    # Nuke: Gelblich
                    colored_img = scaled_img.copy()
                    yellow_overlay = pygame.Surface(scaled_img.get_size(), pygame.SRCALPHA)
                    yellow_overlay.fill((255, 255, 100, 100))
                    colored_img.blit(yellow_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
                    self.icon_images[weapon] = colored_img
                elif weapon == "shield":
                    # Shield: Blaulich
                    colored_img = scaled_img.copy()
                    blue_overlay = pygame.Surface(scaled_img.get_size(), pygame.SRCALPHA)
                    blue_overlay.fill((100, 150, 255, 100))
                    colored_img.blit(blue_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
                    self.icon_images[weapon] = colored_img
                else:
                    # Verwende das Original-Icon ohne Farbüberlagerung
                    self.icon_images[weapon] = scaled_img

                # Graustufen-Version erstellen
                self.icon_images_gray[weapon] = self.make_grayscale(self.icon_images[weapon])

            except Exception as e:
                print(f"Fehler beim Laden von {filename}: {e}")
                # Fallback: Einfaches farbiges Rechteck
                fallback = pygame.Surface((self.icon_size, self.icon_size))
                fallback.fill((100, 100, 100))
                self.icon_images[weapon] = fallback
                self.icon_images_gray[weapon] = fallback

        # Power-Up Icons laden
        powerup_mapping = {
            "double_laser": "doubleLaser.png",
            "super_shield": "shield.png",
            "speed_boost": "speedup.png"
        }

        for powerup, filename in powerup_mapping.items():
            try:
                icon_path = f"assets/images/icon/{filename}"
                img = pygame.image.load(icon_path)
                # Auf 48x48 skalieren
                scaled_img = pygame.transform.smoothscale(img, (self.powerup_icon_size, self.powerup_icon_size))
                
                # Spezielle Färbung für Power-Ups
                if powerup == "double_laser":
                    # DoubleLaser: Original-Farben behalten
                    self.powerup_images[powerup] = scaled_img
                elif powerup == "super_shield":
                    # Super Shield: Leicht gelbliche Färbung
                    colored_img = scaled_img.copy()
                    yellow_overlay = pygame.Surface(scaled_img.get_size(), pygame.SRCALPHA)
                    yellow_overlay.fill((255, 255, 100, 50))  # Dezente gelbe Färbung
                    colored_img.blit(yellow_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
                    self.powerup_images[powerup] = colored_img
                elif powerup == "speed_boost":
                    # Speed Boost: Bläuliches Glühen für Geschwindigkeit
                    colored_img = scaled_img.copy()
                    blue_overlay = pygame.Surface(scaled_img.get_size(), pygame.SRCALPHA)
                    blue_overlay.fill((100, 200, 255, 60))  # Helles Blau
                    colored_img.blit(blue_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
                    self.powerup_images[powerup] = colored_img
                else:
                    self.powerup_images[powerup] = scaled_img

            except Exception as e:
                print(f"Fehler beim Laden des Power-Up Icons {filename}: {e}")
                # Fallback: Goldenes Rechteck
                fallback = pygame.Surface((self.powerup_icon_size, self.powerup_icon_size))
                fallback.fill((255, 215, 0))
                self.powerup_images[powerup] = fallback

    def update_weapon_status(self, player, current_time, cooldowns):
        """Aktualisiert den Status der Waffen basierend auf Verfügbarkeit und Cooldowns"""
        from config.ship import SHIP_CONFIG
        from config.projectile import PROJECTILES_CONFIG

        ship_config = SHIP_CONFIG.get(player.stage, {})
        weapons = ship_config.get("weapons", {})

        # Rocket Status mit Cooldown
        self.icons["rocket"]["available"] = weapons.get("rocket", 0) > 0
        rocket_cooldown = PROJECTILES_CONFIG.get("rocket", {}).get("cooldown", 1000)
        rocket_last_used = cooldowns.get("rocket_last_used", 0)
        rocket_progress = min(1.0, (current_time - rocket_last_used) / rocket_cooldown) if rocket_cooldown > 0 else 1.0
        self.icons["rocket"]["cooldown_progress"] = rocket_progress

        # Homing Rocket Status mit Cooldown
        self.icons["homing_rocket"]["available"] = weapons.get("homing_rocket", 0) > 0
        homing_cooldown = PROJECTILES_CONFIG.get("homing_rocket", {}).get("cooldown", 2000)
        homing_last_used = cooldowns.get("homing_rocket_last_used", 0)
        homing_progress = min(1.0, (current_time - homing_last_used) / homing_cooldown) if homing_cooldown > 0 else 1.0
        self.icons["homing_rocket"]["cooldown_progress"] = homing_progress

        # Blaster Status mit Cooldown
        self.icons["blaster"]["available"] = weapons.get("blaster", 0) > 0
        blaster_cooldown = PROJECTILES_CONFIG.get("blaster", {}).get("cooldown", 300)
        blaster_last_used = cooldowns.get("blaster_last_used", 0)
        blaster_progress = min(1.0, (current_time - blaster_last_used) / blaster_cooldown) if blaster_cooldown > 0 else 1.0
        self.icons["blaster"]["cooldown_progress"] = blaster_progress

        # Nuke Status mit Cooldown
        self.icons["nuke"]["available"] = weapons.get("nuke", 0) > 0
        nuke_cooldown = PROJECTILES_CONFIG.get("nuke", {}).get("cooldown", 5000)
        nuke_last_used = cooldowns.get("nuke_last_used", 0)
        nuke_progress = min(1.0, (current_time - nuke_last_used) / nuke_cooldown) if nuke_cooldown > 0 else 1.0
        self.icons["nuke"]["cooldown_progress"] = nuke_progress

        # Shield Status mit Cooldown
        shield_available = ship_config.get("shield", 0) == 1
        shield_ready_at = cooldowns.get("shield_ready_at", 0)
        if shield_ready_at > current_time:
            shield_progress = 1.0 - ((shield_ready_at - current_time) / 5000.0)  # 5s Cooldown angenommen
        else:
            shield_progress = 1.0
        self.icons["shield"]["available"] = shield_available
        self.icons["shield"]["cooldown_progress"] = shield_progress

    def update_powerup_status(self, double_laser_active, double_laser_until, super_shield_active, super_shield_until, speed_boost_active, speed_boost_until, current_time):
        """Aktualisiert Power-Up Status"""
        # DoubleLaser Power-Up
        if double_laser_active and double_laser_until > current_time:
            remaining_time = double_laser_until - current_time
            self.powerup_icons["double_laser"]["active"] = True
            self.powerup_icons["double_laser"]["remaining_time"] = remaining_time
            # Duration progress: 1.0 = gerade gestartet, 0.0 = fast abgelaufen
            self.powerup_icons["double_laser"]["duration_progress"] = remaining_time / self.powerup_icons["double_laser"]["total_time"]
        else:
            self.powerup_icons["double_laser"]["active"] = False
            self.powerup_icons["double_laser"]["remaining_time"] = 0
            self.powerup_icons["double_laser"]["duration_progress"] = 0.0

        # Super Shield Power-Up
        if super_shield_active and super_shield_until > current_time:
            remaining_time = super_shield_until - current_time
            self.powerup_icons["super_shield"]["active"] = True
            self.powerup_icons["super_shield"]["remaining_time"] = remaining_time
            # Duration progress: 1.0 = gerade gestartet, 0.0 = fast abgelaufen  
            self.powerup_icons["super_shield"]["duration_progress"] = remaining_time / self.powerup_icons["super_shield"]["total_time"]
        else:
            self.powerup_icons["super_shield"]["active"] = False
            self.powerup_icons["super_shield"]["remaining_time"] = 0
            self.powerup_icons["super_shield"]["duration_progress"] = 0.0

        # Speed Boost Power-Up
        if speed_boost_active and speed_boost_until > current_time:
            remaining_time = speed_boost_until - current_time
            self.powerup_icons["speed_boost"]["active"] = True
            self.powerup_icons["speed_boost"]["remaining_time"] = remaining_time
            # Duration progress: 1.0 = gerade gestartet, 0.0 = fast abgelaufen
            self.powerup_icons["speed_boost"]["duration_progress"] = remaining_time / self.powerup_icons["speed_boost"]["total_time"]
        else:
            self.powerup_icons["speed_boost"]["active"] = False
            self.powerup_icons["speed_boost"]["remaining_time"] = 0
            self.powerup_icons["speed_boost"]["duration_progress"] = 0.0

    def draw(self, screen):
        """Zeichnet das HUD mit Cooldown-Animation"""
        for weapon, data in self.icons.items():
            if weapon not in self.icon_images or weapon not in self.icon_images_gray:
                continue

            pos = data["pos"]
            available = data["available"]
            cooldown_progress = data["cooldown_progress"]

            if not available:
                # Waffe nicht verfügbar: Nur graues Icon zeigen
                screen.blit(self.icon_images_gray[weapon], pos)
            else:
                # Waffe verfügbar: Cooldown-Animation von grau zu farbig
                color_icon = self.icon_images[weapon]
                gray_icon = self.icon_images_gray[weapon]
                self.blit_color_from_bottom_feather(screen, color_icon, gray_icon, pos, cooldown_progress)

        # Power-Up Icons unten rechts zeichnen
        self._draw_powerup_icons(screen)

    def _draw_powerup_icons(self, screen):
        """Zeichnet Power-Up Icons unten rechts mit Duration-Animation"""
        for powerup, data in self.powerup_icons.items():
            if not data["active"] or powerup not in self.powerup_images:
                continue

            pos = data["pos"]
            duration_progress = data["duration_progress"]
            remaining_time = data["remaining_time"]
            
            # Power-Up Icon mit Duration-Animation (von voll zu verschwunden)
            powerup_icon = self.powerup_images[powerup]
            
            # Power-Up Icon ohne Fading - immer voll sichtbar
            screen.blit(powerup_icon, pos)
            
            # Zeit-Text ÜBER dem Icon - nur ganze Sekunden, skaliert
            remaining_sec = int(remaining_time / 1000.0)  # Ganze Sekunden
            if remaining_sec > 0:  # Nur anzeigen wenn Zeit übrig
                # Skalierte Font-Größe basierend auf Icon-Größe
                font_size = max(int(28 * (self.powerup_icon_size / 48)), 18)  # Relative zur Icon-Größe
                font = pygame.font.Font(None, font_size)
                time_text = font.render(f"{remaining_sec}", True, (255, 255, 255))  # Weiß
                text_rect = time_text.get_rect()
                text_x = pos[0] + (self.powerup_icon_size - text_rect.width) // 2
                text_y = pos[1] - text_rect.height - 5  # ÜBER dem Icon
                
                screen.blit(time_text, (text_x, text_y))
