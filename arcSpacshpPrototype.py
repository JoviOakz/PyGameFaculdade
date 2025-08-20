import pygame
import sys
import random

pygame.init()

# ----- Screen config -----
WIDTH, HEIGHT = 1240, 760
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Parallax - Spaceship Arcade 2.5D")

# ----- Colors -----
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
LIGHT_BLUE = (0, 200, 200)

# ----- Clock -----
clock = pygame.time.Clock()

# ----- Spaceship config -----
ship = pygame.Rect(100, HEIGHT // 2, 40, 20)
ship_speed = 5

# ----- Bullets -----
bullets = []
bullet_speed = 10

# ----- Stars (Parallax) -----
stars = []
for i in range(50):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    speed = random.choice([1, 2, 3])
    size = speed
    stars.append([x, y, speed, size])

# ----- Enemies -----
enemies = []
spawn_timer = 0

# ----- Main loop -----
while True:
    clock.tick(60)

    # ----- Events -----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
                
            if event.key == pygame.K_SPACE:
                bullets.append(pygame.Rect(ship.right, ship.centery - 2, 10, 4))

    # ----- Spaceship movement -----
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and ship.top > 0:
        ship.y -= ship_speed
    if keys[pygame.K_DOWN] and ship.bottom < HEIGHT:
        ship.y += ship_speed
    if keys[pygame.K_LEFT] and ship.left > 0:
        ship.x -= ship_speed
    if keys[pygame.K_RIGHT] and ship.right < WIDTH:
        ship.x += ship_speed

    # ----- Bullets movement -----
    for bullet in bullets[:]:
        bullet.x += bullet_speed
        if bullet.x > WIDTH:
            bullets.remove(bullet)

    # ----- Stars movement -----
    for star in stars:
        star[0] -= star[2]
        if star[0] < 0:
            star[0] = WIDTH
            star[1] = random.randint(0, HEIGHT)

    # ----- Enemy spawn -----
    spawn_timer += 1
    if spawn_timer > 60:  # every 1 second
        spawn_timer = 0
        y = random.randint(50, HEIGHT - 50)
        enemies.append({"x": WIDTH + 50, "y": y, "size": 10, "speed": 2})

    # ----- Enemy movement and growth -----
    for enemy in enemies[:]:
        enemy["x"] -= enemy["speed"]
        enemy["size"] += 0.1  # grows to simulate coming closer

        # ----- Remove enemy out of screen -----
        if enemy["x"] < -50:
            enemies.remove(enemy)

    # ----- Bullets collision -----
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            enemy_rect = pygame.Rect(enemy["x"], enemy["y"], enemy["size"], enemy["size"])
            if bullet.colliderect(enemy_rect):
                bullets.remove(bullet)
                enemies.remove(enemy)
                break

    # ----- Screen background -----
    screen.fill(BLACK)

    # ----- Background stars -----
    for star in stars:
        pygame.draw.circle(screen, WHITE, (star[0], star[1]), star[3])

    # ----- Spaceship -----
    pygame.draw.rect(screen, LIGHT_BLUE, ship)

    # ----- Bullets -----
    for bullet in bullets:
        pygame.draw.rect(screen, (255, 255, 0), bullet)

    # ----- Enemies -----
    for enemy in enemies:
        pygame.draw.rect(screen, RED, (enemy["x"], enemy["y"], enemy["size"], enemy["size"]))

    pygame.display.flip()