import pygame
from config.settings import WIDTH, HEIGHT, REFERENCE_WIDTH, REFERENCE_HEIGHT

class ResolutionManager:
    """Verwaltet Auflösungs-abhängige Skalierung"""

    def __init__(self, target_width=WIDTH, target_height=HEIGHT):
        self.target_width = target_width
        self.target_height = target_height

        # Berechne Skalierungsfaktoren
        self.scale_x = target_width / REFERENCE_WIDTH
        self.scale_y = target_height / REFERENCE_HEIGHT
        self.scale_factor = min(self.scale_x, self.scale_y)  # Uniform scaling

        print(f"Resolution: {target_width}x{target_height}")
        print(f"Scale factors: X={self.scale_x:.2f}, Y={self.scale_y:.2f}, Uniform={self.scale_factor:.2f}")

    def scale(self, value):
        """Uniform scaling"""
        return int(value * self.scale_factor)

    def scale_x(self, value):
        """X-axis scaling"""
        return int(value * self.scale_x)

    def scale_y(self, value):
        """Y-axis scaling"""
        return int(value * self.scale_y)

    def scale_pos(self, x, y):
        """Scale position"""
        return (self.scale_x(x), self.scale_y(y))

    def scale_size(self, width, height):
        """Scale size uniformly"""
        return (self.scale(width), self.scale(height))

    def scale_speed(self, speed):
        """Scale movement speed"""
        return max(1, self.scale(speed))

    def update_resolution(self, new_width, new_height):
        """Update resolution and recalculate scale factors"""
        self.target_width = new_width
        self.target_height = new_height
        self.scale_x = new_width / REFERENCE_WIDTH
        self.scale_y = new_height / REFERENCE_HEIGHT
        self.scale_factor = min(self.scale_x, self.scale_y)

# Global instance
resolution_manager = ResolutionManager()
