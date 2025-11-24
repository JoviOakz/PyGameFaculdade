import pygame
import sys
import random
import math
import os
from time import perf_counter

pygame.init()

# =============================================================================
# FUNÇÃO PARA CAMINHOS DE RECURSOS
# =============================================================================

def resource_path(relative_path):
    """Retorna o caminho absoluto dos recursos"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# =============================================================================
# CONFIGURAÇÕES GLOBAIS
# =============================================================================

# Dimensões da tela
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Parallax - Spaceship Arcade 2.5D')
clock = pygame.time.Clock()

# Parâmetros de gameplay
spawn_margin = 100
difficulty_step = 100
game_speed = 1

# Duração das transições (ms)
FADE_DURATION = 500

# Paleta de cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
YELLOW = (255, 255, 0)
GRAY = (50, 50, 50)
CYAN = (0, 255, 255)
PURPLE = (160, 80, 255)

# =============================================================================
# CARREGAMENTO DE ASSETS
# =============================================================================

def load_image(path, scale=None, alpha=True):
    """Carrega uma imagem com opções de escala e transparência"""
    img = pygame.image.load(path)
    img = img.convert_alpha() if alpha else img.convert()
    return pygame.transform.scale(img, scale) if scale else img

# Fundo do menu
try:
    menu_bg = load_image(resource_path("assets/Menu.png"), alpha=False)
except:
    menu_bg = pygame.Surface((WIDTH, HEIGHT))
    menu_bg.fill((10, 10, 30))

# Naves do jogador
ship1_img = load_image(resource_path("assets/Spaceship1.png"))
ship2_img = load_image(resource_path("assets/Spaceship2.png"))

# Inimigos
enemy_imgs = [load_image(resource_path(f"assets/Asteroid{i}.png"), (80, 80)) for i in range(1, 4)]
trash_img = load_image(resource_path("assets/TrashBag.png"), (45, 45))

# Ícones da HUD
life_icon = load_image(resource_path("assets/Life.png"), (50, 50))
score_icon = load_image(resource_path("assets/Trophy.png"), (50, 50))

# =============================================================================
# CLASSE DA NAVE DO JOGADOR
# =============================================================================

class Ship:
    """Representa a nave controlada pelo jogador"""
    
    def __init__(self, img, speed, bullet_color, bullet_speed, size, shoot_type, shoot_cooldown):
        self.img = pygame.transform.scale(img, size)
        self.rect = self.img.get_rect(center=(100, HEIGHT // 2))
        self.speed = speed
        self.bullet_color = bullet_color
        self.bullet_speed = bullet_speed
        self.shoot_type = shoot_type
        self.shoot_cooldown = shoot_cooldown
        self.last_shot_time = 0
        
        # Estado do laser (apenas para naves com laser)
        self.laser_active = False
        self.laser_start_time = 0

    def move(self, keys):
        """Move a nave baseado nas teclas pressionadas"""
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed

        # Limita movimento dentro da área de jogo
        margin = 185
        margin_y = int(self.rect.height * 0.98)
        play_area = pygame.Rect(
            margin, margin_y,
            WIDTH - 4 * margin,
            HEIGHT - 2 * margin_y
        )
        self.rect.clamp_ip(play_area)

    def trigger_laser(self):
        """Ativa o disparo do laser"""
        now = pygame.time.get_ticks()
        if not self.laser_active and now - self.last_shot_time > self.shoot_cooldown:
            self.laser_active = True
            self.laser_start_time = now
            self.last_shot_time = now

    def shoot(self):
        """Retorna um projétil (laser ou bullet) se possível disparar"""
        now = pygame.time.get_ticks()
        
        if self.shoot_type == "laser":
            if self.laser_active:
                # Verifica se o laser ainda está ativo
                if now - self.laser_start_time > 1125:
                    self.laser_active = False
                    return None
                return {
                    "type": "laser",
                    "rect": pygame.Rect(
                        self.rect.right - 10,
                        self.rect.top + 15,
                        WIDTH,
                        self.rect.height - 30
                    )
                }
            return None
            
        elif self.shoot_type == "bullet":
            # Verifica cooldown
            if now - self.last_shot_time < self.shoot_cooldown:
                return None
            self.last_shot_time = now
            return {
                "type": "bullet",
                "rect": pygame.Rect(
                    self.rect.right - 20,
                    self.rect.centery - 3,
                    20, 6
                )
            }

# =============================================================================
# CONFIGURAÇÕES DAS NAVES DISPONÍVEIS
# =============================================================================

ship1_cfg = {
    "img": ship1_img,
    "speed": 9,
    "bullet_color": WHITE,
    "bullet_speed": 26,
    "size": (141, 90),
    "shoot_type": "bullet",
    "shoot_cooldown": 100
}

ship2_cfg = {
    "img": ship2_img,
    "speed": 5,
    "bullet_color": YELLOW,
    "bullet_speed": 10,
    "size": (150, 105),
    "shoot_type": "laser",
    "shoot_cooldown": 2500
}

# =============================================================================
# ESTADOS DO JOGO E VARIÁVEIS GLOBAIS
# =============================================================================

# Estados possíveis
MENU, CHARACTER_SELECT, GAME, PAUSE, LOSE = "menu", "character_select", "game", "pause", "lose"
game_state = MENU

# Entidades do jogo
ship = None
bullets = []
enemies = []
stars = []

# Estatísticas
spawn_timer = 0
score = 0
lives = 3

# Seleções dos menus
selected_menu = 0
selected_pause = 0
selected_lose = 0
selected_slot = 0

# =============================================================================
# SISTEMA DE TRANSIÇÕES (FADE IN/OUT)
# =============================================================================

transition = {
    "active": False,
    "from": None,
    "to": None,
    "start_time": 0.0,
    "phase": "fade_out"
}

def request_state_change(new_state):
    """Inicia uma transição suave para um novo estado"""
    if transition["active"]:
        return
    
    transition.update({
        "active": True,
        "from": game_state,
        "to": new_state,
        "start_time": perf_counter(),
        "phase": "fade_out"
    })

def update_transition():
    """Atualiza o estado da transição e retorna o alpha do overlay"""
    if not transition["active"]:
        return None
    
    elapsed = (perf_counter() - transition["start_time"]) * 1000
    progress = min(elapsed / FADE_DURATION, 1.0)

    if transition["phase"] == "fade_out":
        alpha = int(255 * progress)
        if progress >= 1.0:
            # Troca o estado e inicia o fade in
            global game_state
            game_state = transition["to"]
            transition["phase"] = "fade_in"
            transition["start_time"] = perf_counter()
        return alpha
    else:  # fade_in
        alpha = int(255 * (1.0 - progress))
        if progress >= 1.0:
            # Finaliza a transição
            transition["active"] = False
            transition["from"] = None
            transition["to"] = None
        return alpha

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def reset_stars():
    """Gera estrelas para o fundo animado"""
    global stars
    stars = [
        [
            random.randint(0, WIDTH),
            random.randint(0, HEIGHT),
            speed := random.choice([1, 2, 3]),
            speed
        ]
        for _ in range(120)
    ]

def reset_game():
    """Reseta todas as variáveis do jogo"""
    global bullets, enemies, spawn_timer, ship, score, lives, game_speed
    bullets.clear()
    enemies.clear()
    spawn_timer = 0
    ship = None
    score = 0
    lives = 3
    game_speed = 1
    reset_stars()

def draw_text_center(text, font, color, y):
    """Desenha texto centralizado horizontalmente"""
    surf = font.render(text, True, color)
    screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))
    return surf

def create_neon_title(text, font_size=200):
    """Cria um título com efeito neon pulsante"""
    font_title = pygame.font.SysFont(None, font_size, bold=True)
    
    # Calcula brilho pulsante
    t = pygame.time.get_ticks() * 0.004
    glow = 180 + 75 * math.sin(t)
    glow_color = (255, glow, 50)
    
    # Renderiza texto principal
    title_surf = font_title.render(text, True, glow_color)
    
    # Cria contorno neon com múltiplas camadas
    outline_surf = pygame.Surface(
        (title_surf.get_width() + 30, title_surf.get_height() + 30),
        pygame.SRCALPHA
    )
    
    for offset in range(1, 8):
        o_color = (255, glow * 0.7, 50, 25)
        outline = font_title.render(text, True, o_color)
        outline_surf.blit(outline, (offset + 10, offset + 10))
    
    outline_surf.blit(title_surf, (15, 15))
    return outline_surf

def draw_menu_options(options, selected, base_y=None, gap=100):
    """Desenha opções de menu com cursor animado"""
    font_opt = pygame.font.SysFont(None, 90)
    
    if base_y is None:
        total_height = (len(options) - 1) * gap
        base_y = HEIGHT // 2 - total_height // 2
    
    # Animação de pulso do cursor
    pulse = 255 * (0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.006))
    pulse_color = (pulse, pulse, pulse)
    
    for i, text in enumerate(options):
        label = font_opt.render(text, True, WHITE)
        cursor = font_opt.render(">", True, pulse_color if i == selected else BLACK)
        
        total_width = cursor.get_width() + 25 + label.get_width()
        x_start = WIDTH // 2 - total_width // 2
        y = base_y + i * gap
        
        screen.blit(cursor, (x_start, y))
        screen.blit(label, (x_start + cursor.get_width() + 25, y))

# =============================================================================
# FUNÇÕES DE RENDERIZAÇÃO DAS TELAS
# =============================================================================

def draw_menu(selected_option):
    """Renderiza a tela do menu principal"""
    screen.blit(menu_bg, (0, 0))
    
    # Título com efeito neon
    title = create_neon_title("START")
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 200))
    
    # Opções do menu
    draw_menu_options(["Iniciar", "Sair"], selected_option)

def draw_pause(selected_option):
    """Renderiza a tela de pausa"""
    screen.blit(menu_bg, (0, 0))
    
    # Título
    title = create_neon_title("PAUSE", 180)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 200))
    
    # Opções
    draw_menu_options(["Continuar", "Voltar ao Menu", "Sair"], selected_option)

def draw_lose(selected_option):
    """Renderiza a tela de game over"""
    screen.blit(menu_bg, (0, 0))
    
    # Título
    title = create_neon_title("GAME OVER")
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 200))
    
    # Opções
    draw_menu_options(["Jogar Novamente", "Voltar ao Menu", "Sair"], selected_option)

def draw_character_select(selected_slot, slots, t):
    """Renderiza a tela de seleção de personagem"""
    screen.blit(menu_bg, (0, 0))
    
    # Banner do título
    font_title = pygame.font.SysFont(None, 95, bold=True)
    text_surf = font_title.render("ESCOLHA SUA NAVE", True, (255, 230, 0))
    text_rect = text_surf.get_rect(center=(WIDTH // 2, 200))
    
    # Fundo da faixa
    padding_x, padding_y = 40, 25
    banner_rect = pygame.Rect(
        text_rect.x - padding_x,
        text_rect.y - padding_y,
        text_rect.width + padding_x * 2,
        text_rect.height + padding_y * 2
    )
    
    pygame.draw.rect(screen, (20, 20, 20), banner_rect, border_radius=20)
    pygame.draw.rect(screen, (255, 230, 0), banner_rect, 4, border_radius=20)
    
    # Brilho interno
    glow_rect = banner_rect.inflate(15, 15)
    pygame.draw.rect(screen, (255, 255, 120, 60), glow_rect, 6, border_radius=28)
    
    screen.blit(text_surf, text_rect)
    
    # Desenha os slots de seleção
    for i, slot in enumerate(slots):
        rect, idx = slot["rect"], slot["index"]
        
        if idx in (1, 2):
            # Slot desbloqueado
            preview_img = ship2_img if idx == 1 else ship1_img
            preview = pygame.transform.scale(preview_img, (130, 130))
            screen.blit(preview, (rect.x + 10, rect.y + 10))
            pygame.draw.rect(screen, WHITE, rect, 3)
        else:
            # Slot bloqueado
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, WHITE, rect, 2)
            lock_txt = pygame.font.SysFont(None, 40).render("???", True, WHITE)
            screen.blit(lock_txt, (
                rect.centerx - lock_txt.get_width() // 2,
                rect.centery - lock_txt.get_height() // 2
            ))
        
        # Destacar slot selecionado
        if i == selected_slot:
            pygame.draw.rect(screen, YELLOW, rect, 6)
    
    # Instruções
    instr = pygame.font.SysFont(None, 50).render(
        "Use as setas e Espaço para confirmar", True, WHITE
    )
    screen.blit(instr, (WIDTH // 2 - instr.get_width() // 2, HEIGHT - 100))

def draw_hud():
    """Desenha a interface de pontuação e vidas"""
    font = pygame.font.SysFont(None, 60)
    
    # Pontuação
    score_text = font.render(f"{score}", True, YELLOW)
    screen.blit(score_icon, (190, 110))
    screen.blit(score_text, (250, 119))
    
    # Vidas
    lives_text = font.render(f"{lives}", True, RED)
    screen.blit(life_icon, (191, 171))
    screen.blit(lives_text, (250, 180))

# =============================================================================
# LÓGICA PRINCIPAL DO JOGO
# =============================================================================

def spawn_enemy():
    """Gera um novo inimigo (asteroide ou lixo espacial)"""
    vertical_margin = HEIGHT // 6
    spawn_y = random.randint(vertical_margin, HEIGHT - vertical_margin)
    
    # 20% de chance de spawnar um TrashBag
    if random.randint(1, 5) == 1:
        return {
            'x': WIDTH + 50,
            'y': spawn_y,
            'size': 65,
            'speed': 4 * game_speed,
            'img': trash_img,
            'type': 'trash',
            'angle': random.randint(0, 360),
            'rotation_speed': random.uniform(2, 4)
        }
    else:
        # Asteroide comum
        asteroid_size = random.randint(60, 120)
        asteroid_img = random.choice(enemy_imgs)
        asteroid_img = pygame.transform.scale(asteroid_img, (asteroid_size, asteroid_size))
        angle = random.randint(0, 360)
        rotated_img = pygame.transform.rotate(asteroid_img, angle)
        
        return {
            'x': WIDTH + 50,
            'y': spawn_y,
            'size': asteroid_size,
            'speed': 3 * game_speed,
            'img': rotated_img,
            'type': 'asteroid',
            'angle': angle
        }

def draw_laser(bullet):
    """Desenha o efeito visual do laser"""
    laser_surface = pygame.Surface(
        (bullet["rect"].width, bullet["rect"].height),
        pygame.SRCALPHA
    )
    
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

def draw_game(keys):
    """Atualiza e renderiza o loop principal do jogo"""
    global bullets, enemies, spawn_timer, score, game_speed, lives, ship
    
    if ship is None:
        return
    
    # Movimento da nave
    ship.move(keys)
    
    # Sistema de disparo
    if ship.shoot_type == "laser":
        shot = ship.shoot()
        if shot:
            # Mantém apenas um laser ativo
            bullets = [b for b in bullets if b["type"] != "laser"]
            bullets.append(shot)
        else:
            bullets = [b for b in bullets if b["type"] != "laser"]
    
    # Atualiza posição dos projéteis
    for bullet in bullets[:]:
        if bullet["type"] == "bullet":
            bullet["rect"].x += ship.bullet_speed
            if bullet["rect"].x > WIDTH:
                bullets.remove(bullet)
    
    # Anima fundo estrelado
    for star in stars:
        star[0] -= star[2] * game_speed
        if star[0] < 0:
            star[0] = WIDTH
            star[1] = random.randint(0, HEIGHT)
    
    # Sistema de spawn de inimigos
    spawn_timer += 1
    if spawn_timer > 60:
        spawn_timer = 0
        enemies.append(spawn_enemy())
    
    # Movimento dos inimigos
    for enemy in enemies[:]:
        enemy['x'] -= enemy['speed']
        
        # Remove inimigos fora da tela
        if enemy['x'] < -100:
            if enemy['type'] == 'trash':
                # Penalidade por deixar lixo escapar
                lives -= 1
                if lives <= 0:
                    request_state_change(LOSE)
                    return
            enemies.remove(enemy)
    
    # Detecção de colisão: projéteis vs inimigos
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            rect_enemy = pygame.Rect(enemy['x'], enemy['y'], enemy['size'], enemy['size'])
            hitbox_enemy = rect_enemy.inflate(
                -rect_enemy.width * 0.45,
                -rect_enemy.height * 0.45
            )
            
            if bullet["rect"].colliderect(hitbox_enemy):
                enemies.remove(enemy)
                if bullet["type"] == "bullet":
                    bullets.remove(bullet)
                score += 10
                break
    
    # Detecção de colisão: nave vs inimigos
    ship_hitbox = ship.rect.inflate(-ship.rect.width * 0.28, -ship.rect.height * 0.28)
    
    for enemy in enemies[:]:
        rect_enemy = pygame.Rect(enemy['x'], enemy['y'], enemy['size'], enemy['size'])
        
        # Ajusta hitbox baseado no tipo de inimigo
        inflation = -0.42 if enemy['type'] == 'asteroid' else -0.35
        hitbox_enemy = rect_enemy.inflate(
            rect_enemy.width * inflation,
            rect_enemy.height * inflation
        )
        
        if ship_hitbox.colliderect(hitbox_enemy):
            enemies.remove(enemy)
            lives -= 1
            if lives <= 0:
                request_state_change(LOSE)
                return
    
    # Sistema de dificuldade progressiva
    new_speed_level = 1 + (score // difficulty_step) * 0.25
    if new_speed_level != game_speed:
        game_speed = new_speed_level
        ship.speed += 0.1
    
    # === RENDERIZAÇÃO ===
    screen.fill(BLACK)
    
    # Fundo estrelado
    for star in stars:
        pygame.draw.circle(screen, WHITE, (star[0], star[1]), star[3])
    
    # Nave do jogador
    screen.blit(ship.img, ship.rect)
    
    # Projéteis
    for bullet in bullets:
        if bullet["type"] == "laser":
            draw_laser(bullet)
        else:
            pygame.draw.rect(screen, ship.bullet_color, bullet["rect"], border_radius=4)
    
    # Inimigos
    for enemy in enemies:
        rect = pygame.Rect(enemy['x'], enemy['y'], enemy['size'], enemy['size'])
        img = enemy['img']
        
        if enemy['type'] == 'trash':
            # Rotação contínua do lixo espacial
            enemy['angle'] = (enemy['angle'] + enemy['rotation_speed']) % 360
            rotated_img = pygame.transform.rotate(img, enemy['angle'])
            rotated_rect = rotated_img.get_rect(center=rect.center)
            screen.blit(rotated_img, rotated_rect)
        else:
            rotated_rect = img.get_rect(center=rect.center)
            screen.blit(img, rotated_rect)
    
    # HUD
    draw_hud()

# =============================================================================
# PREPARAÇÃO DOS SLOTS DE SELEÇÃO
# =============================================================================

cols, rows = 3, 3
slot_size, spacing = 150, 25
total_width = cols * slot_size + (cols - 1) * spacing
total_height = rows * slot_size + (rows - 1) * spacing
start_x = WIDTH // 2 - total_width // 2
start_y = 350

slots = [
    {
        "rect": pygame.Rect(
            start_x + c * (slot_size + spacing),
            start_y + r * (slot_size + spacing),
            slot_size,
            slot_size
        ),
        "index": i + 1
    }
    for i, (r, c) in enumerate([(r, c) for r in range(rows) for c in range(cols)])
]

# =============================================================================
# LOOP PRINCIPAL
# =============================================================================

reset_stars()

while True:
    dt = clock.tick(60)
    t = perf_counter()
    keys = pygame.key.get_pressed()
    
    # Processa eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # Bloqueia inputs durante transições
        if event.type == pygame.KEYDOWN:
            if transition["active"] and transition["phase"] == "fade_out":
                continue
            
            # === MENU PRINCIPAL ===
            if game_state == MENU:
                if event.key == pygame.K_UP:
                    selected_menu = (selected_menu - 1) % 2
                elif event.key == pygame.K_DOWN:
                    selected_menu = (selected_menu + 1) % 2
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if selected_menu == 0:
                        request_state_change(CHARACTER_SELECT)
                    else:
                        pygame.quit()
                        sys.exit()
            
            # === SELEÇÃO DE PERSONAGEM ===
            elif game_state == CHARACTER_SELECT:
                if event.key == pygame.K_RIGHT and (selected_slot + 1) % cols != 0:
                    selected_slot += 1
                elif event.key == pygame.K_LEFT and selected_slot % cols != 0:
                    selected_slot -= 1
                elif event.key == pygame.K_DOWN and selected_slot + cols < len(slots):
                    selected_slot += cols
                elif event.key == pygame.K_UP and selected_slot - cols >= 0:
                    selected_slot -= cols
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    idx = slots[selected_slot]["index"]
                    if idx == 1:
                        ship = Ship(**ship2_cfg)
                        request_state_change(GAME)
                    elif idx == 2:
                        ship = Ship(**ship1_cfg)
                        request_state_change(GAME)
            
            # === JOGO ===
            elif game_state == GAME:
                if event.key == pygame.K_ESCAPE:
                    request_state_change(PAUSE)
                elif ship and ship.shoot_type == "laser" and event.key == pygame.K_SPACE:
                    ship.trigger_laser()
                elif ship and ship.shoot_type == "bullet" and event.key == pygame.K_SPACE:
                    shot = ship.shoot()
                    if shot:
                        bullets.append(shot)
            
            # === PAUSA ===
            elif game_state == PAUSE:
                if event.key == pygame.K_UP:
                    selected_pause = (selected_pause - 1) % 3
                elif event.key == pygame.K_DOWN:
                    selected_pause = (selected_pause + 1) % 3
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if selected_pause == 0:
                        request_state_change(GAME)
                    elif selected_pause == 1:
                        reset_game()
                        request_state_change(MENU)
                    elif selected_pause == 2:
                        pygame.quit()
                        sys.exit()
            
            # === GAME OVER ===
            elif game_state == LOSE:
                if event.key == pygame.K_UP:
                    selected_lose = (selected_lose - 1) % 3
                elif event.key == pygame.K_DOWN:
                    selected_lose = (selected_lose + 1) % 3
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if selected_lose == 0:
                        reset_game()
                        request_state_change(CHARACTER_SELECT)
                    elif selected_lose == 1:
                        reset_game()
                        request_state_change(MENU)
                    elif selected_lose == 2:
                        pygame.quit()
                        sys.exit()
    
    # Renderiza o estado atual
    if game_state == MENU:
        draw_menu(selected_menu)
    elif game_state == CHARACTER_SELECT:
        draw_character_select(selected_slot, slots, t)
    elif game_state == GAME:
        draw_game(keys)
    elif game_state == PAUSE:
        draw_pause(selected_pause)
    elif game_state == LOSE:
        draw_lose(selected_lose)
    
    # Aplica overlay de transição
    alpha = update_transition()
    if alpha is not None:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(alpha)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
    
    pygame.display.flip()