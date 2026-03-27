# system/survivor_screens.py - Survivor Mode specific screens
import pygame
import time
from system.utils import load_survivor_highscores, save_survivor_score, get_online_manager, resource_path


def draw_saving_progress(screen, phase="local", progress=0.0, status_text="Saving..."):
    """
    Zeichnet eine kleine Progress Bar unten rechts.

    Args:
        screen: Pygame Surface
        phase: "local", "online", oder "done"
        progress: 0.0 bis 1.0 (Fortschritt)
        status_text: Text unter der Bar
    """
    cw, ch = screen.get_size()

    # Dimensionen (klein und kompakt)
    bar_width = 200
    bar_height = 8
    padding = 20

    # Position: Unten rechts
    x = cw - bar_width - padding
    y = ch - bar_height - 50

    # Farben
    bg_color = (40, 40, 40)
    if phase == "local":
        bar_color = (100, 200, 100)  # Grün
    elif phase == "online":
        bar_color = (100, 150, 255)  # Blau
    elif phase == "done":
        bar_color = (255, 200, 50)   # Gold
    else:
        bar_color = (150, 150, 150)  # Grau

    # Hintergrund
    pygame.draw.rect(screen, bg_color, (x, y, bar_width, bar_height))

    # Fortschrittsbalken
    filled_width = int(bar_width * min(progress, 1.0))
    if filled_width > 0:
        pygame.draw.rect(screen, bar_color, (x, y, filled_width, bar_height))

    # Rahmen
    pygame.draw.rect(screen, (100, 100, 100), (x, y, bar_width, bar_height), 1)

    # Status Text
    try:
        font = pygame.font.Font(resource_path("assets/fonts/monofonto rg.otf"), 14)
    except:
        font = pygame.font.Font(None, 16)

    text_surface = font.render(status_text, True, (200, 200, 200))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x + bar_width // 2, y + bar_height + 4)
    screen.blit(text_surface, text_rect)


def save_with_progress_animation(screen, bg_scaled, survivor_time, survivor_kills, player_name, stage):
    """
    Speichert Highscore mit animierter Progress Bar.

    Returns:
        tuple: (local_top_10, online_saved_successfully)
    """
    clock = pygame.time.Clock()

    # Phase 1: Lokales Speichern (schnell)
    for progress in [0.3, 0.6, 1.0]:
        # Hintergrund neu zeichnen
        if bg_scaled:
            screen.blit(bg_scaled, (0, 0))
        else:
            screen.fill((0, 0, 0))

        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Progress Bar zeichnen
        draw_saving_progress(screen, "local", progress, "Saving locally...")
        pygame.display.flip()
        clock.tick(60)  # 60 FPS

    # Tatsächlich lokal speichern
    local_top_10, online_saved = save_survivor_score(survivor_time, survivor_kills, player_name, stage)

    # Phase 2: Online Speichern (falls zentral verfügbar)
    from system.firebase_manager import is_firebase_available
    if online_saved or is_firebase_available():
        for progress in [0.3, 0.6, 1.0]:
            if bg_scaled:
                screen.blit(bg_scaled, (0, 0))
            else:
                screen.fill((0, 0, 0))

            overlay = pygame.Surface(screen.get_size())
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))

            draw_saving_progress(screen, "online", progress, "Uploading online...")
            pygame.display.flip()
            clock.tick(60)

    # Phase 3: Fertig!
    for _ in range(15):  # 0.25 Sekunden anzeigen
        if bg_scaled:
            screen.blit(bg_scaled, (0, 0))
        else:
            screen.fill((0, 0, 0))

        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        status = "✓ Saved!" if online_saved else "✓ Saved locally"
        draw_saving_progress(screen, "done", 1.0, status)
        pygame.display.flip()
        clock.tick(60)

    return local_top_10, online_saved

