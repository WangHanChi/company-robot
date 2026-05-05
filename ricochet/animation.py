import math
import random
import pygame


def ease_out_cubic(t):
    return 1 - (1 - t) ** 3


class SlideAnimation:
    def __init__(self, color, start_cell, end_cell, direction, duration_ms=180,
                 won=False):
        self.color = color
        self.start = start_cell
        self.end = end_cell
        self.direction = direction
        self.duration = duration_ms
        self.won = won
        self.t0 = pygame.time.get_ticks()

    @property
    def progress(self):
        return min(1.0, (pygame.time.get_ticks() - self.t0) / self.duration)

    @property
    def done(self):
        return self.progress >= 1.0

    def current_cell(self):
        e = ease_out_cubic(self.progress)
        sx, sy = self.start
        ex, ey = self.end
        return (sx + (ex - sx) * e, sy + (ey - sy) * e)


class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'color', 'life', 'born')

    def __init__(self, x, y, vx, vy, color, life=500):
        self.x = x; self.y = y
        self.vx = vx; self.vy = vy
        self.color = color
        self.life = life
        self.born = pygame.time.get_ticks()

    def age(self):
        return pygame.time.get_ticks() - self.born


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit_burst(self, x, y, color, count=14, speed_range=(0.05, 0.18), life=450):
        for _ in range(count):
            ang = random.uniform(0, 2 * math.pi)
            sp = random.uniform(*speed_range)
            self.particles.append(
                Particle(x, y, math.cos(ang) * sp, math.sin(ang) * sp, color, life))

    def emit_directional(self, x, y, dx, dy, color, count=10):
        if dx == 0 and dy == 0:
            return
        base_ang = math.atan2(-dy, -dx)
        for _ in range(count):
            ang = base_ang + random.uniform(-0.7, 0.7)
            sp = random.uniform(0.06, 0.20)
            self.particles.append(
                Particle(x, y, math.cos(ang) * sp, math.sin(ang) * sp, color, 380))

    def update(self, dt_ms):
        alive = []
        for p in self.particles:
            if p.age() < p.life:
                p.x += p.vx * dt_ms
                p.y += p.vy * dt_ms
                p.vy += 0.0004 * dt_ms
                alive.append(p)
        self.particles = alive

    def draw(self, screen):
        now = pygame.time.get_ticks()
        for p in self.particles:
            t = (now - p.born) / p.life
            r = max(1, int(4 * (1 - t)))
            pygame.draw.circle(screen, p.color, (int(p.x), int(p.y)), r)


class FlashEffect:
    def __init__(self, color, duration_ms=400, max_alpha=110):
        self.color = color
        self.duration = duration_ms
        self.max_alpha = max_alpha
        self.t0 = pygame.time.get_ticks()

    @property
    def done(self):
        return pygame.time.get_ticks() - self.t0 >= self.duration

    def alpha(self):
        t = (pygame.time.get_ticks() - self.t0) / self.duration
        return max(0, int(self.max_alpha * (1 - t)))
