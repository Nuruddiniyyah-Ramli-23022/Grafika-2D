# mini_game_kelinci_rumput.py
import pygame
import sys
import random

# ---------------------------
# KONFIGURASI
# ---------------------------
pygame.init()
SCREEN_W, SCREEN_H = 800, 600
FPS = 60

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY = (135, 206, 235)
GREEN = (34, 139, 34)
ORANGE = (255, 140, 0)
RED = (220, 20, 60)

# Game settings
PLAYER_SPEED = 6
FALL_START_SPEED = 2
FALL_SPEED_INCREMENT = 0.3
SPAWN_INTERVAL = 1300
MAX_LIVES = 3
PLAYER_SIZE = (100, 150)

# ---------------------------
# INISIALISASI LAYAR
# ---------------------------
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Mini Game: Kelinci Makan Wortel")
clock = pygame.time.Clock()

font_small = pygame.font.SysFont("arial", 24)
font_big = pygame.font.SysFont("arial", 48)

# ---------------------------
# LOAD GAMBAR (AMAN)
# ---------------------------
def load_image_scaled(path, fallback_fn=None, size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except:
        surf = fallback_fn()
        if size:
            surf = pygame.transform.scale(surf, size)
        return surf

def draw_player_surface():
    surf = pygame.Surface((80, 60), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (200, 200, 200), (10, 10, 60, 40))
    pygame.draw.polygon(surf, (220,220,220), [(25,10),(30,-20),(35,10)])
    pygame.draw.circle(surf, BLACK, (55, 30), 4)
    return surf

def draw_carrot_surface():
    surf = pygame.Surface((28, 40), pygame.SRCALPHA)
    pygame.draw.polygon(surf, ORANGE, [(14,0),(28,30),(0,30)])
    pygame.draw.rect(surf, GREEN, (10,28,8,12))
    return surf

player_img = load_image_scaled(
    "kelinciku.webp",
    fallback_fn=draw_player_surface,
    size=PLAYER_SIZE
)

carrot_img = load_image_scaled(
    "wortel.png",
    fallback_fn=draw_carrot_surface,
    size=(28, 40)
)

# ---------------------------
# LOAD BACKGROUND GUNUNG
# ---------------------------
try:
    background = pygame.image.load("gunung.webp").convert()
    background = pygame.transform.scale(background, (SCREEN_W, SCREEN_H))
except:
    background = None
    print("Background tidak ditemukan")

# ---------------------------
# RUMPUT
# ---------------------------
class Grass(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 30), pygame.SRCALPHA)
        for i in range(6):
            px = random.randint(0, 40)
            tinggi = random.randint(10, 30)
            warna = (20, random.randint(120,160), 20)
            pygame.draw.line(self.image, warna, (px, 30), (px-5, 30-tinggi), 3)
            pygame.draw.line(self.image, warna, (px, 30), (px+5, 30-tinggi), 3)
        self.rect = self.image.get_rect(midbottom=(x, y))

# ---------------------------
# PLAYER
# ---------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect(midbottom=(SCREEN_W//2, SCREEN_H-10))

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += PLAYER_SPEED

        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, SCREEN_W)

# ---------------------------
# WORTEL
# ---------------------------
class Carrot(pygame.sprite.Sprite):
    def __init__(self, x, speed):
        super().__init__()
        self.image = carrot_img
        self.rect = self.image.get_rect(midtop=(x, -40))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_H:
            self.kill()

# ---------------------------
# HUD
# ---------------------------
def draw_hud(score, lives, level):
    screen.blit(font_small.render(f"Skor: {score}", True, BLACK), (10,10))
    screen.blit(font_small.render(f"Level: {level}", True, BLACK), (10,36))
    screen.blit(font_small.render("❤"*lives, True, RED), (SCREEN_W-100,10))

def show_text(lines):
    screen.fill(SKY)
    y = SCREEN_H//2 - 50
    for text, font in lines:
        surf = font.render(text, True, BLACK)
        rect = surf.get_rect(center=(SCREEN_W//2, y))
        screen.blit(surf, rect)
        y += 50
    pygame.display.flip()

    wait = True
    while wait:
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                wait = False
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

# ---------------------------
# MAIN GAME
# ---------------------------
def main():
    player = Player()
    player_group = pygame.sprite.GroupSingle(player)
    carrots = pygame.sprite.Group()
    grasses = pygame.sprite.Group()

    for i in range(25):
        grasses.add(Grass(random.randint(0, SCREEN_W), SCREEN_H-5))

    score = 0
    lives = MAX_LIVES
    level = 1
    fall_speed = FALL_START_SPEED
    spawn_time = pygame.time.get_ticks()

    show_text([
        ("MINI GAME KELINCI MAKAN WORTEL", font_big),
        ("Gerakkan ← → atau A D", font_small),
        ("Tekan tombol apa saja", font_small)
    ])

    while True:
        clock.tick(FPS)
        now = pygame.time.get_ticks()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        keys = pygame.key.get_pressed()

        if now - spawn_time > SPAWN_INTERVAL:
            spawn_time = now
            carrots.add(Carrot(random.randint(40, SCREEN_W-40), fall_speed))

        player_group.update(keys)
        carrots.update()

        hit = pygame.sprite.spritecollide(player, carrots, True)
        if hit:
            score += 10

        for c in carrots:
            if c.rect.top > SCREEN_H:
                lives -= 1
                c.kill()
                if lives <= 0:
                    show_text([
                        ("GAME OVER", font_big),
                        (f"Skor: {score}", font_small),
                        ("Tekan tombol untuk keluar", font_small)
                    ])
                    pygame.quit(); sys.exit()

        level = score // 100 + 1
        fall_speed = FALL_START_SPEED + level * 0.3

        # DRAW
        if background:
            screen.blit(background, (0,0))
        else:
            screen.fill(SKY)

        pygame.draw.rect(screen, GREEN, (0, SCREEN_H-80, SCREEN_W, 80))
        grasses.draw(screen)
        carrots.draw(screen)
        player_group.draw(screen)
        draw_hud(score, lives, level)

        pygame.display.flip()

# ---------------------------
# START
# ---------------------------
if __name__ == "__main__":
    main()