class SurvivorNameInputScreen:
    """Namenseingabe-Screen für Survivor-Mode Highscore"""

    def __init__(self):
        self.player_name = ""

    def handle_and_draw(self, screen, bg_scaled, survivor_time, survivor_kills, stage=1):
        """
        Zeichnet und handhabt die Namenseingabe

        Args:
            stage: Die Stage (1-4) für die Highscore-Liste

        Returns:
            "submit": Wenn Name eingegeben und ENTER gedrückt
            None: Sonst
        """
        # Hintergrund verdunkeln
        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))

        # Spielfeld mit Overlay zeichnen
        if bg_scaled:
            screen.blit(bg_scaled, (0, 0))
        else:
            screen.fill((0, 0, 0))

        screen.blit(overlay, (0, 0))

        cw, ch = screen.get_size()
        ui_scale = max(cw / 1920, ch / 1080) * 1.2

        # Fonts mit Unicode-Support laden
        try:
            title_font       = pygame.font.Font(resource_path("assets/fonts/Astralight.ttf")    , int(80 * ui_scale))
            stats_font       = pygame.font.Font(resource_path("assets/fonts/monofonto rg.otf")  , int(45 * ui_scale))
            prompt_font      = pygame.font.Font(resource_path("assets/fonts/White On Black.ttf"), int(40 * ui_scale))
            name_font        = pygame.font.Font(resource_path("assets/fonts/monofonto rg.otf")  , int(60 * ui_scale))
            instruction_font = pygame.font.Font(resource_path("assets/fonts/White On Black.ttf"), int(28 * ui_scale))
        except:
            title_font       = pygame.font.Font(None, int(80 * ui_scale))
            stats_font       = pygame.font.Font(None, int(50 * ui_scale))
            prompt_font      = pygame.font.Font(None, int(40 * ui_scale))
            name_font        = pygame.font.Font(None, int(60 * ui_scale))
            instruction_font = pygame.font.Font(None, int(30 * ui_scale))

        # Title
        title_text = title_font.render("GAME OVER", True, (255, 100, 100))
        title_rect = title_text.get_rect(center=(cw // 2, ch // 4))

        shadow_text = title_font.render("GAME OVER", True, (0, 0, 0))
        shadow_rect = shadow_text.get_rect(center=(cw // 2 + 3, ch // 4 + 3))
        screen.blit(shadow_text, shadow_rect)
        screen.blit(title_text, title_rect)

        # Stats
        minutes = int(survivor_time // 60)
        seconds = int(survivor_time % 60)
        millis = int((survivor_time % 1) * 100)
        time_str = f"Time: {minutes:02d}:{seconds:02d}.{millis:02d}"
        time_text = stats_font.render(time_str, True, (255, 255, 100))
        time_rect = time_text.get_rect(center=(cw // 2, ch // 2 - int(110 * ui_scale)))
        screen.blit(time_text, time_rect)

        kills_str = f"Kills: {survivor_kills}"
        kills_text = stats_font.render(kills_str, True, (100, 255, 100))
        kills_rect = kills_text.get_rect(center=(cw // 2, ch // 2 - int(60 * ui_scale)))
        screen.blit(kills_text, kills_rect)

        # Name Input Prompt
        prompt_text = prompt_font.render("Enter your name:", True, (200, 200, 200))
        prompt_rect = prompt_text.get_rect(center=(cw // 2, ch // 2 + int(30 * ui_scale)))
        screen.blit(prompt_text, prompt_rect)

        # Name Display (mit Cursor)
        display_name = self.player_name + "_"
        name_text = name_font.render(display_name, True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(cw // 2, ch // 2 + int(110 * ui_scale)))

        # Box um Namen
        padding = int(20 * ui_scale)
        box_rect = name_rect.inflate(padding * 2, padding)
        pygame.draw.rect(screen, (50, 50, 50), box_rect)
        pygame.draw.rect(screen, (150, 150, 150), box_rect, 2)
        screen.blit(name_text, name_rect)

        # Instruktion
        instruction_text = instruction_font.render("Press ENTER to save, ESC to skip", True, (150, 150, 150))
        instruction_rect = instruction_text.get_rect(center=(cw // 2, ch - int(100 * ui_scale)))
        screen.blit(instruction_text, instruction_rect)

        # Event Handling
        result = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if not self.player_name:
                        self.player_name = "Player"
                    _, online_saved = save_with_progress_animation(
                        screen, bg_scaled, survivor_time, survivor_kills, self.player_name, stage
                    )
                    self.player_name = ""
                    result = "submit"
                elif event.key == pygame.K_ESCAPE:
                    # ESC = Nicht speichern
                    self.player_name = ""
                    result = "skip"
                elif event.key == pygame.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                elif event.key == pygame.K_F11:
                    result = "maximize"
                elif event.key == pygame.K_RETURN and (pygame.key.get_pressed()[pygame.K_LALT] or pygame.key.get_pressed()[pygame.K_RALT]):
                    result = "fullscreen"
                else:
                    if len(self.player_name) < 15 and event.unicode.isprintable():
                        self.player_name += event.unicode

        pygame.display.flip()
        return result


class SurvivorGameOverScreen:
    """Game Over Screen mit Bestenliste für Survivor-Mode"""

    def handle_and_draw(self, screen, bg_scaled, survivor_time, survivor_kills, stage=1):
        """
        Zeichnet und handhabt den Game Over Screen mit Leaderboard

        Args:
            stage: Die Stage (1-4) für die Highscore-Liste

        Returns:
            "retry": Wenn SPACE gedrückt
            "menu": Wenn ESC gedrückt
            None: Sonst
        """
        # Hintergrund verdunkeln
        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))

        # Spielfeld mit Overlay zeichnen
        if bg_scaled:
            screen.blit(bg_scaled, (0, 0))
        else:
            screen.fill((0, 0, 0))

        screen.blit(overlay, (0, 0))

        cw, ch = screen.get_size()
        ui_scale = max(cw / 1920, ch / 1080) * 1.2

        # Fonts mit Unicode-Support laden
        try:
            title_font       = pygame.font.Font(resource_path("assets/fonts/Astralight.ttf")    , int(120 * ui_scale))
            time_font        = pygame.font.Font(resource_path("assets/fonts/monofonto rg.otf")  , int(60  * ui_scale))
            leaderboard_font = pygame.font.Font(resource_path("assets/fonts/White On Black.ttf"), int(50  * ui_scale))
            score_font       = pygame.font.Font(resource_path("assets/fonts/monofonto rg.otf")  , int(28  * ui_scale))
            controls_font    = pygame.font.Font(resource_path("assets/fonts/KGRedHands.ttf")    , int(24  * ui_scale))
        except:
            title_font       = pygame.font.Font(None, int(120 * ui_scale))
            time_font        = pygame.font.Font(None, int(70 * ui_scale))
            leaderboard_font = pygame.font.Font(None, int(50 * ui_scale))
            score_font       = pygame.font.Font(None, int(32 * ui_scale))
            controls_font    = pygame.font.Font(None, int(24 * ui_scale))

        # Title
        title_text = title_font.render("SURVIVOR MODE", True, (255, 100, 100))
        title_rect = title_text.get_rect(center=(cw // 2, ch // 4))

        shadow_text = title_font.render("SURVIVOR MODE", True, (0, 0, 0))
        shadow_rect = shadow_text.get_rect(center=(cw // 2 + 4, ch // 4 + 4))
        screen.blit(shadow_text, shadow_rect)
        screen.blit(title_text, title_rect)

        # Your Time
        minutes   = int(survivor_time // 60)
        seconds   = int(survivor_time % 60)
        millis    = int((survivor_time % 1) * 100)
        time_str  = f"Your Time: {minutes:02d}:{seconds:02d}.{millis:02d}"
        time_text = time_font.render(time_str, True, (255, 255, 100))
        time_rect = time_text.get_rect(center=(cw // 2, ch // 3))

        shadow = time_font.render(time_str, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(cw // 2 + 3, ch // 3 + 3))
        screen.blit(shadow, shadow_rect)
        screen.blit(time_text, time_rect)

        # Bestenliste
        stage_name = ["Rookie", "Veteran", "Elite", "Legend"][stage - 1]
        leaderboard_title = leaderboard_font.render(f"TOP 10 - {stage_name.upper()}", True, (255, 255, 255))
        leaderboard_title_rect = leaderboard_title.get_rect(center=(cw // 2, ch // 2 - int(80 * ui_scale)))
        screen.blit(leaderboard_title, leaderboard_title_rect)

        # Top 10 anzeigen (für diese Stage)
        scores = load_survivor_highscores(stage)
        start_y = ch // 2 - int(30 * ui_scale)

        for i, score_entry in enumerate(scores[:10]):
            time_val = score_entry.get("time", 0)
            kills = score_entry.get("kills", 0)
            name = score_entry.get("name", "Player")

            mins = int(time_val // 60)
            secs = int(time_val % 60)
            ms = int((time_val % 1) * 100)

            # Highlight aktuelle Zeit
            is_current = abs(time_val - survivor_time) < 0.01 and kills == survivor_kills
            if is_current:
                color = (255, 255, 100)
                marker = " ←"
            else:
                color = (200, 200, 200)
                marker = ""

            # Format: #1  Name           00:34.56  (42 kills)
            text_str = f"#{i+1}  {name:<15}  {mins:02d}:{secs:02d}.{ms:02d}  ({kills} kills){marker}"

            score_text = score_font.render(text_str, True, color)
            score_rect = score_text.get_rect(center=(cw // 2, start_y + i * int(35 * ui_scale)))
            screen.blit(score_text, score_rect)

        # Controls
        controls_y    = ch - int(80 * ui_scale)
        controls_text = "[SPACE] Try Again - [ESC] Main Menu"
        controls      = controls_font.render(controls_text, True, (200, 200, 200))
        controls_rect = controls.get_rect(center=(cw // 2, controls_y))
        screen.blit(controls, controls_rect)

        # Event Handling
        result = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    result = "retry"
                elif event.key == pygame.K_ESCAPE:
                    result = "menu"
                elif event.key == pygame.K_F11:
                    result = "maximize"
                elif event.key == pygame.K_RETURN and (pygame.key.get_pressed()[pygame.K_LALT] or pygame.key.get_pressed()[pygame.K_RALT]):
                    result = "fullscreen"

        pygame.display.flip()
        return result
