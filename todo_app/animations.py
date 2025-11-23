import math
import random
import pygame


class WaveBackground:
    """Latar grid monokrom yang bergerak mengikuti kursor."""

    def __init__(self, width: int, height: int, line_count: int = 6):
        self.width = width
        self.height = height
        self.line_count = line_count
        self.time = 0.0
        self.speed = 0.4
        self.amplitude = 20
        self.spacing = height // (line_count + 1)
        self.gradient_blobs = [
            {
                "origin": (width * 0.25, height * 0.35),
                "radius": height * 0.75,
                "color": (220, 220, 220),
                "alpha": 28,
                "phase": 0.0,
                "drift_x": 22,
                "drift_y": 18,
            },
            {
                "origin": (width * 0.7, height * 0.25),
                "radius": height * 0.55,
                "color": (180, 180, 180),
                "alpha": 32,
                "phase": 1.1,
                "drift_x": 18,
                "drift_y": 14,
            },
            {
                "origin": (width * 0.55, height * 0.75),
                "radius": height * 0.65,
                "color": (140, 140, 140),
                "alpha": 26,
                "phase": 2.3,
                "drift_x": 26,
                "drift_y": 20,
            },
        ]
        self.wave_colors = [
            (215, 215, 215),
            (180, 180, 180),
            (140, 140, 140),
            (200, 200, 200),
        ]

    def update(self, dt: float):
        """Menambah waktu internal untuk menganimasikan semua elemen."""
        self.time += dt * self.speed

    def draw(self, surface: pygame.Surface, mouse_pos):
        """Menggambar latar lengkap: gradien lembut, grid, dan gelombang."""
        surface.fill((6, 6, 8))
        mx, my = mouse_pos

        self._draw_gradient_blobs(surface, mx, my)
        self._draw_grid(surface, mx, my)
        self._draw_waves(surface, mx)

    def _draw_gradient_blobs(self, surface: pygame.Surface, mx: float, my: float):
        # Lapisan blob untuk memberi kedalaman lembut di belakang grid.
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for blob in self.gradient_blobs:
            wobble = 1 + 0.08 * math.sin(self.time * 0.8 + blob["phase"])
            dx = math.sin(self.time * 0.6 + blob["phase"]) * blob["drift_x"] + (mx - self.width / 2) * 0.02
            dy = math.cos(self.time * 0.5 + blob["phase"]) * blob["drift_y"] + (my - self.height / 2) * 0.01
            center = (int(blob["origin"][0] + dx), int(blob["origin"][1] + dy))
            radius = int(blob["radius"] * wobble)
            color = (*blob["color"], blob["alpha"])
            pygame.draw.circle(overlay, color, center, radius)
        surface.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def _draw_grid(self, surface: pygame.Surface, mx: float, my: float):
        grid_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        line_color = (255, 255, 255, 14)
        for x in range(-80, self.width + 80, 80):
            offset = math.sin(self.time + x * 0.02) * 6 + (mx - self.width / 2) * 0.012
            pygame.draw.line(grid_surface, line_color, (x + offset, 0), (x + offset, self.height))
        for y in range(-80, self.height + 80, 80):
            offset = math.cos(self.time * 0.7 + y * 0.025) * 6 + (my - self.height / 2) * 0.01
            pygame.draw.line(grid_surface, line_color, (0, y + offset), (self.width, y + offset))
        surface.blit(grid_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def _draw_waves(self, surface: pygame.Surface, mx: float):
        # Gelombang mengikuti kursor untuk memberi rasa responsif.
        for i in range(1, self.line_count + 1):
            points = []
            y_base = i * self.spacing
            color = self.wave_colors[i % len(self.wave_colors)]
            for x in range(0, self.width, 12):
                wobble = math.sin((x * 0.024) + self.time + i) * (self.amplitude + i * 2)
                follow = (mx - self.width / 2) * 0.02 + math.sin(self.time + i) * 6
                y = y_base + wobble + follow
                points.append((x, y))
            pygame.draw.lines(surface, color, False, points, 2)


class Vibration:
    """Generator jitter halus untuk umpan balik pengetikan."""

    def __init__(self):
        self.phase = random.random() * math.tau
        self.magnitude = 2

    def jitter(self, dt: float) -> tuple[int, int]:
        """Menghasilkan offset kecil yang berubah seiring waktu."""
        self.phase += dt * 20
        dx = int(math.sin(self.phase) * self.magnitude)
        dy = int(math.cos(self.phase * 1.3) * self.magnitude)
        return dx, dy

