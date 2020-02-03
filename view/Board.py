# Spielbrett

# importieren der notwendigen Bibliotheken und Spielklassen
import pygame as pg
import os
from model.Grid import Grid
import model.Ship as Ship
from pygame.locals import *
import pygame_gui as gui
import controller.Game as Game
from controller.RestClient import player
from controller.RestClient import actual_game
from controller.RestClient import get_background


os.environ['SDL_VIDEO_CENTERED'] = '1'

# PyGame initialisieren
pg.init()
print(player.token)
#Spielbrettgröße = 3/4 des Bildschirms
SCALE = 0.75

info = pg.display.Info()
screen_width,screen_height = info.current_w,info.current_h
window_width,window_height = int(screen_width * SCALE), int(screen_height * SCALE)
size = (window_width,window_height)
screen = pg.display.set_mode(size)
manager = gui.UIManager(size, '../docs/gui_theme.json')
# Spielbrett-Hintergrund per REST vom Server holen
get_background()
background_image = '../images/bg-battle.jpg'
pg.display.update()


# Schrift definieren
def create_font(t,s=150,c=(255,255,255), b=True,i=False):
    font = pg.font.SysFont("Arial", int(s * SCALE), bold=b, italic=i)
    text = font.render(t, True, c)
    text_rect = text.get_rect()
    return [text,text_rect]

# Grids erstellen
grid_size = int(size[0] * 0.3)
ownGrid_pos_x = int(size[0]/3.5)
ownGrid_pos_y = int(size[1]/3)
enemyGrid_pos_x = int(size[0]/3.5 + grid_size + 50)
enemyGrid_pos_y = int(size[1]/3)
ownGrid = Grid(grid_size, ownGrid_pos_x, ownGrid_pos_y)
enemyGrid = Grid(grid_size, enemyGrid_pos_x, enemyGrid_pos_y)


