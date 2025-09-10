import pygame
import sys
import random

pygame.init()

# ----- Screen config -----
WIDTH, HEIGHT = 1920, 1080  # Full HD
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Parallax - Spaceship Arcade 2.5D')

# ----- Colors -----
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
LIGHT_BLUE = (0, 200, 200)
YELLOW = (255, 255, 0)

# ----- Clock -----
clock = pygame.time.Clock()

# ----- Assets -----
ship1_img = pygame.image.load("Spaceship2.0Frame.png").convert_alpha()
ship1_img = pygame.transform.scale(ship1_img, (141, 90))

ship2_img = pygame.image.load("SpaceshipFrame.png").convert_alpha()
ship2_img = pygame.transform.scale(ship2_img, (141, 90))

# ----- Game states -----
MENU = "menu"
CHARACTER_SELECT = "character_select"
GAME = "game"
PAUSE = "pause"
game_state = MENU

# ----- Player config -----
ship_img = None
ship = pygame.Rect(50, (HEIGHT // 2) - (90 // 2), 141, 90)
ship_speed = 7

# ----- Bullets -----
bullets = []
bullet_speed = 15

# ----- Stars -----
stars = []
def reset_stars():
    global stars
    stars = []
    for i in range(120):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        speed = random.choice([1, 2, 3])
        size = speed
        stars.append([x, y, speed, size])
reset_stars()

# ----- Enemies -----
enemies = []
spawn_timer = 0

# ----- Reset game function -----
def reset_game():
    global bullets, enemies, spawn_timer, ship, ship_img
    bullets = []
    enemies = []
    spawn_timer = 0
    ship_img = None
    ship = pygame.Rect(50, (HEIGHT // 2) - (90 // 2), 141, 90)
    reset_stars()

# =========================================
# ----------- GAME LOOP -------------------
# =========================================
while True:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # ----- MENU -----
        if game_state == MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:  # iniciar jogo
                    game_state = CHARACTER_SELECT
                if event.key == pygame.K_2:  # sair
                    pygame.quit()
                    sys.exit()

        # ----- CHARACTER SELECTION -----
        elif game_state == CHARACTER_SELECT:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    ship_img = ship1_img
                    game_state = GAME
                if event.key == pygame.K_2:
                    ship_img = ship2_img
                    game_state = GAME

        # ----- GAME -----
        elif game_state == GAME:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = PAUSE  # pausa o jogo
                if event.key == pygame.K_SPACE:
                    bullets.append(pygame.Rect(ship.right - 55, ship.centery - 2, 12, 4))

        # ----- PAUSE -----
        elif game_state == PAUSE:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:  # continuar
                    game_state = GAME
                if event.key == pygame.K_2:  # voltar ao menu (reset jogo)
                    reset_game()
                    game_state = MENU
                if event.key == pygame.K_3:  # sair
                    pygame.quit()
                    sys.exit()

    # =========================================
    # ----------- DRAW SCREENS ----------------
    # =========================================

    # ----- MENU -----
    if game_state == MENU:
        screen.fill(BLACK)
        font = pygame.font.SysFont(None, 80)
        title = font.render("PARALLAX SPACESHIP", True, WHITE)
        start = font.render("1 - Jogar", True, LIGHT_BLUE)
        quit_game = font.render("2 - Sair", True, RED)

        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))
        screen.blit(start, (WIDTH // 2 - start.get_width() // 2, HEIGHT // 2))
        screen.blit(quit_game, (WIDTH // 2 - quit_game.get_width() // 2, HEIGHT // 2 + 100))

    # ----- CHARACTER SELECTION -----
    elif game_state == CHARACTER_SELECT:
        screen.fill(BLACK)
        font = pygame.font.SysFont(None, 60)
        text = font.render("Selecione seu personagem (1 ou 2)", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 150))

        screen.blit(ship1_img, (WIDTH // 3 - ship1_img.get_width() // 2, HEIGHT // 2))
        screen.blit(ship2_img, (2 * WIDTH // 3 - ship2_img.get_width() // 2, HEIGHT // 2))

    # ----- GAME -----
    elif game_state == GAME:
        # Movimento nave
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and ship.top > 0:
            ship.y -= ship_speed
        if keys[pygame.K_DOWN] and ship.bottom < HEIGHT:
            ship.y += ship_speed
        if keys[pygame.K_LEFT] and ship.left > 0:
            ship.x -= ship_speed
        if keys[pygame.K_RIGHT] and ship.right < WIDTH:
            ship.x += ship_speed

        # Movimento balas
        for bullet in bullets[:]:
            bullet.x += bullet_speed
            if bullet.x > WIDTH:
                bullets.remove(bullet)

        # Movimento estrelas
        for star in stars:
            star[0] -= star[2]
            if star[0] < 0:
                star[0] = WIDTH
                star[1] = random.randint(0, HEIGHT)

        # Spawn inimigos
        spawn_timer += 1
        if spawn_timer > 60:
            spawn_timer = 0
            y = random.randint(50, HEIGHT - 50)
            enemies.append({'x': WIDTH + 50, 'y': y, 'size': 15, 'speed': 3})

        # Movimento inimigos
        for enemy in enemies[:]:
            enemy['x'] -= enemy['speed']
            enemy['size'] += 0.15
            if enemy['x'] < -50:
                enemies.remove(enemy)

        # Colisão
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                enemy_rect = pygame.Rect(enemy['x'], enemy['y'], enemy['size'], enemy['size'])
                if bullet.colliderect(enemy_rect):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    break

        # ----- Draw -----
        screen.fill(BLACK)
        for star in stars:
            pygame.draw.circle(screen, WHITE, (star[0], star[1]), star[3])

        screen.blit(ship_img, ship)

        for bullet in bullets:
            pygame.draw.rect(screen, YELLOW, bullet)

        for enemy in enemies:
            pygame.draw.rect(screen, RED, (enemy['x'], enemy['y'], enemy['size'], enemy['size']))

    # ----- PAUSE -----
    elif game_state == PAUSE:
        screen.fill(BLACK)
        font = pygame.font.SysFont(None, 80)
        pause_text = font.render("PAUSADO", True, WHITE)
        resume = font.render("1 - Continuar", True, LIGHT_BLUE)
        main_menu = font.render("2 - Voltar ao Menu", True, YELLOW)
        quit_game = font.render("3 - Sair", True, RED)

        screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 4))
        screen.blit(resume, (WIDTH // 2 - resume.get_width() // 2, HEIGHT // 2))
        screen.blit(main_menu, (WIDTH // 2 - main_menu.get_width() // 2, HEIGHT // 2 + 100))
        screen.blit(quit_game, (WIDTH // 2 - quit_game.get_width() // 2, HEIGHT // 2 + 200))

    pygame.display.flip()