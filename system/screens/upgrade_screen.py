# system/screens/upgrade_screen.py - Upgrade Screen zwischen den Leveln
import pygame
from config.levels import UPGRADE_CONFIG
from system.utils import resource_path


class UpgradeScreen:
    """Upgrade-Screen zwischen den Leveln - Combat-Buffs + Schiff-Upgrade mit Score als Währung"""

    def __init__(self, ship_stage=1):
        self.selected = 0
        self.ship_stage = ship_stage  # Aktuelles Schiff
        self.upgrade_levels = {cat: 0 for cat in UPGRADE_CONFIG}
        self.categories = list(UPGRADE_CONFIG.keys())
        self._created_at = pygame.time.get_ticks()
        self._input_delay = 500  # 500ms Input-Verzögerung gegen Enter-Spam
        self._last_purchase = None  # ("name", timestamp) für Feedback

    def get_cost(self, category):
        """Berechnet aktuelle Kosten für ein Upgrade"""
        config = UPGRADE_CONFIG[category]
        level = self.upgrade_levels[category]
        max_lvl = config["max_level"]

        # Ship Upgrade: max abhängig von Start-Stage (Stage 4 = kein Upgrade möglich)
        if category == "next_ship":
            max_lvl = 4 - self.ship_stage  # Stage 1→3 upgrades, Stage 3→1, Stage 4→0
            if max_lvl <= 0:
                return None

        if level >= max_lvl:
            return None
        return int(config["base_cost"] * (config.get("cost_multiplier", 1.5) ** level))

    def get_max_level(self, category):
        """Gibt das tatsächliche Max-Level zurück"""
        if category == "next_ship":
            return max(0, 4 - self.ship_stage)
        return UPGRADE_CONFIG[category]["max_level"]

    def handle_and_draw(self, screen, score, level_completed, kills, assets=None):
        """
        Returns:
            ("continue", score, upgrades_dict): Weiter zum nächsten Level
            "quit": Beenden
            None: Kein Input
        """
        screen.fill((0, 0, 0))
        cw, ch = screen.get_size()
        ui_scale = max(cw / 1920, ch / 1080) * 1.2

        # Fonts
        try:
            title_font = pygame.font.Font(resource_path("assets/fonts/Astralight.ttf"), int(80 * ui_scale))
            subtitle_font = pygame.font.Font(resource_path("assets/fonts/White On Black.ttf"), int(40 * ui_scale))
            info_font = pygame.font.Font(resource_path("assets/fonts/monofonto rg.otf"), int(24 * ui_scale))
            controls_font = pygame.font.Font(resource_path("assets/fonts/monofonto rg.otf"), int(20 * ui_scale))
        except:
            title_font = pygame.font.Font(None, int(80 * ui_scale))
            subtitle_font = pygame.font.Font(None, int(40 * ui_scale))
            info_font = pygame.font.Font(None, int(24 * ui_scale))
            controls_font = pygame.font.Font(None, int(20 * ui_scale))

        # Title
        title = title_font.render(f"LEVEL {level_completed} COMPLETE!", True, (100, 255, 100))
        title_shadow = title_font.render(f"LEVEL {level_completed} COMPLETE!", True, (0, 80, 0))
        screen.blit(title_shadow, title_shadow.get_rect(center=(cw // 2 + 3, int(60 * ui_scale) + 3)))
        screen.blit(title, title.get_rect(center=(cw // 2, int(60 * ui_scale))))

        # Score + Kills
        score_text = subtitle_font.render(f"Score: {score:,}  |  Kills: {kills}", True, (255, 255, 100))
        screen.blit(score_text, score_text.get_rect(center=(cw // 2, int(130 * ui_scale))))

        # Current Ship Info
        stage_names = {1: "Rookie", 2: "Veteran", 3: "Elite", 4: "Legend"}
        current_stage = self.ship_stage + self.upgrade_levels.get("next_ship", 0)
        ship_info = subtitle_font.render(
            f"Ship: Stage {current_stage} - {stage_names.get(current_stage, '???')}",
            True, (100, 200, 255)
        )
        screen.blit(ship_info, ship_info.get_rect(center=(cw // 2, int(180 * ui_scale))))

        # Upgrade-Label
        upgrade_label = subtitle_font.render("UPGRADES", True, (200, 200, 255))
        screen.blit(upgrade_label, upgrade_label.get_rect(center=(cw // 2, int(230 * ui_scale))))

        # Upgrade-Optionen (2 Spalten)
        start_y = int(280 * ui_scale)
        box_height = int(70 * ui_scale)
        box_width = int(520 * ui_scale)
        gap_x = int(30 * ui_scale)
        gap_y = int(12 * ui_scale)
        col_left_x = cw // 2 - box_width - gap_x // 2
        col_right_x = cw // 2 + gap_x // 2

        for i, cat in enumerate(self.categories):
            config = UPGRADE_CONFIG[cat]
            level = self.upgrade_levels[cat]
            cost = self.get_cost(cat)
            max_lvl = self.get_max_level(cat)

            # 2-Spalten Layout
            col = i % 2
            row = i // 2
            x = col_left_x if col == 0 else col_right_x
            y = start_y + row * (box_height + gap_y)

            is_selected = (i == self.selected)
            is_maxed = (cost is None)
            can_afford = (not is_maxed and score >= cost)

            # Box
            box_rect = pygame.Rect(x, y, box_width, box_height)

            if is_selected:
                pygame.draw.rect(screen, (40, 40, 80), box_rect)
                border_color = (255, 215, 0) if can_afford else (100, 200, 255)
                pygame.draw.rect(screen, border_color, box_rect, 3)
            else:
                pygame.draw.rect(screen, (20, 20, 40), box_rect)
                pygame.draw.rect(screen, (50, 50, 70), box_rect, 1)

            pad = int(12 * ui_scale)

            # Name
            name_color = (255, 255, 255) if is_selected else (160, 160, 160)
            # Ship Upgrade: Zeige Stage-Transition
            if cat == "next_ship" and not is_maxed:
                next_stage = current_stage + 1
                display_name = f"{config['name']}: Stage {current_stage} → {next_stage}"
            else:
                display_name = f"{config['name']} ({level}/{max_lvl})"
            name_text = info_font.render(display_name, True, name_color)
            screen.blit(name_text, (box_rect.x + pad, box_rect.y + pad))

            # Beschreibung + Kosten auf einer Zeile
            desc_text = info_font.render(config["description"], True, (120, 120, 120))
            screen.blit(desc_text, (box_rect.x + pad, box_rect.y + pad + int(28 * ui_scale)))

            if is_maxed:
                cost_surface = info_font.render("MAX", True, (100, 255, 100))
            elif can_afford:
                cost_surface = info_font.render(f"{cost:,} pts", True, (255, 255, 100))
            else:
                cost_surface = info_font.render(f"{cost:,} pts", True, (255, 80, 80))
            screen.blit(cost_surface, (box_rect.right - cost_surface.get_width() - pad,
                                       box_rect.y + pad + int(14 * ui_scale)))

        # Purchase Feedback
        now = pygame.time.get_ticks()
        if self._last_purchase and now - self._last_purchase[1] < 1500:
            feedback = info_font.render(f"Purchased: {self._last_purchase[0]}!", True, (100, 255, 100))
            screen.blit(feedback, feedback.get_rect(center=(cw // 2, ch - int(80 * ui_scale))))

        # Controls
        controls = controls_font.render(
            "[UP/DOWN/LEFT/RIGHT] Select - [ENTER] Buy - [SPACE] Continue",
            True, (150, 150, 150)
        )
        screen.blit(controls, controls.get_rect(center=(cw // 2, ch - int(40 * ui_scale))))

        # Event Handling (mit Input-Delay gegen Enter-Spam)
        input_ready = (now - self._created_at) > self._input_delay
        result = None
        cols = 2
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN and input_ready:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - cols) % len(self.categories)
                elif event.key == pygame.K_DOWN:
                    new = self.selected + cols
                    if new < len(self.categories):
                        self.selected = new
                elif event.key == pygame.K_LEFT:
                    if self.selected % cols > 0:
                        self.selected -= 1
                elif event.key == pygame.K_RIGHT:
                    if self.selected % cols < cols - 1 and self.selected + 1 < len(self.categories):
                        self.selected += 1
                elif event.key == pygame.K_RETURN:
                    cat = self.categories[self.selected]
                    cost = self.get_cost(cat)
                    if cost is not None and score >= cost:
                        score -= cost
                        self.upgrade_levels[cat] += 1
                        self._last_purchase = (UPGRADE_CONFIG[cat]["name"], now)
                elif event.key == pygame.K_SPACE:
                    result = ("continue", score, dict(self.upgrade_levels))

        pygame.display.flip()
        return result