#Spielbrettinhalte initialisieren
pg.display.set_caption("Schiffe versenken")
bg_start = pg.image.load(background_image)
bg_start = pg.transform.scale(bg_start, size)
text_title, title_box = create_font('Schiffe versenken')
title_box.center = int((screen.get_width() - text_title.get_width())//2), screen.get_height()//20
font_text = pg.font.Font(None, int(round(35*SCALE)))
text_header, header_box = create_font('Schiffe platzieren: ', 30)
header_box.center = int(grid_size - text_header.get_width())//2, grid_size
text_rules1 = font_text.render('- Schiffe mit der linken Maustaste auf das Grid ziehen', True, Color(255,255,255))
text_rules2 = font_text.render('- Schiffe mit der rechten Maustaste drehen', True, Color(255,255,255))
text_rules3 = font_text.render('- Schiffe durch Loslassen der linken Maustaste platzieren', True, Color(255,255,255))

bg_ships = pg.Surface((grid_size * 0.75, grid_size))
bg_ships.set_alpha(180)
bg_ships.fill((155, 181, 196))
bg_rules = pg.Surface((grid_size+60, grid_size-100))
bg_rules.set_alpha(180)
bg_rules.fill((155, 181, 196))
startbutton = gui.elements.UIButton(relative_rect=pg.Rect((enemyGrid_pos_x + 100, size[1]-200), (250, 100)),
                                    text='Gegner suchen', tool_tip_text="Platzierung abgeschlossen?", manager=manager)
startbutton.disable()
Ship.create_ships(size, int(grid_size / 10))

status = ""

placed_sprites = Ship.get_placed_sprites()
ship_sprites = Ship.get_ships()

fire = pg.image.load('../images/fire2.png')
fire = pg.transform.scale(fire, (ownGrid.cell_size, ownGrid.cell_size))
bombe = pg.image.load('../images/bombe.png')
bombe = pg.transform.scale(bombe, (enemyGrid.cell_size, enemyGrid.cell_size))
miss = pg.image.load('../images/water.png')
miss = pg.transform.scale(miss, (ownGrid.cell_size, int(ownGrid.cell_size)))


# Spielbrett zeichnen (game_running == False: Spielbrett Schiffspositionierung,  == True: Spielbrett mit 2 Grids
def draw_board(game_running):
    screen.fill((255,255,255))
    screen.blit(bg_start, (0, 0))
    screen.blit(text_title, title_box.center)
    text_player, player_box = create_font('Spieler: ' + player.username, 25)
    text_statistics, stat_box = create_font('gespielte Spiele: ' + player.games.__str__()
                                          + ', gewonnene Spiele: ' + player.wins.__str__() + ', verlorene Spiele: '
                                            + (str(player.games - player.wins)), 40)
    stat_box.center = int((screen.get_width() - text_statistics.get_width())//2), int(screen.get_height() - screen.get_height()//10)
    screen.blit(text_statistics, stat_box.center)
    screen.blit(text_player, (ownGrid_pos_x + 0.35 * grid_size, ownGrid_pos_y - 30))
    screen.blit(Grid.get_grid_surface(ownGrid), [ownGrid_pos_x, ownGrid_pos_y])

    if game_running:
        ownGrid.grid_pos_x = int(size[0]/30)
        screen.blit(text_player, (ownGrid_pos_x + 0.35 * grid_size, ownGrid_pos_y - 30))
        screen.blit(Grid.get_grid_surface(ownGrid), [ownGrid_pos_x, ownGrid_pos_y])
        font_status = pg.font.Font(None, int(150 * SCALE))
        status_text = font_status.render(actual_game.status, True, Color(255, 0, 0))
        status_box = status_text.get_rect()
        status_box.center = int((screen.get_width() - status_text.get_width()) // 2), 160
        screen.blit(status_text, status_box.center)
        text_enemy = font_text.render('Gegner: ' + actual_game.enemy_name, True, Color(255, 255, 255))
        screen.blit(text_enemy, (enemyGrid_pos_x + 0.35 * grid_size, enemyGrid_pos_y - 30))
        screen.blit(Grid.get_grid_surface(enemyGrid), [enemyGrid_pos_x, enemyGrid_pos_y])
        placed_sprites.draw(screen)
        for enemy in Game.sunken_enemies:
            screen.blit(enemy[0], enemy[1])
        for shot in Game.my_shots:
            screen.blit(bombe, shot)
        for my_hit in Game.my_hits:
            screen.blit(fire, my_hit)
        for my_miss in Game.my_misses:
            screen.blit(miss, my_miss)
        for enemy_hit in Game.enemy_hits:
            screen.blit(fire, enemy_hit)
        for enemy_miss in Game.enemy_misses:
            screen.blit(miss, enemy_miss)

    elif not game_running:
        screen.blit(bg_rules, (enemyGrid_pos_x, enemyGrid_pos_y))
        screen.blit(bg_ships, (int(size[0]/30), int(size[1] / 3)))
        screen.blit(text_header, (enemyGrid_pos_x + 10, int(size[1] / 3) + 10))
        screen.blit(text_rules1, (enemyGrid_pos_x + 10, enemyGrid_pos_y + 50))
        screen.blit(text_rules2, (enemyGrid_pos_x + 10, enemyGrid_pos_y + 65))
        screen.blit(text_rules3, (enemyGrid_pos_x + 10, enemyGrid_pos_y + 80))
        ship_sprites.draw(screen)
        placed_sprites.draw(screen)
        manager.draw_ui(screen)

    # Spielbrett anzeigen
    pg.display.flip()


# SpielerGrid zurückgeben
def get_own_grid():
    return ownGrid


# Position auf dem Spielerbrett zurückgeben
def get_grid_pos():
    return ownGrid_pos_x, ownGrid_pos_y


# Spiel starten Button aktivieren
def enable_startbutton():
    startbutton.enable()


# Spiel starten Button deaktivieren
def disable_startbutton():
    startbutton.disable()

