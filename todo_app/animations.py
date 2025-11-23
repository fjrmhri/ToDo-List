import math
import random
import pygame


class WaveBackground:
    def __init__(self, width: int, height: int, line_count: int = 6):
        self.width = width
        self.height = height
        self.line_count = line_count
        self.time = 0.0
        self.speed = 0.4
        self.amplitude = 20
        self.spacing = height // (line_count + 1)

    def update(self, dt: float):
        self.time += dt * self.speed

    def draw(self, surface: pygame.Surface, mouse_pos):
        surface.fill((0, 0, 0))
        mx, my = mouse_pos
        for i in range(1, self.line_count + 1):
            points = []
            y_base = i * self.spacing
            for x in range(0, self.width, 16):
                offset = math.sin((x * 0.02) + self.time + i) * self.amplitude
                follow = (mx - self.width / 2) * 0.02 + math.sin(self.time + i) * 4
                y = y_base + offset + follow
                points.append((x, y))
            pygame.draw.lines(surface, (255, 255, 255), False, points, 1)


class Vibration:
    def __init__(self):
        self.phase = random.random() * math.tau
        self.magnitude = 2

    def jitter(self, dt: float) -> tuple[int, int]:
        self.phase += dt * 20
        dx = int(math.sin(self.phase) * self.magnitude)
        dy = int(math.cos(self.phase * 1.3) * self.magnitude)
        return dx, dy

