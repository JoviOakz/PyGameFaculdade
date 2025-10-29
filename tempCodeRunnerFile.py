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
            enemies.append({
                'x': WIDTH + 50,
                'y': spawn_y,
                'size': 80,
                'speed': 3 * game_speed,
                'img': random.choice(enemy_imgs),
                'type': 'asteroid'
            })