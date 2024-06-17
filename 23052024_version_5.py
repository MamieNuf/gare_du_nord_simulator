import pgzrun
import pygame
import os
from random import randint
from math import sin
from tkinter import ANCHOR


# Constantes de jeu
WIDTH = 800
HEIGHT = 600
GROUND = 458
GRAVITY = 1300
GAME_SPEED = 300
JUMP_SPEED = 700
NUMBER_OF_BACKGROUND = 2

# États du jeu
TITLE = "Gare du Nord Simulator"
PLAYING = "playing"
PAUSED = "paused"
GAME_OVER = "game_over"

# Intervalles d'apparitions des ennemis
BOX_APPARITION = (2, 5)  # poubelles
VERTICAL_ENEMY_APPARITION = (7, 10)  # pigeons
HORIZONTAL_ENEMY_APPARITION = (7, 10)  # rats en voiture
FLYING_ENEMY_APPARITION = (7, 10)  # rats en fusée

# Variables de jeu
game_state = TITLE

hero_speed = 0

next_box_time = randint(BOX_APPARITION[0],BOX_APPARITION[1])
next_vertical_enemy_time = randint(VERTICAL_ENEMY_APPARITION[0],VERTICAL_ENEMY_APPARITION[1])
next_horizontal_enemy_time = randint(HORIZONTAL_ENEMY_APPARITION[0],HORIZONTAL_ENEMY_APPARITION[1])
next_flying_enemy_time = randint(FLYING_ENEMY_APPARITION[0],FLYING_ENEMY_APPARITION[1])

boxes = []
vertical_enemies = []
horizontal_enemies = []
flying_enemies = []

lives = 3
invincibility_time = 0
can_jump = True
score = 0
selected_hero = "thomas"  # choix du perso, thomas de base

# Pour le clignotement après s'être fait hit:
hero_visible = True
invincibility_blink_time = 0
cover_image = Actor("cover", anchor=('left', 'top'))
credits_image = Actor("credits", anchor=('left','top'))

# =================================================================================================================================================
# Initialisations héros + backgrounds

hero = Actor(selected_hero, anchor=('middle', 'bottom'))
hero.pos = (64, GROUND)

backgrounds_bottom = []
backgrounds_top = []

# Initialiser les arrière-plans dans une boucle
for n in range(NUMBER_OF_BACKGROUND):
    bg_1 = Actor("bg_1", anchor=('left', 'top'))
    bg_1.pos = n * WIDTH, 0
    backgrounds_bottom.append(bg_1)

    bg_2 = Actor("bg_2", anchor=('left', 'top'))
    bg_2.pos = n * WIDTH, 0
    backgrounds_top.append(bg_2)

    trees = Actor("trees", anchor=('left', 'top'))
    trees.pos = n * WIDTH, 0
    backgrounds_top.append(trees)
    extra_cars = Actor("extra_cars", anchor=('left', 'top'))
    extra_cars.pos = n * WIDTH, 0
    backgrounds_top.append(extra_cars)    
    cars = Actor("cars", anchor=('left', 'top'))
    cars.pos = n * WIDTH, 0
    backgrounds_top.append(cars)

# =================================================================================================================================================

