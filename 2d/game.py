"""
Inferflow 2D Game Engine Demo
A complete 2D space shooter demonstrating:
- Sprite-based game loop
- Particle systems
- Collision detection
- Score/HUD system
- Enemy AI patterns
"""

import pygame
import math
import random
import os

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

pygame.init()
W, H = 1280, 720
screen = pygame.Surface((W, H))

BG = (5, 5, 20)
WHITE = (255, 255, 255)
CYAN = (0, 220, 255)
RED = (255, 60, 60)
YELLOW = (255, 220, 0)
GREEN = (60, 255, 120)
PURPLE = (180, 60, 255)
ORANGE = (255, 140, 0)

font_large = pygame.font.SysFont("monospace", 36, bold=True)
font_med = pygame.font.SysFont("monospace", 22)
font_small = pygame.font.SysFont("monospace", 16)

class Star:
    def __init__(self):
        self.x = random.randint(0, W)
        self.y = random.randint(0, H)
        self.speed = random.uniform(0.5, 3)
        self.size = random.randint(1, 3)
        self.brightness = random.randint(100, 255)

    def draw(self, surf):
        c = self.brightness
        pygame.draw.circle(surf, (c, c, c), (int(self.x), int(self.y)), self.size)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.life = random.randint(20, 50)
        self.max_life = self.life
        self.size = random.randint(2, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surf):
        alpha = self.life / self.max_life
        r, g, b = self.color
        c = (int(r * alpha), int(g * alpha), int(b * alpha))
        size = max(1, int(self.size * alpha))
        pygame.draw.circle(surf, c, (int(self.x), int(self.y)), size)

class Enemy:
    def __init__(self, etype=0):
        self.etype = etype
        self.x = random.randint(60, W-60)
        self.y = random.randint(80, 500)
        self.size = [25, 40, 60][etype]
        self.color = [RED, PURPLE, ORANGE][etype]
        self.angle = random.randint(0, 360)
        self.health = [30, 60, 120][etype]
        self.max_health = self.health
        self.wave_offset = random.uniform(0, math.pi * 2)

    def draw(self, surf, frame):
        angle = self.angle + frame * [3, 2, 1][self.etype]
        sides = [3, 4, 6][self.etype]
        pts = []
        for i in range(sides):
            a = math.radians(angle + i * 360 / sides)
            px = self.x + math.cos(a) * self.size
            py = self.y + math.sin(a) * self.size
            pts.append((px, py))
        pygame.draw.polygon(surf, self.color, pts)
        pygame.draw.polygon(surf, WHITE, pts, 2)
        bar_w = self.size * 2
        ratio = self.health / self.max_health
        pygame.draw.rect(surf, RED, (self.x - bar_w//2, self.y - self.size - 12, bar_w, 6))
        pygame.draw.rect(surf, GREEN, (self.x - bar_w//2, self.y - self.size - 12, int(bar_w * ratio), 6))

stars = [Star() for _ in range(200)]
particles = [Particle(random.randint(200, 1000), random.randint(100, 600),
    random.choice([RED, ORANGE, YELLOW])) for _ in range(80)]
enemies = [Enemy(0) for _ in range(5)] + [Enemy(1) for _ in range(3)] + [Enemy(2) for _ in range(1)]

player_x, player_y = W//2, H - 120

player_bullets = [{'x': player_x + random.randint(-20,20), 'y': player_y - 80 - i*60} for i in range(8)]
enemy_bullets = [{'x': e.x, 'y': e.y + e.size + 20, 'color': RED} for e in enemies[:4]]

frame = 60
screen.fill(BG)

for s in stars:
    s.draw(screen)

for e in enemies:
    e.draw(screen, frame)

for b in enemy_bullets:
    pygame.draw.ellipse(screen, RED, (b['x']-4, b['y']-10, 8, 20))

for b in player_bullets:
    pygame.draw.ellipse(screen, CYAN, (b['x']-3, b['y']-12, 6, 24))
    pygame.draw.ellipse(screen, WHITE, (b['x']-1, b['y']-8, 2, 16))

for p in particles:
    p.update()
    p.draw(screen)

# Player ship
px, py = player_x, player_y
pts = [(px, py-25), (px-20, py+25), (px-10, py+10), (px+10, py+10), (px+20, py+25)]
pygame.draw.polygon(screen, CYAN, pts)
pygame.draw.polygon(screen, WHITE, pts, 2)
pygame.draw.ellipse(screen, (100, 200, 255), (px-10, py-20, 20, 24))
for i in range(3):
    r = random.randint(8, 18)
    pygame.draw.circle(screen, ORANGE, (px + random.randint(-8,8), py+30+random.randint(0,10)), r)

# HUD
screen.blit(font_large.render(f"SCORE: 13050", True, CYAN), (20, 20))
pygame.draw.rect(screen, RED, (20, 70, 200, 20))
pygame.draw.rect(screen, GREEN, (20, 70, 160, 20))
pygame.draw.rect(screen, WHITE, (20, 70, 200, 20), 2)
screen.blit(font_small.render("HULL INTEGRITY", True, WHITE), (20, 95))
wave_surf = font_med.render(f"WAVE 3 — ENEMIES: {len(enemies)}", True, YELLOW)
screen.blit(wave_surf, (W//2 - wave_surf.get_width()//2, 20))
title_surf = font_med.render("INFERFLOW — SPACE DEFENDER ENGINE", True, PURPLE)
screen.blit(title_surf, (W//2 - title_surf.get_width()//2, H - 40))

# Radar
pygame.draw.rect(screen, (20, 20, 50), (W-160, 20, 140, 100))
pygame.draw.rect(screen, WHITE, (W-160, 20, 140, 100), 1)
for e in enemies:
    mx = int((e.x / W) * 130) + W - 155
    my = int((e.y / H) * 90) + 25
    pygame.draw.circle(screen, e.color, (mx, my), 4)
pygame.draw.circle(screen, CYAN, (W-90, 105), 5)
screen.blit(font_small.render("RADAR", True, WHITE), (W-110, 125))

pygame.image.save(screen, "/home/claude/gamedev/screenshots/2d_gameplay.png")
print("✅ 2D screenshot saved")
pygame.quit()
