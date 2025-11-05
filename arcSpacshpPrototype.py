import pygame
import sys
import random

pygame.init()

# =========================================
# ----------- CONFIGURAÇÕES GERAIS --------
# =========================================
WIDTH, HEIGHT = 1920, 1080  # Full HD
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Spaceship Arcade 2.5D')
clock = pygame.time.Clock()
spawn_margin = 100  # distância da borda superior e inferior para spawn de inimigos
difficulty_step = 100  # pontos para aumentar dificuldade
game_speed = 1  # multiplicador de velocidade do jogo

# ----- Cores -----
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
LIGHT_BLUE = (0, 200, 200)
YELLOW = (255, 255, 0)
GRAY = (50, 50, 50)
CYAN = (0, 255, 255)
PURPLE = (160, 80, 255)

# =========================================
# ----------- CARREGAMENTO DE ASSETS -------
# =========================================
ship1_img = pygame.image.load("assets/Spaceship1.png").convert_alpha()
ship2_img = pygame.image.load("assets/Spaceship2.png").convert_alpha()
enemy_imgs = [
    pygame.transform.scale(pygame.image.load("assets/Asteroid1.png").convert_alpha(), (80, 80)),
    pygame.transform.scale(pygame.image.load("assets/Asteroid2.png").convert_alpha(), (80, 80)),
    pygame.transform.scale(pygame.image.load("assets/Asteroid3.png").convert_alpha(), (80, 80))
]
trash_img = pygame.transform.scale(pygame.image.load("assets/TrashBag.png").convert_alpha(), (45, 45))

# =========================================
# ----------- CLASSE DA NAVE ---------------
# =========================================
class Ship:
    def __init__(self, img, speed, bullet_color, bullet_speed, size, shoot_type, shoot_cooldown):
        self.img = pygame.transform.scale(img, size)
        self.rect = self.img.get_rect(center=(100, HEIGHT // 2))
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

        margin = 185
        margin_y = int(self.rect.height * 0.98)
        play_area = pygame.Rect(
            margin, margin_y,
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
                if now - self.laser_start_time > 1125:
                    self.laser_active = False
                    return None
                return {"type": "laser", "rect": pygame.Rect(
                    self.rect.right - 10, self.rect.top + 15, WIDTH, self.rect.height - 30
                )}
            return None
        elif self.shoot_type == "bullet":
            if now - self.last_shot_time < self.shoot_cooldown:
                return None
            self.last_shot_time = now
            return {"type": "bullet", "rect": pygame.Rect(
                self.rect.right - 20, self.rect.centery - 3, 20, 6
            )}

# =========================================
# ----------- CONFIGURAÇÕES DE NAVES -------
# =========================================
ship2_cfg = {
    "img": ship2_img,
    "speed": 5,
    "bullet_color": YELLOW,
    "bullet_speed": 10,
    "size": (150, 105),
    "shoot_type": "laser",
    "shoot_cooldown": 2500
}

ship1_cfg = {
    "img": ship1_img,
    "speed": 9,
    "bullet_color": WHITE,
    "bullet_speed": 26,
    "size": (141, 90),
    "shoot_type": "bullet",
    "shoot_cooldown": 100
}

# =========================================
# ----------- VARIÁVEIS GLOBAIS ------------
# =========================================
MENU, CHARACTER_SELECT, GAME, PAUSE, LOSE = "menu", "character_select", "game", "pause", "lose"
game_state = MENU

ship = None
bullets = []
enemies = []
stars = []
spawn_timer = 0
score = 0
lives = 3  # quantidade inicial de vidas

# =========================================
# ----------- FUNÇÕES AUXILIARES -----------
# =========================================
def reset_stars():
    global stars
    stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT),
              speed := random.choice([1, 2, 3]), speed] for _ in range(120)]

def reset_game():
    global bullets, enemies, spawn_timer, ship, score, lives
    bullets.clear()
    enemies.clear()
    spawn_timer = 0
    ship = None
    score = 0
    lives = 3  # agora a variável global é atualizada
    reset_stars()

reset_stars()

