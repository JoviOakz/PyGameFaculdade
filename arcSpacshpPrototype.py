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
ship1_img = pygame.image.load("SpaceshipFrame.png").convert_alpha()
ship2_img = pygame.image.load("Spaceship2Frame.png").convert_alpha()

# =========================================
# ----------- SHIP CLASS ------------------
# =========================================
class Ship:
    def __init__(self, img, speed, bullet_color, bullet_speed, size, shoot_type, shoot_cooldown):
        self.img = pygame.transform.scale(img, size)
        self.rect = self.img.get_rect()
        self.rect.x = 50
        self.rect.y = (HEIGHT // 2) - (self.rect.height // 2)
        self.speed = speed
        self.bullet_color = bullet_color
        self.bullet_speed = bullet_speed
        self.shoot_type = shoot_type              # "bullet" ou "laser"
        self.shoot_cooldown = shoot_cooldown      # em ms
        self.last_shot_time = 0                   # controla o cooldown

    def move(self, keys):
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # Correção dinâmica de limites com base no tamanho da nave
        margin = 185
        margin_y = int(self.rect.height * 0.98)

        play_area = pygame.Rect(
            margin,
            margin_y,
            WIDTH - 4 * margin,
            HEIGHT - 2 * margin_y
        )
        self.rect.clamp_ip(play_area)

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time < self.shoot_cooldown:
            return None  # ainda em cooldown

        self.last_shot_time = now

        if self.shoot_type == "bullet":
            bullet = pygame.Rect(self.rect.right - 20, self.rect.centery - 3, 20, 6)
            return {"type": "bullet", "rect": bullet}

        elif self.shoot_type == "laser":
            # Laser atravessa a tela e dura 1s
            laser = pygame.Rect(self.rect.right - 10, self.rect.top+10, WIDTH, self.rect.height-20)
            return {"type": "laser", "rect": laser, "expire": now + 1000}

# =========================================
# ----------- GAME STATES -----------------
# =========================================
MENU = "menu"
CHARACTER_SELECT = "character_select"
GAME = "game"
PAUSE = "pause"
game_state = MENU

# ----- Player config -----
ship = None

# Configs de cada nave
ship1_cfg = {
    "img": ship1_img,
    "speed": 5,
    "bullet_color": YELLOW,
    "bullet_speed": 12,
    "size": (160, 110),
    "shoot_type": "laser",
    "shoot_cooldown": 2000   # 2 segundos de cooldown
}

ship2_cfg = {
    "img": ship2_img,
    "speed": 9,
    "bullet_color": WHITE,
    "bullet_speed": 20,
    "size": (141, 90),
    "shoot_type": "bullet",
    "shoot_cooldown": 20    # 0.2 segundos de cooldown
}

# ----- Bullets -----
bullets = []

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
    global bullets, enemies, spawn_timer, ship
    bullets = []
    enemies = []
    spawn_timer = 0
    ship = None
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
                    ship = Ship(**ship1_cfg)
                    game_state = GAME
                if event.key == pygame.K_2:
                    ship = Ship(**ship2_cfg)
                    game_state = GAME

        # ----- GAME -----
        elif game_state == GAME:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = PAUSE  # pausa o jogo
                if event.key == pygame.K_SPACE and ship:
                    shot = ship.shoot()
                    if shot:
                        bullets.append(shot)

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

        preview1 = pygame.transform.scale(ship1_img, ship1_cfg["size"])
        preview2 = pygame.transform.scale(ship2_img, ship2_cfg["size"])
        screen.blit(preview1, (WIDTH // 3 - preview1.get_width() // 2, HEIGHT // 2))
        screen.blit(preview2, (2 * WIDTH // 3 - preview2.get_width() // 2, HEIGHT // 2))

    # ----- GAME -----
    elif game_state == GAME and ship:
        # Movimento nave
        keys = pygame.key.get_pressed()
        ship.move(keys)

        # Movimento balas/lasers
        now = pygame.time.get_ticks()
        for bullet in bullets[:]:
            if bullet["type"] == "bullet":
                bullet["rect"].x += ship.bullet_speed
                if bullet["rect"].x > WIDTH:
                    bullets.remove(bullet)

            elif bullet["type"] == "laser":
                if now > bullet["expire"]:
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
                if bullet["rect"].colliderect(enemy_rect):
                    enemies.remove(enemy)
                    if bullet["type"] == "bullet":
                        bullets.remove(bullet)  # laser não desaparece ao colidir
                    break

        # ----- Draw -----
        screen.fill(BLACK)
        for star in stars:
            pygame.draw.circle(screen, WHITE, (star[0], star[1]), star[3])

        screen.blit(ship.img, ship.rect)

        for bullet in bullets:
            pygame.draw.rect(screen, ship.bullet_color, bullet["rect"])

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