def draw():
    screen.clear()

    # Dessiner les arrière-plans
    for bg in backgrounds_top:
        bg.draw()
    for bg in backgrounds_bottom:
        bg.draw()


    for box in boxes:
        box.draw()
    for enemy in vertical_enemies:
        enemy.draw()
    for enemy in horizontal_enemies:
        enemy.draw()
    for enemy in flying_enemies:
        enemy.draw()
    if hero_visible or invincibility_time <= 0:
        hero.draw()

    if game_state == TITLE:
        cover_image.draw()
    elif game_state == GAME_OVER:
        credits_image.draw()
        screen.draw.text(f"Score: {int(score)}", center=(WIDTH // 2, HEIGHT // 2 + 275), fontsize=30, color="red")
    elif game_state == PAUSED:
        screen.draw.text("En pause", center=(WIDTH // 2, HEIGHT // 2 - 50), fontsize=60, color="yellow")
        screen.draw.text("Appuyez sur P pour reprendre", center=(WIDTH // 2, HEIGHT // 2), fontsize=30, color="white")
    elif game_state == PLAYING:
        screen.draw.text(f"Vies: {lives}", topleft=(10, 10), fontsize=30, color="black")
        screen.draw.text(f"Score: {int(score)}", topright=(WIDTH - 10, 10), fontsize=30, color="black")
        screen.draw.text("Appuyez sur P pour mettre en pause", bottomright=(WIDTH - 10, HEIGHT - 10), fontsize=20, color="black")

# =================================================================================================================================================

def update(dt):
    global next_box_time, next_vertical_enemy_time, next_horizontal_enemy_time, next_flying_enemy_time, hero_speed, game_state, lives, invincibility_time, can_jump, score, hero_visible, invincibility_blink_time

    if game_state in [TITLE, GAME_OVER, PAUSED]:
        return

    hero.image = selected_hero

    # Invincibilité et clignotement après hit
    if invincibility_time > 0:
        invincibility_time -= dt
        invincibility_blink_time -= dt
        if invincibility_blink_time <= 0:
            hero_visible = not hero_visible
            invincibility_blink_time = 0.2
    else:
        hero_visible = True

    # Calculer le nombre total d'ennemis
    total_enemies = len(boxes) + len(vertical_enemies) + len(horizontal_enemies) + len(flying_enemies)

    # POUBELLES =====================================================================================
    next_box_time -= dt
    if next_box_time <= 0 and total_enemies < 2:
        boxes.append(Actor("box", anchor=('left', 'bottom'), pos=(WIDTH, GROUND)))
        next_box_time = randint(BOX_APPARITION[0], BOX_APPARITION[1])

    for box in boxes[:]:
        box.pos = (box.pos[0] - GAME_SPEED * dt, box.pos[1])
        if box.colliderect(hero) and invincibility_time <= 0:
            lives -= 1
            invincibility_time = 2  
            if lives == 0:
                game_state = GAME_OVER
        if box.pos[0] <= -32:
            boxes.remove(box)
            score += 1  

    # PIGEONS ================================================================================================
    next_vertical_enemy_time -= dt
    if next_vertical_enemy_time <= 0 and total_enemies < 2:
        vertical_enemy = Actor("pigeons2", anchor=('middle', 'center'), pos=(WIDTH, randint(100, 350)))
        vertical_enemy.sinusoidal_angle = 0.5
        vertical_enemy.angular_speed = 3
        vertical_enemies.append(vertical_enemy)
        next_vertical_enemy_time = randint(VERTICAL_ENEMY_APPARITION[0], VERTICAL_ENEMY_APPARITION[1])

    for enemy in vertical_enemies[:]:
        enemy.sinusoidal_angle += enemy.angular_speed * dt
        y = 330 + 100 * sin(enemy.sinusoidal_angle)
        enemy.pos = (enemy.pos[0] - GAME_SPEED * dt, y)

        if enemy.pos[0] <= -enemy.width:
            vertical_enemies.remove(enemy)
            score += 1  

        if enemy.colliderect(hero) and invincibility_time <= 0:
            lives -= 1
            invincibility_time = 2  
            if lives == 0:
                game_state = GAME_OVER

    # MISE À JOUR DES ENNEMIS HORIZONTAUX ================================================================================================
    next_horizontal_enemy_time -= dt
    if next_horizontal_enemy_time <= 0 and total_enemies < 2:
        horizontal_enemies.append(Actor("rat", anchor=('left', 'bottom'), pos=(WIDTH, GROUND)))
        next_horizontal_enemy_time = randint(HORIZONTAL_ENEMY_APPARITION[0], HORIZONTAL_ENEMY_APPARITION[1])

    for enemy in horizontal_enemies[:]:
        enemy.pos = (enemy.pos[0] - GAME_SPEED * 1.5 * dt, enemy.pos[1]) 
        if enemy.colliderect(hero) and invincibility_time <= 0:
            lives -= 1
            invincibility_time = 2  
            if lives == 0:
                game_state = GAME_OVER
        if enemy.pos[0] <= -32:
            horizontal_enemies.remove(enemy)
            score += 1  

    # MISE À JOUR DES ENNEMIS VOLANTS ================================================================================================
    next_flying_enemy_time -= dt
    if next_flying_enemy_time <= 0 and total_enemies < 2:
        flying_enemy = Actor("rocketrat", anchor=('left', 'center'), pos=(WIDTH, randint(150, 450))) 
        flying_enemies.append(flying_enemy)
        next_flying_enemy_time = randint(FLYING_ENEMY_APPARITION[0], FLYING_ENEMY_APPARITION[1])

    for enemy in flying_enemies[:]:
        enemy.pos = (enemy.pos[0] - GAME_SPEED * 1.5 * dt, enemy.pos[1])  
        if enemy.colliderect(hero) and invincibility_time <= 0:
            lives -= 1
            invincibility_time = 2 
            if lives == 0:
                game_state = GAME_OVER
        if enemy.pos[0] <= -32:
            flying_enemies.remove(enemy)
            score += 1

    # Mise à jour du héros
    hero_speed -= GRAVITY * dt
    x, y = hero.pos
    y -= hero_speed * dt

    if y > GROUND:
        y = GROUND
        hero_speed = 0
        can_jump = True

    hero.pos = x, y

    # Mise à jour des arrière-plans
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

# =================================================================================================================================================

def on_key_down(key):
    global hero_speed, game_state, boxes, vertical_enemies, horizontal_enemies, flying_enemies, next_box_time, next_vertical_enemy_time, next_horizontal_enemy_time, next_flying_enemy_time, lives, invincibility_time, can_jump, score, selected_hero, hero

    if game_state == TITLE:
        if key == keys.RETURN:
            reset_game()
            game_state = PLAYING
        elif key == keys.T:
            selected_hero = "thomas"
            reset_game()
        elif key == keys.B:
            selected_hero = "bastien"
            reset_game()
    elif game_state == GAME_OVER:
        if key == keys.RETURN:
            reset_game()
            game_state = PLAYING
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
    global hero_speed, boxes, vertical_enemies, horizontal_enemies, flying_enemies, next_box_time, next_vertical_enemy_time, next_horizontal_enemy_time, next_flying_enemy_time, lives, invincibility_time, game_state, can_jump, score, selected_hero, hero
    hero = Actor(selected_hero, anchor=('middle', 'bottom'))
    hero.pos = (64, GROUND)
    hero_speed = 0
    boxes = []
    vertical_enemies = []
    horizontal_enemies = []
    flying_enemies = []
    next_box_time = randint(*BOX_APPARITION)
    next_vertical_enemy_time = randint(*VERTICAL_ENEMY_APPARITION)
    next_horizontal_enemy_time = randint(*HORIZONTAL_ENEMY_APPARITION)
    next_flying_enemy_time = randint(*FLYING_ENEMY_APPARITION)
    lives = 3
    invincibility_time = 0
    can_jump = True
    score = 0

os.environ['SDL_VIDEO_CENTERED'] = '1'
pgzrun.go()