# =========================================
# ----------- FUNÇÕES DE TELAS -------------
# =========================================
def draw_menu():
    screen.fill(BLACK)
    for star in stars:
        pygame.draw.circle(screen, WHITE, (star[0], star[1]), star[3])

    font_title = pygame.font.SysFont(None, 120, bold=True)
    font_btn = pygame.font.SysFont(None, 80)

    title = font_title.render("SPACE CLEANER", True, YELLOW)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))

    start_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2, 400, 80)
    quit_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 + 120, 400, 80)
    pygame.draw.rect(screen, LIGHT_BLUE, start_rect, border_radius=10)
    pygame.draw.rect(screen, RED, quit_rect, border_radius=10)

    start_txt = font_btn.render("1 - Jogar", True, BLACK)
    quit_txt = font_btn.render("2 - Sair", True, BLACK)
    screen.blit(start_txt, (start_rect.centerx - start_txt.get_width() // 2, start_rect.centery - start_txt.get_height() // 2))
    screen.blit(quit_txt, (quit_rect.centerx - quit_txt.get_width() // 2, quit_rect.centery - quit_txt.get_height() // 2))

def draw_character_select(selected_slot, slots):
    screen.fill(BLACK)
    font = pygame.font.SysFont(None, 80, bold=True)
    title = font.render("ESCOLHA SUA NAVE", True, YELLOW)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 180))

    for i, slot in enumerate(slots):
        rect, idx = slot["rect"], slot["index"]
        if idx == 1:
            preview = pygame.transform.scale(ship2_img, (130, 130))
            screen.blit(preview, (rect.x + 10, rect.y + 10))
        elif idx == 2:
            preview = pygame.transform.scale(ship1_img, (130, 130))
            screen.blit(preview, (rect.x + 10, rect.y + 10))
        else:
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, WHITE, rect, 2)
            lock_txt = pygame.font.SysFont(None, 40).render("???", True, WHITE)
            screen.blit(lock_txt, (rect.centerx - lock_txt.get_width() // 2, rect.centery - lock_txt.get_height() // 2))

        if i == selected_slot:
            pygame.draw.rect(screen, YELLOW, rect, 6)

    instr = pygame.font.SysFont(None, 50).render("Use as setas e Espaço para confirmar", True, WHITE)
    screen.blit(instr, (WIDTH // 2 - instr.get_width() // 2, HEIGHT - 100))

def draw_lose():
    screen.fill(BLACK)
    font_title = pygame.font.SysFont(None, 120, bold=True)
    font_btn = pygame.font.SysFont(None, 80)
    
    title = font_title.render("YOU LOSE!", True, RED)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
    
    retry_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2, 400, 80)
    menu_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 + 120, 400, 80)
    
    pygame.draw.rect(screen, LIGHT_BLUE, retry_rect, border_radius=10)
    pygame.draw.rect(screen, YELLOW, menu_rect, border_radius=10)
    
    retry_txt = font_btn.render("1 - Retry", True, BLACK)
    menu_txt = font_btn.render("2 - Menu", True, BLACK)
    
    screen.blit(retry_txt, (retry_rect.centerx - retry_txt.get_width() // 2, retry_rect.centery - retry_txt.get_height() // 2))
    screen.blit(menu_txt, (menu_rect.centerx - menu_txt.get_width() // 2, menu_rect.centery - menu_txt.get_height() // 2))

# =========================================
# ----------- FUNÇÃO DO JOGO ---------------
# =========================================
def draw_game():
    global bullets, enemies, spawn_timer, score, game_speed, lives, ship, game_state

    if ship is None:
        return

    ship.move(keys)

    # --- Disparo ---
    if ship.shoot_type == "laser":
        shot = ship.shoot()
        if shot:
            if len(bullets) == 0 or bullets[-1]["type"] != "laser":
                bullets.append(shot)
            else:
                bullets[-1] = shot
        else:
            bullets = [b for b in bullets if b["type"] != "laser"]

    for bullet in bullets[:]:
        if bullet["type"] == "bullet":
            bullet["rect"].x += ship.bullet_speed
            if bullet["rect"].x > WIDTH:
                bullets.remove(bullet)

    # --- Fundo estrelado ---
    for star in stars:
        star[0] -= star[2] * game_speed
        if star[0] < 0:
            star[0] = WIDTH
            star[1] = random.randint(0, HEIGHT)

    # --- Geração de inimigos (asteroides e lixo especial) ---
    spawn_timer += 1
    if spawn_timer > 60:
        spawn_timer = 0
        vertical_margin = HEIGHT // 6
        spawn_y = random.randint(vertical_margin, HEIGHT - vertical_margin)

        # 1 a cada 5 inimigos será um TrashBag (inimigo especial)
        if random.randint(1, 5) == 1:
            enemies.append({
                'x': WIDTH + 50,
                'y': spawn_y,
                'size': 65,
                'speed': 4 * game_speed,
                'img': trash_img,
                'type': 'trash',
                'angle': random.randint(0, 360),  # ângulo inicial aleatório
                'rotation_speed': random.uniform(2, 4)  # velocidade de rotação
            })
        else:
            asteroid_size = random.randint(60, 120)
            asteroid_img = random.choice(enemy_imgs)
            asteroid_img = pygame.transform.scale(asteroid_img, (asteroid_size, asteroid_size))

            # Adiciona uma rotação inicial aleatória ao asteroide
            angle = random.randint(0, 360)
            rotated_img = pygame.transform.rotate(asteroid_img, angle)

            enemies.append({
                'x': WIDTH + 50,
                'y': spawn_y,
                'size': asteroid_size,
                'speed': 3 * game_speed,
                'img': rotated_img,
                'type': 'asteroid',
                'angle': angle  # armazenamos caso queira usar no futuro
            })

    # --- Movimento dos inimigos ---
    for enemy in enemies[:]:
        enemy['x'] -= enemy['speed']

        # Se o inimigo sair da tela
        if enemy['x'] < -100:
            # Se for um lixo (TrashBag), o jogador perde 1 vida
            if enemy['type'] == 'trash':
                lives -= 1
                if lives <= 0:
                    game_state = LOSE
                    return
            enemies.remove(enemy)

    # --- Colisões com tiros ---
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            rect_enemy = pygame.Rect(enemy['x'], enemy['y'], enemy['size'], enemy['size'])
            hitbox_enemy = rect_enemy.inflate(-rect_enemy.width * 0.45, -rect_enemy.height * 0.45)
            if bullet["rect"].colliderect(hitbox_enemy):
                enemies.remove(enemy)
                if bullet["type"] == "bullet":
                    bullets.remove(bullet)
                score += 10
                break

    # --- Colisão da nave com inimigos ---
    ship_hitbox = ship.rect.inflate(-ship.rect.width * 0.28, -ship.rect.height * 0.28)
    for enemy in enemies[:]:
        rect_enemy = pygame.Rect(enemy['x'], enemy['y'], enemy['size'], enemy['size'])
        # Asteroides têm hitbox um pouco menor que o sprite
        if enemy['type'] == 'asteroid':
            hitbox_enemy = rect_enemy.inflate(-rect_enemy.width * 0.42, -rect_enemy.height * 0.42)
        else:
            hitbox_enemy = rect_enemy.inflate(-rect_enemy.width * 0.35, -rect_enemy.height * 0.35)

        if ship_hitbox.colliderect(hitbox_enemy):
            enemies.remove(enemy)
            lives -= 1
            if lives <= 0:
                game_state = LOSE
                return


    # --- Dificuldade progressiva ---
    new_speed_level = 1 + (score // difficulty_step) * 0.25
    if new_speed_level != game_speed:
        game_speed = new_speed_level
        if ship:
            ship.speed += 0.1

    # --- Desenho ---
    screen.fill(BLACK)
    for star in stars:
        pygame.draw.circle(screen, WHITE, (star[0], star[1]), star[3])
    screen.blit(ship.img, ship.rect)

    for bullet in bullets:
        if bullet["type"] == "laser":
            laser_surface = pygame.Surface((bullet["rect"].width, bullet["rect"].height), pygame.SRCALPHA)
            color_center = (180, 80, 255, 200)
            color_edge = (0, 255, 255, 100)
            for i in range(bullet["rect"].height):
                t = i / bullet["rect"].height
                r = int(color_center[0] * (1 - t) + color_edge[0] * t)
                g = int(color_center[1] * (1 - t) + color_edge[1] * t)
                b = int(color_center[2] * (1 - t) + color_edge[2] * t)
                a = int(color_center[3] * (1 - t) + color_edge[3] * t)
                pygame.draw.line(laser_surface, (r, g, b, a), (0, i), (bullet["rect"].width, i))
            screen.blit(laser_surface, bullet["rect"])
        else:
            pygame.draw.rect(screen, ship.bullet_color, bullet["rect"], border_radius=4)

    # --- Desenho dos inimigos ---
    for enemy in enemies:
        rect = pygame.Rect(enemy['x'], enemy['y'], enemy['size'], enemy['size'])
        img = enemy['img']

        # Lixos giram continuamente
        if enemy['type'] == 'trash':
            enemy['angle'] = (enemy['angle'] + enemy['rotation_speed']) % 360
            rotated_img = pygame.transform.rotate(img, enemy['angle'])
            rotated_rect = rotated_img.get_rect(center=rect.center)
            screen.blit(rotated_img, rotated_rect)
        else:
            rotated_rect = img.get_rect(center=rect.center)
            screen.blit(img, rotated_rect)

    score_text = pygame.font.SysFont(None, 60, bold=True).render(f"Pontos: {score}", True, YELLOW)
    lives_text = pygame.font.SysFont(None, 60, bold=True).render(f"Vidas: {lives}", True, RED)
    screen.blit(lives_text, (195, 180))
    screen.blit(score_text, (195, 115))

# =========================================
# ----------- TELA DE PAUSE ----------------
# =========================================
def draw_pause():
    screen.fill(BLACK)
    font = pygame.font.SysFont(None, 80)
    texts = [
        ("PAUSADO", WHITE, HEIGHT // 4),
        ("1 - Continuar", LIGHT_BLUE, HEIGHT // 2),
        ("2 - Voltar ao Menu", YELLOW, HEIGHT // 2 + 100),
        ("3 - Sair", RED, HEIGHT // 2 + 200)
    ]
    for txt, color, y in texts:
        render = font.render(txt, True, color)
        screen.blit(render, (WIDTH // 2 - render.get_width() // 2, y))

# =========================================
# ----------- PREPARO DOS SLOTS ------------
# =========================================
cols, rows = 3, 3
slot_size, spacing = 150, 25
total_width = cols * slot_size + (cols - 1) * spacing
total_height = rows * slot_size + (rows - 1) * spacing
start_x, start_y = WIDTH // 2 - total_width // 2, 350

slots = [{"rect": pygame.Rect(start_x + c * (slot_size + spacing),
                              start_y + r * (slot_size + spacing),
                              slot_size, slot_size),
          "index": i + 1}
         for i, (r, c) in enumerate([(r, c) for r in range(rows) for c in range(cols)])]

selected_slot = 0

# =========================================
# ----------- LOOP PRINCIPAL ---------------
# =========================================
while True:
    clock.tick(60)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game_state == MENU and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                game_state = CHARACTER_SELECT
            elif event.key == pygame.K_2:
                pygame.quit()
                sys.exit()

        elif game_state == CHARACTER_SELECT and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT and (selected_slot + 1) % cols != 0:
                selected_slot += 1
            elif event.key == pygame.K_LEFT and selected_slot % cols != 0:
                selected_slot -= 1
            elif event.key == pygame.K_DOWN and selected_slot + cols < len(slots):
                selected_slot += cols
            elif event.key == pygame.K_UP and selected_slot - cols >= 0:
                selected_slot -= cols
            elif event.key == pygame.K_SPACE:
                idx = slots[selected_slot]["index"]
                if idx == 1:
                    ship = Ship(**ship2_cfg)
                    game_state = GAME
                elif idx == 2:
                    ship = Ship(**ship1_cfg)
                    game_state = GAME

        elif game_state == GAME and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_state = PAUSE
            elif ship and ship.shoot_type == "laser" and event.key == pygame.K_SPACE:
                ship.trigger_laser()
            elif ship and ship.shoot_type == "bullet" and event.key == pygame.K_SPACE:
                shot = ship.shoot()
                if shot:
                    bullets.append(shot)

        elif game_state == PAUSE and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                game_state = GAME
            elif event.key == pygame.K_2:
                reset_game()
                game_state = MENU
            elif event.key == pygame.K_3:
                pygame.quit()
                sys.exit()

        elif game_state == LOSE and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                reset_game()
                # recria a nave selecionada
                if selected_slot == 0:
                    ship = Ship(**ship2_cfg)
                elif selected_slot == 1:
                    ship = Ship(**ship1_cfg)
                game_state = GAME
            elif event.key == pygame.K_2:
                reset_game()
                game_state = MENU

    if game_state == MENU:
        draw_menu()
    elif game_state == CHARACTER_SELECT:
        draw_character_select(selected_slot, slots)
    elif game_state == GAME:
        draw_game()  # draw_game() já se protege sozinho
    elif game_state == PAUSE:
        draw_pause()
    elif game_state == LOSE:
        draw_lose()

    pygame.display.flip()