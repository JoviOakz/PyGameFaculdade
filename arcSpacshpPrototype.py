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
GRAY = (50, 50, 50)

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
        self.shoot_type = shoot_type
        self.shoot_cooldown = shoot_cooldown
        self.last_shot_time = 0
        self.laser_active = False
        self.laser_start_time = 0

    def move(self, keys):
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
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

    def trigger_laser(self):
        now = pygame.time.get_ticks()
        if not self.laser_active and now - self.last_shot_time > self.shoot_cooldown:
            self.laser_active = True
            self.laser_start_time = now
            self.last_shot_time = now

    def shoot(self, holding=None):
        now = pygame.time.get_ticks()
        if self.shoot_type == "laser":
            if self.laser_active:
                if now - self.laser_start_time > 1125:  # 2 segundos
                    self.laser_active = False
                    return None
                else:
                    laser = pygame.Rect(self.rect.right - 10, self.rect.top + 10, WIDTH, self.rect.height - 20)
                    return {"type": "laser", "rect": laser}
            return None

        elif self.shoot_type == "bullet":
            if now - self.last_shot_time < self.shoot_cooldown:
                return None
            self.last_shot_time = now
            bullet = pygame.Rect(self.rect.right - 20, self.rect.centery - 3, 20, 6)
            return {"type": "bullet", "rect": bullet}

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
    "speed": 4,
    "bullet_color": YELLOW,
    "bullet_speed": 10,
    "size": (160, 110),
    "shoot_type": "laser",
    "shoot_cooldown": 3500   # 2 segundos de cooldown
}

ship2_cfg = {
    "img": ship2_img,
    "speed": 10,
    "bullet_color": WHITE,
    "bullet_speed": 26,
    "size": (141, 90),
    "shoot_type": "bullet",
    "shoot_cooldown": 250    # 0.08 segundos de cooldown
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
# ----------- CHARACTER SELECT VARS -------
# =========================================
cols, rows = 3, 3
slot_size = 150
spacing = 25
total_width = cols * slot_size + (cols - 1) * spacing
total_height = rows * slot_size + (rows - 1) * spacing
start_x = WIDTH // 2 - total_width // 2
start_y = 350

slots = []
idx = 1
for row in range(rows):
    for col in range(cols):
        x = start_x + col * (slot_size + spacing)
        y = start_y + row * (slot_size + spacing)
        rect = pygame.Rect(x, y, slot_size, slot_size)
        slots.append({"rect": rect, "index": idx})
        idx += 1

selected_slot = 0  # começa no primeiro
score = 0  # pontuação inicial

# =========================================
# ----------- GAME LOOP -------------------
# =========================================
while True:
    clock.tick(60)

    keys = pygame.key.get_pressed()

    events = pygame.event.get()
    for event in events:
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
                if event.key == pygame.K_RIGHT and (selected_slot + 1) % cols != 0:
                    selected_slot += 1
                elif event.key == pygame.K_LEFT and selected_slot % cols != 0:
                    selected_slot -= 1
                elif event.key == pygame.K_DOWN and selected_slot + cols < len(slots):
                    selected_slot += cols
                elif event.key == pygame.K_UP and selected_slot - cols >= 0:
                    selected_slot -= cols
                elif event.key == pygame.K_SPACE:  # confirma escolha
                    chosen_index = slots[selected_slot]["index"]
                    if chosen_index == 1:
                        score=0
                        ship = Ship(**ship1_cfg)
                        game_state = GAME
                    elif chosen_index == 2:
                        score=0
                        ship = Ship(**ship2_cfg)
                        game_state = GAME

        # ----- GAME -----
        elif game_state == GAME:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = PAUSE  # pausa o jogo
                if ship and ship.shoot_type == "laser" and event.key == pygame.K_SPACE:
                    ship.trigger_laser()  # dispara laser por 2 segundos
                if ship and ship.shoot_type == "bullet" and event.key == pygame.K_SPACE:
                    shot = ship.shoot(False)
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
        for star in stars:
            pygame.draw.circle(screen, WHITE, (star[0], star[1]), star[3])

        font_title = pygame.font.SysFont(None, 120, bold=True)
        font_btn = pygame.font.SysFont(None, 80)

        title = font_title.render("PARALLAX SPACESHIP", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))

        start_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2, 400, 80)
        pygame.draw.rect(screen, LIGHT_BLUE, start_rect, border_radius=10)
        start_txt = font_btn.render("1 - Jogar", True, BLACK)
        screen.blit(start_txt, (start_rect.centerx - start_txt.get_width() // 2, start_rect.centery - start_txt.get_height() // 2))

        quit_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 + 120, 400, 80)
        pygame.draw.rect(screen, RED, quit_rect, border_radius=10)
        quit_txt = font_btn.render("2 - Sair", True, BLACK)
        screen.blit(quit_txt, (quit_rect.centerx - quit_txt.get_width() // 2, quit_rect.centery - quit_txt.get_height() // 2))

    # ----- CHARACTER SELECTION -----
    elif game_state == CHARACTER_SELECT:
        screen.fill(BLACK)
        font = pygame.font.SysFont(None, 80, bold=True)
        text = font.render("ESCOLHA SUA NAVE", True, YELLOW)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 180))

        for i, slot in enumerate(slots):
            rect = slot["rect"]
            idx = slot["index"]

            if idx == 1:
                preview = pygame.transform.scale(ship1_img, (slot_size-20, slot_size-20))
                screen.blit(preview, (rect.x+10, rect.y+10))
            elif idx == 2:
                preview = pygame.transform.scale(ship2_img, (slot_size-20, slot_size-20))
                screen.blit(preview, (rect.x+10, rect.y+10))
            else:
                pygame.draw.rect(screen, GRAY, rect)
                pygame.draw.rect(screen, WHITE, rect, 2)
                lock_txt = pygame.font.SysFont(None, 40).render("???", True, WHITE)
                screen.blit(lock_txt, (rect.centerx - lock_txt.get_width()//2, rect.centery - lock_txt.get_height()//2))

            if i == selected_slot:
                pygame.draw.rect(screen, YELLOW, rect, 6)

        instr = pygame.font.SysFont(None, 50).render("Use as setas e Espaço para confirmar", True, WHITE)
        screen.blit(instr, (WIDTH // 2 - instr.get_width() // 2, HEIGHT - 100))

    # ----- GAME -----
    elif game_state == GAME and ship:
        ship.move(keys)

        if ship.shoot_type == "laser":
            shot = ship.shoot()
            if shot:
                if len(bullets) == 0 or bullets[-1]["type"] != "laser":
                    bullets.append(shot)
                else:
                    bullets[-1] = shot
            else:
                bullets = [b for b in bullets if b["type"] != "laser"]

        # Movimento balas normais
        for bullet in bullets[:]:
            if bullet["type"] == "bullet":
                bullet["rect"].x += ship.bullet_speed
                if bullet["rect"].x > WIDTH:
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
                        bullets.remove(bullet)
                    score += 10  # adiciona 10 pontos a cada inimigo destruído
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

        # Desenhar a pontuação
        font_score = pygame.font.SysFont(None, 60, bold=True)
        score_text = font_score.render(f"Pontos: {score}", True, YELLOW)
        screen.blit(score_text, (195, 115))

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