import pgzrun
from random import randint
from math import sin

# Constantes de jeu
WIDTH = 800
HEIGHT = 600
GROUND = 458
GRAVITY = 1000
GAME_SPEED = 300
JUMP_SPEED = 400
NUMBER_OF_BACKGROUND = 2

# États du jeu
TITLE = "title"
PLAYING = "playing"
PAUSED = "paused"
GAME_OVER = "game_over"

# Intervalle de temps pour apparition des ennemis
BOX_APPARITION = (2, 5)
VERTICAL_ENEMY_APPARITION = (3, 7)

# Variables de jeu
game_state = TITLE
hero_speed = 0
next_box_time = randint(*BOX_APPARITION)
next_vertical_enemy_time = randint(*VERTICAL_ENEMY_APPARITION)
boxes = []
vertical_enemy = None
lives = 3
invincibility_time = 0
can_jump = True
score = 0
hero_visible = True
invincibility_blink_time = 0  # Timer pour gérer la fréquence de clignotement

# Variable pour stocker le choix du héros
selected_hero = "hero"

# Initialisation du héros (sera réinitialisé lors de la sélection)
hero = Actor(selected_hero, anchor=('middle', 'bottom'))
hero.pos = (64, GROUND)

# Initialisation des fonds
backgrounds_bottom = [Actor("bg_1", anchor=('left', 'top'), pos=(n * WIDTH, 0)) for n in range(NUMBER_OF_BACKGROUND)]
backgrounds_top = [Actor("bg_2", anchor=('left', 'top'), pos=(n * WIDTH, 0)) for n in range(NUMBER_OF_BACKGROUND)]

def draw():
    screen.clear()
    for bg in backgrounds_bottom + backgrounds_top:
        bg.draw()
    for box in boxes:
        box.draw()
    if vertical_enemy:
        vertical_enemy.draw()
    if hero_visible or invincibility_time <= 0:
        hero.draw()
    
    if game_state == TITLE:
        draw_text_center("Evasion Urbaine", 60, "blue", -100)
        draw_text_center("Press A for Hero1, Press B for Hero2", 30, "white", -50)
        draw_text_center("Press Enter to Start", 30, "white")
    elif game_state == GAME_OVER:
        draw_text_center("Game Over", 60, "red", -50)
        draw_text_center(f"Score: {int(score)}", 30, "white", 0)
        draw_text_center("Press Enter to Restart", 30, "white", 50)
    elif game_state == PAUSED:
        draw_text_center("Paused", 60, "yellow", -50)
        draw_text_center("Press P to Resume", 30, "white")
    elif game_state == PLAYING:
        screen.draw.text(f"Lives: {lives}", topleft=(10, 10), fontsize=30, color="white")
        screen.draw.text(f"Score: {int(score)}", topright=(WIDTH - 10, 10), fontsize=30, color="white")

