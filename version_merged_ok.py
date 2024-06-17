import pgzrun
from random import randint, uniform
import math
from math import sin
 
WIDTH = 800
HEIGHT = 600
 
GROUND = 458
GRAVITY = 1000
GAME_SPEED = 300
JUMP_SPEED = 400
 
NUMBER_OF_BACKGROUND = 2
 
# Game states
TITLE = "title"
PLAYING = "playing"
PAUSED = "paused"
GAME_OVER = "game_over"
game_state = TITLE
 
# Hero initialisation
hero = Actor("hero", anchor=('middle', 'bottom'))
hero.pos = (64, GROUND)
hero_speed = 0
 
# Enemies initialisations
BOX_APPARITION = (2, 5)
VERTICAL_ENEMY_APPARITION = (3, 7)
next_box_time = randint(BOX_APPARITION[0], BOX_APPARITION[1])
next_vertical_enemy_time = randint(VERTICAL_ENEMY_APPARITION[0], VERTICAL_ENEMY_APPARITION[1])
boxes = []
vertical_enemy = None
 
# Background initialisation
backgrounds_bottom = []
backgrounds_top = []
 
for n in range(NUMBER_OF_BACKGROUND):
    bg_b = Actor("bg_1", anchor=('left', 'top'))
    bg_b.pos = n * WIDTH, 0
    backgrounds_bottom.append(bg_b)
 
    bg_t = Actor("bg_2", anchor=('left', 'top'))
    bg_t.pos = n * WIDTH, 0
    backgrounds_top.append(bg_t)
 
# Lives
lives = 3
invincibility_time = 0
 
def draw():
    screen.clear()
 
    for bg in backgrounds_bottom:
        bg.draw()
 
    for bg in backgrounds_top:
        bg.draw()
 
    for box in boxes:
        box.draw()
 
    if vertical_enemy:
        vertical_enemy.draw()
 
    hero.draw()
 
    if game_state == TITLE:
        screen.draw.text("Evasion Urbaine", center=(WIDTH // 2, HEIGHT // 2), fontsize=60, color="blue")
        screen.draw.text("Press Enter to Start", center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=30, color="white")
    elif game_state == GAME_OVER:
        screen.draw.text("Game Over", center=(WIDTH // 2, HEIGHT // 2), fontsize=60, color="red")
        screen.draw.text("Press Enter to Restart", center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=30, color="white")
    elif game_state == PAUSED:
        screen.draw.text("Paused", center=(WIDTH // 2, HEIGHT // 2), fontsize=60, color="yellow")
        screen.draw.text("Press P to Resume", center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=30, color="white")
    elif game_state == PLAYING:
        screen.draw.text(f"Lives: {lives}", topleft=(10, 10), fontsize=30, color="white")
 
def update(dt):
    global next_box_time, next_vertical_enemy_time, hero_speed, game_state, lives, vertical_enemy, invincibility_time
 
    if game_state in [TITLE, GAME_OVER, PAUSED]:
        return
 
    if invincibility_time > 0:
        invincibility_time -= dt
 
    # Enemies update
    next_box_time -= dt
    if next_box_time <= 0:
        box = Actor("box", anchor=('left', 'bottom'))
        box.pos = WIDTH, GROUND
        boxes.append(box)
        next_box_time = randint(BOX_APPARITION[0], BOX_APPARITION[1])
 
    for box in boxes:
        x, y = box.pos
        x -= GAME_SPEED * dt
        box.pos = x, y
        if box.colliderect(hero) and invincibility_time <= 0:
            lives -= 1
            invincibility_time = 2  # 2 seconds of invincibility
            if lives == 0:
                game_state = GAME_OVER
 
    if boxes and boxes[0].pos[0] <= -32:
        boxes.pop(0)
 
    if not vertical_enemy:
        vertical_enemy = Actor("box", anchor=('middle', 'center'))
        vertical_enemy.pos = (WIDTH, randint(100, 350))
        vertical_enemy.sinusoidal_angle = 0.5
        vertical_enemy.angular_speed = 3
 
    vertical_enemy.sinusoidal_angle += vertical_enemy.angular_speed * dt
    y = 330 + 100 * sin(vertical_enemy.sinusoidal_angle)
    vertical_enemy.pos = (vertical_enemy.pos[0] - GAME_SPEED * dt, y)
 
    if vertical_enemy.pos[0] <= -vertical_enemy.width:
        vertical_enemy.pos = (WIDTH, randint(100, 350))
 
    if vertical_enemy.colliderect(hero) and invincibility_time <= 0:
        lives -= 1
        invincibility_time = 2  # 2 seconds of invincibility
        if lives == 0:
            game_state = GAME_OVER
 
    # Hero update
    hero_speed -= GRAVITY * dt
    x, y = hero.pos
    y -= hero_speed * dt
 
    if y > GROUND:
        y = GROUND
        hero_speed = 0
 
    hero.pos = x, y
 
    # Background update
    for bg in backgrounds_bottom:
        x, y = bg.pos
        x -= GAME_SPEED * dt
        bg.pos = x, y
 
    if backgrounds_bottom[0].pos[0] <= -WIDTH:
        bg = backgrounds_bottom.pop(0)
        bg.pos = (NUMBER_OF_BACKGROUND - 1) * WIDTH, 0
        backgrounds_bottom.append(bg)
 
    for bg in backgrounds_top:
        x, y = bg.pos
        x -= GAME_SPEED / 3 * dt
        bg.pos = x, y
 
    if backgrounds_top[0].pos[0] <= -WIDTH:
        bg = backgrounds_top.pop(0)
        bg.pos = (NUMBER_OF_BACKGROUND - 1) * WIDTH, 0
        backgrounds_top.append(bg)
 
def on_key_down(key):
    global hero_speed, game_state, boxes, vertical_enemy, next_box_time, next_vertical_enemy_time, lives, invincibility_time
 
    if game_state == TITLE:
        if key == keys.RETURN:
            game_state = PLAYING
            lives = 3
    elif game_state == GAME_OVER:
        if key == keys.RETURN:
            game_state = PLAYING
            hero.pos = (64, GROUND)
            hero_speed = 0
            boxes = []
            vertical_enemy = None
            next_box_time = randint(BOX_APPARITION[0], BOX_APPARITION[1])
            next_vertical_enemy_time = randint(VERTICAL_ENEMY_APPARITION[0], VERTICAL_ENEMY_APPARITION[1])
            lives = 3
            invincibility_time = 0
    elif game_state == PLAYING:
        if key == keys.SPACE:
            if hero_speed <= 0:
                hero_speed = JUMP_SPEED
        elif key == keys.P:
            game_state = PAUSED
    elif game_state == PAUSED:
        if key == keys.P:
            game_state = PLAYING
 
pgzrun.go()