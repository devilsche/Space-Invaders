"""
Test Script für ShieldGlow.png Sprite Animation
Zeigt das Shield-Glow animiert um ein Schiff herum
"""

import pygame
import sys

# Pygame initialisieren
pygame.init()

# Fenster erstellen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ShieldGlow Sprite Test")
clock = pygame.time.Clock()

# Farben
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Lade Shield Glow Sprite Sheet
try:
    shield_sprite_sheet = pygame.image.load("assets/images/ShieldGlow.png").convert_alpha()
    print(f"Shield sprite loaded: {shield_sprite_sheet.get_size()}")
except Exception as e:
    print(f"Error loading ShieldGlow.png: {e}")
    pygame.quit()
    sys.exit(1)

# Lade Jet Sprite Sheet (Engine Thruster Animation)
try:
    jet_sprite_sheet = pygame.image.load("assets/images/jet.png").convert_alpha()
    print(f"Jet sprite loaded: {jet_sprite_sheet.get_size()}")
except Exception as e:
    print(f"Error loading jet.png: {e}")
    pygame.quit()
    sys.exit(1)

# Lade alle Stage-Schiffe
ship_images = {}
ship_configs = {
    1: {"file": "assets/images/player/stage1.png", "size": 85, "shield_scale": 0.55, "jet_scale": 0.4, "jet_count": 1, "jet_offset": 0},
    2: {"file": "assets/images/player/stage2.png", "size": 90, "shield_scale": 0.6, "jet_scale": 0.4, "jet_count": 1, "jet_offset": 0},
    3: {"file": "assets/images/player/stage3.png", "size": 100, "shield_scale": 0.7, "jet_scale": 0.5, "jet_count": 1, "jet_offset": 0},
    4: {"file": "assets/images/player/stage4.png", "size": 130, "shield_scale": 1.0, "jet_scale": 0.35, "jet_count": 2, "jet_offset": 6},
}

current_stage = 1

