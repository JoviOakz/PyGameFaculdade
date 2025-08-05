import pygame
import sys

# Inicializa o Pygame
pygame.init()

# Tamanho da tela
LARGURA = 800
ALTURA = 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Movimento com Teclado")

# Cores
ROXO = (120, 0, 177)
MARROM = (128, 70, 20)

# Configurações do personagem
x = 100
y = 100
velocidade = 2.5

# Forma atual (pode ser: "quadrado", "circulo", "triangulo")
forma = "quadrado"

# Relógio para controle de FPS
clock = pygame.time.Clock()

# Loop principal
while True:
    # Limita FPS
    clock.tick(60)

    # Verifica eventos (ex: fechar janela)
    for evento in pygame.event.get():
        # Trocar forma com as teclas 1, 2, 3
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_1:
                forma = "quadrado"
            elif evento.key == pygame.K_2:
                forma = "circulo"
            elif evento.key == pygame.K_3:
                forma = "triangulo"

        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Verifica teclas pressionadas
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
        x -= velocidade
    if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
        x += velocidade
    if teclas[pygame.K_UP] or teclas[pygame.K_w]:
        y -= velocidade
    if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
        y += velocidade

    # Preenche o fundo
    tela.fill(ROXO)

    # Desenha o personagem conforme a forma atual
    if forma == "quadrado":
        pygame.draw.rect(tela, MARROM, (x, y, 50, 50))
    elif forma == "circulo":
        pygame.draw.circle(tela, MARROM, (x + 25, y + 25), 25)
    elif forma == "triangulo":
        pontos = [(x + 25, y), (x, y + 50), (x + 50, y + 50)]
        pygame.draw.polygon(tela, MARROM, pontos)

    # Atualiza a tela
    pygame.display.flip()