def draw_text_center(text, size, color, offset_y=0):
    screen.draw.text(text, center=(WIDTH // 2, HEIGHT // 2 + offset_y), fontsize=size, color=color)

def update(dt):
    global next_box_time, next_vertical_enemy_time, hero_speed, game_state, lives, vertical_enemy, invincibility_time, can_jump, score, hero_visible, invincibility_blink_time

    if game_state in [TITLE, GAME_OVER, PAUSED]:
        return
    
    hero.image = selected_hero  # Assurez-vous que la sprite est mise à jour

    if invincibility_time > 0:
        invincibility_time -= dt
        invincibility_blink_time -= dt
        if invincibility_blink_time <= 0:
            hero_visible = not hero_visible  # Alterne la visibilité du héros
            invincibility_blink_time = 0.2  # Réinitialise le timer de clignotement
    else:
        hero_visible = True

    update_enemies(dt)
    update_hero(dt)
    update_backgrounds(dt)

def update_enemies(dt):
    global next_box_time, vertical_enemy, lives, invincibility_time, game_state, score

    next_box_time -= dt
    if next_box_time <= 0:
        boxes.append(Actor("box", anchor=('left', 'bottom'), pos=(WIDTH, GROUND)))
        next_box_time = randint(*BOX_APPARITION)
    
    for box in boxes[:]:
        box.pos = (box.pos[0] - GAME_SPEED * dt, box.pos[1])
        if box.colliderect(hero) and invincibility_time <= 0:
            lives -= 1
            invincibility_time = 2  # 2 secondes d'invincibilité
            if lives == 0:
                game_state = GAME_OVER
        if box.pos[0] <= -32:
            boxes.remove(box)
            score += 1  # Augmente le score pour chaque boîte évitée
    
    if not vertical_enemy:
        vertical_enemy = Actor("box", anchor=('middle', 'center'), pos=(WIDTH, randint(100, 350)))
        vertical_enemy.sinusoidal_angle = 0.5
        vertical_enemy.angular_speed = 3

    vertical_enemy.sinusoidal_angle += vertical_enemy.angular_speed * dt
    y = 330 + 100 * sin(vertical_enemy.sinusoidal_angle)
    vertical_enemy.pos = (vertical_enemy.pos[0] - GAME_SPEED * dt, y)

    if vertical_enemy.pos[0] <= -vertical_enemy.width:
        vertical_enemy.pos = (WIDTH, randint(100, 350))
        score += 1  # Augmente le score pour chaque ennemi vertical évité

    if vertical_enemy.colliderect(hero) and invincibility_time <= 0:
        lives -= 1
        invincibility_time = 2  # 2 secondes d'invincibilité
        if lives == 0:
            game_state = GAME_OVER

def update_hero(dt):
    global hero_speed, can_jump
    hero_speed -= GRAVITY * dt
    x, y = hero.pos
    y -= hero_speed * dt

    if y > GROUND:
        y = GROUND
        hero_speed = 0
        can_jump = True

    hero.pos = x, y

def update_backgrounds(dt):
    for bg in backgrounds_bottom:
        bg.pos = (bg.pos[0] - GAME_SPEED * dt, bg.pos[1])
    if backgrounds_bottom[0].pos[0] <= -WIDTH:
        bg = backgrounds_bottom.pop(0)
        bg.pos = (NUMBER_OF_BACKGROUND - 1) * WIDTH, 0
        backgrounds_bottom.append(bg)

    for bg in backgrounds_top:
        bg.pos = (bg.pos[0] - GAME_SPEED / 3 * dt, bg.pos[1])
    if backgrounds_top[0].pos[0] <= -WIDTH:
        bg = backgrounds_top.pop(0)
        bg.pos = (NUMBER_OF_BACKGROUND - 1) * WIDTH, 0
        backgrounds_top.append(bg)

def on_key_down(key):
    global hero_speed, game_state, boxes, vertical_enemy, next_box_time, next_vertical_enemy_time, lives, invincibility_time, can_jump, score, selected_hero, hero

    if game_state == TITLE:
        if key == keys.RETURN:
            reset_game()
            game_state = PLAYING
        elif key == keys.A:
            selected_hero = "hero"
            reset_game()
        elif key == keys.B:
            selected_hero = "hero2"
            reset_game()
    elif game_state == GAME_OVER:
        if key == keys.RETURN:
            reset_game()
    elif game_state == PLAYING:
        if key == keys.SPACE and can_jump:
            hero_speed = JUMP_SPEED
            can_jump = False
        elif key == keys.P:
            game_state = PAUSED
    elif game_state == PAUSED:
        if key == keys.P:
            game_state = PLAYING

def reset_game():
    global hero_speed, boxes, vertical_enemy, next_box_time, next_vertical_enemy_time, lives, invincibility_time, game_state, can_jump, score, selected_hero, hero
    hero = Actor(selected_hero, anchor=('middle', 'bottom'))
    hero.pos = (64, GROUND)
    hero_speed = 0
    boxes = []
    vertical_enemy = None
    next_box_time = randint(*BOX_APPARITION)
    next_vertical_enemy_time = randint(*VERTICAL_ENEMY_APPARITION)
    lives = 3
    invincibility_time = 0
    can_jump = True
    score = 0

pgzrun.go()