for stage, config in ship_configs.items():
    try:
        img = pygame.image.load(config["file"]).convert_alpha()
        img = pygame.transform.scale(img, (config["size"], config["size"]))
        ship_images[stage] = img
        print(f"Stage {stage} ship loaded: {config['size']}x{config['size']}")
    except Exception as e:
        print(f"Error loading stage {stage} ship: {e}")
        # Fallback: Erstelle ein einfaches Schiff
        img = pygame.Surface((config["size"], config["size"]), pygame.SRCALPHA)
        pygame.draw.polygon(img, WHITE, [(config["size"]//2, 0), (0, config["size"]),
                                         (config["size"]//2, config["size"]*0.75), (config["size"], config["size"])])
        ship_images[stage] = img

# Aktuelles Schiff und Config
ship_image = ship_images[current_stage]
shield_scale = ship_configs[current_stage]["shield_scale"]

# Extrahiere Frames aus dem Sprite Sheet
# Annahme: Sprite ist horizontal angeordnet
sprite_width = shield_sprite_sheet.get_width()
sprite_height = shield_sprite_sheet.get_height()

# Verschiedene Frame-Konfigurationen testen
configs = [
    {"frames": 16, "rows": 4, "name": "16 Frames, 4x4 Grid"},
    {"frames": 8, "rows": 1, "name": "8 Frames, 1 Row (Test)"},
    {"frames": 4, "rows": 2, "name": "4 Frames, 2 Rows (Test)"},
]

current_config = 0
frame_count = configs[current_config]["frames"]
rows = configs[current_config]["rows"]

def extract_frames(sheet, num_frames, num_rows):
    """Extrahiert Frames aus dem Sprite Sheet"""
    frames = []
    cols = num_frames // num_rows
    frame_width = sheet.get_width() // cols
    frame_height = sheet.get_height() // num_rows

    for row in range(num_rows):
        for col in range(cols):
            x = col * frame_width
            y = row * frame_height
            frame = sheet.subsurface((x, y, frame_width, frame_height))
            frames.append(frame)

    return frames, frame_width, frame_height

shield_frames, frame_w, frame_h = extract_frames(shield_sprite_sheet, frame_count, rows)
print(f"Extracted {len(shield_frames)} frames, each {frame_w}x{frame_h}")

# Extrahiere Jet Frames (4x2 grid = 8 frames)
jet_frame_count = 8
jet_rows = 2
jet_frames, jet_frame_w, jet_frame_h = extract_frames(jet_sprite_sheet, jet_frame_count, jet_rows)
print(f"Extracted {len(jet_frames)} jet frames, each {jet_frame_w}x{jet_frame_h}")

# Animation
current_frame = 0
current_jet_frame = 0
animation_speed = 0.3  # Frames pro Update (schneller)
frame_timer = 0
jet_frame_timer = 0

# Rotation
rotation_angle = 0  # Aktueller Rotationswinkel
rotation_step = 360 / 360  # 11.25° pro Frame
rotation_enabled = False  # Rotation standardmäßig AUS

# Shield Alpha (Transparenz)
shield_alpha = 125  # 0-255, 125 = ~50% sichtbar

# Jet Engine Toggle
jet_enabled = True  # Jet standardmäßig AN

# Shield Toggle
shield_enabled = True  # Shield standardmäßig AN

# Ship Position
ship_x = WIDTH // 2
ship_y = HEIGHT // 2

# UI
font = pygame.font.Font(None, 30)
small_font = pygame.font.Font(None, 20)

running = True
paused = False

while running:
    dt = clock.tick(60) / 1000.0  # Delta time in Sekunden

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_1:
                current_stage = 1
                ship_image = ship_images[current_stage]
                shield_scale = ship_configs[current_stage]["shield_scale"]
                print(f"Switched to Stage 1 - Shield Scale: {shield_scale}")
            elif event.key == pygame.K_2:
                current_stage = 2
                ship_image = ship_images[current_stage]
                shield_scale = ship_configs[current_stage]["shield_scale"]
                print(f"Switched to Stage 2 - Shield Scale: {shield_scale}")
            elif event.key == pygame.K_3:
                current_stage = 3
                ship_image = ship_images[current_stage]
                shield_scale = ship_configs[current_stage]["shield_scale"]
                print(f"Switched to Stage 3 - Shield Scale: {shield_scale}")
            elif event.key == pygame.K_4:
                current_stage = 4
                ship_image = ship_images[current_stage]
                shield_scale = ship_configs[current_stage]["shield_scale"]
                print(f"Switched to Stage 4 - Shield Scale: {shield_scale}")
            elif event.key == pygame.K_UP:
                shield_scale += 0.1
                print(f"Shield scale: {shield_scale:.1f}")
            elif event.key == pygame.K_DOWN:
                shield_scale = max(0.5, shield_scale - 0.1)
                print(f"Shield scale: {shield_scale:.1f}")
            elif event.key == pygame.K_LEFT:
                animation_speed = max(0.05, animation_speed - 0.05)
                print(f"Animation speed: {animation_speed:.2f}")
            elif event.key == pygame.K_RIGHT:
                animation_speed = min(1.0, animation_speed + 0.05)
                print(f"Animation speed: {animation_speed:.2f}")
            elif event.key == pygame.K_c:
                # Wechsle Frame-Konfiguration
                current_config = (current_config + 1) % len(configs)
                frame_count = configs[current_config]["frames"]
                rows = configs[current_config]["rows"]
                shield_frames, frame_w, frame_h = extract_frames(shield_sprite_sheet, frame_count, rows)
                current_frame = 0
                rotation_angle = 0  # Reset rotation
                print(f"Config: {configs[current_config]['name']}")
                print(f"Extracted {len(shield_frames)} frames, each {frame_w}x{frame_h}")
            elif event.key == pygame.K_r:
                # Toggle Rotation
                rotation_enabled = not rotation_enabled
                print(f"Rotation: {'ON' if rotation_enabled else 'OFF'}")
            elif event.key == pygame.K_j:
                # Toggle Jet Engine
                jet_enabled = not jet_enabled
                print(f"Jet Engine: {'ON' if jet_enabled else 'OFF'}")
            elif event.key == pygame.K_q:
                # Toggle Shield
                shield_enabled = not shield_enabled
                print(f"Shield: {'ON' if shield_enabled else 'OFF'}")
            elif event.key == pygame.K_a:
                # Erhöhe Transparenz (weniger sichtbar)
                shield_alpha = max(50, shield_alpha - 20)
                print(f"Shield Alpha: {shield_alpha} ({shield_alpha/255*100:.0f}%)")
            elif event.key == pygame.K_s:
                # Verringere Transparenz (mehr sichtbar)
                shield_alpha = min(255, shield_alpha + 20)
                print(f"Shield Alpha: {shield_alpha} ({shield_alpha/255*100:.0f}%)")

    # Animation update
    if not paused:
        frame_timer += animation_speed
        if frame_timer >= 1:
            frame_timer = 0
            current_frame = (current_frame + 1) % len(shield_frames)
            # Rotiere um 11.25° pro Frame-Wechsel (nur wenn aktiviert)
            if rotation_enabled:
                rotation_angle = (rotation_angle + rotation_step) % 360

        # Jet-Animation separat (schneller)
        jet_frame_timer += animation_speed * 1.5  # Jet animiert schneller
        if jet_frame_timer >= 1:
            jet_frame_timer = 0
            current_jet_frame = (current_jet_frame + 1) % len(jet_frames)

    # Zeichnen
    screen.fill(BLACK)

    # Aktuellen Jet-Frame skalieren und unter dem Schiff positionieren (wenn aktiviert)
    if jet_enabled:
        config = ship_configs[current_stage]
        jet_size = int(config["size"] * config["jet_scale"])
        current_jet = pygame.transform.scale(jet_frames[current_jet_frame], (jet_size, jet_size))
        current_jet.set_alpha(180)  # Leicht transparent

        # Jet unter dem Schiff positionieren
        jet_offset_y = config["size"] - 60
        
        # Zeichne Jets basierend auf jet_count
        if config["jet_count"] == 1:
            # Ein Jet in der Mitte
            jet_rect = current_jet.get_rect(center=(ship_x, ship_y + jet_offset_y))
            screen.blit(current_jet, jet_rect)
        elif config["jet_count"] == 2:
            # Zwei Jets links und rechts
            jet_spacing = config["jet_offset"]
            jet_offset_y = config["size"] - 70
            # Linker Jet
            jet_rect_left = current_jet.get_rect(center=(ship_x - jet_spacing-2, ship_y + jet_offset_y))
            screen.blit(current_jet, jet_rect_left)
            # Rechter Jet
            jet_rect_right = current_jet.get_rect(center=(ship_x + jet_spacing, ship_y + jet_offset_y))
            screen.blit(current_jet, jet_rect_right)

    # Aktuellen Shield-Frame skalieren und rotieren (wenn aktiviert)
    if shield_enabled:
        shield_size = int(max(frame_w, frame_h) * shield_scale)
        current_shield = pygame.transform.scale(shield_frames[current_frame], (shield_size, shield_size))
        # Rotiere den Frame (nur wenn aktiviert)
        if rotation_enabled:
            current_shield = pygame.transform.rotate(current_shield, rotation_angle)

        # Setze Alpha (Transparenz)
        current_shield.set_alpha(shield_alpha)

        # Shield zentriert um das Schiff zeichnen
        shield_rect = current_shield.get_rect(center=(ship_x, ship_y))
        screen.blit(current_shield, shield_rect)

    # Schiff über dem Shield zeichnen
    ship_rect = ship_image.get_rect(center=(ship_x, ship_y))
    screen.blit(ship_image, ship_rect)

    # Info-Text
    rotation_status = "ON" if rotation_enabled else "OFF"
    jet_status = "ON" if jet_enabled else "OFF"
    shield_status = "ON" if shield_enabled else "OFF"
    ship_size = ship_configs[current_stage]["size"]
    # Shield size nur berechnen wenn enabled
    display_shield_size = int(max(frame_w, frame_h) * shield_scale) if shield_enabled else 0
    info_texts = [
        f"Ship: Stage {current_stage} ({ship_size}x{ship_size}) - Press 1-4 to switch",
        f"Config: {configs[current_config]['name']} (Press C to change)",
        f"Shield Frame: {current_frame + 1}/{len(shield_frames)} | Jet Frame: {current_jet_frame + 1}/{len(jet_frames)}",
        f"Rotation: {rotation_status} - {rotation_angle:.1f}° (Press R to toggle)",
        f"Shield: {shield_status} (Press Q to toggle)",
        f"Jet Engine: {jet_status} (Press J to toggle)",
        f"Shield Scale: {shield_scale:.1f} (UP/DOWN to adjust)",
        f"Shield Alpha: {shield_alpha} ({shield_alpha/255*100:.0f}%) - A/S to adjust",
        f"Speed: {animation_speed:.2f} (LEFT/RIGHT to adjust)",
        f"Frame Size: {frame_w}x{frame_h}",
        f"Scaled Size: {display_shield_size}x{display_shield_size}",
        "",
        "1-4 - Switch Ship Stage",
        "R - Toggle Rotation",
        "Q - Toggle Shield",
        "J - Toggle Jet Engine",
        "A/S - Adjust Transparency",
        "SPACE - Pause/Resume",
        "ESC - Exit"
    ]

    y_offset = 10
    for text in info_texts:
        if text:
            surface = small_font.render(text, True, GREEN)
        else:
            y_offset += 10
            continue
        screen.blit(surface, (10, y_offset))
        y_offset += 25

    # Status
    if paused:
        pause_text = font.render("PAUSED", True, (255, 255, 0))
        pause_rect = pause_text.get_rect(center=(WIDTH // 2, 50))
        screen.blit(pause_text, pause_rect)

    pygame.display.flip()

pygame.quit()
print("Test beendet.")
