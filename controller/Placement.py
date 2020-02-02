# Schiffe platzieren/Spiel starten

import pygame as pg
import model.Ship as Ship
from model.Grid import Grid
import view.Board as Board
#import controller.StartGame as StartGame
from controller.Game import start_game


def place_ships(placement):
    pg.display.set_mode(Board.size)
    pg.display.update()
    Board.disable_startbutton()
    clock = pg.time.Clock()

    while placement:
        clock.tick(80)
        # --- globale Variablen  ---
        pg.init()
        # Schiffinstanzen in Listen holen
        placed_sprites = Ship.get_placed_sprites()
        ship_sprites = Ship.get_ships()
        left_mouse_down = False
        # Grid für eigene Schiffe erzeugen
        own_grid = Board.get_own_grid()
        game_running = False

        selected = None

        clock = pg.time.Clock()
        is_running = True

        while is_running:

            # --- Events ---

            for event in pg.event.get():

                if event.type == pg.QUIT:
                    is_running = False
                    exit()

                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        is_running = False
                        exit()
                        #Spiel erstellen, wenn alle Schiffe platziert sind und Button gedrückt wurde
                if event.type == pg.USEREVENT:
                    if event.user_type == 'ui_button_pressed':
                        if event.ui_element == Board.startbutton:
                            is_running = False
                            placement = False
                            start_game()
                            # Bei Linksklick auf Schiffobjekt - Schiff an Mauszeiger hängen
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        left_mouse_down = True
                        for ship_sprite in ship_sprites:
                            if ship_sprite.get_rect().collidepoint(event.pos):
                                event.pos = ship_sprite.get_front()
                                selected = ship_sprite.get_id()
                                # Schiff im Grid & rechte Maustaste gedrückt - Schiff rotieren
                    if event.button == 3:
                        if left_mouse_down:
                            for ship_sprite in ship_sprites:
                                if ship_sprite.get_id() == selected:
                                    ship_sprite.rotate()
                                    event.pos = ship_sprite.get_front()
                # Wenn die rechte Maustaste im Grid losgelassen wird, Schiff platzieren
                # wenn es innerhalb des Grids liegt und mit keinem bereits platzierten kollidiert
                # Schiff in die "platziert"-Liste übernehmen
                # Wenn die rechte Maustaste außerhalb des Grids losgelassen wird, Schiff auf Ausgangsposition zurück
                # Schiff aus der "platziert"-Liste entfernen
                elif event.type == pg.MOUSEBUTTONUP:
                    if event.button == 1:
                        left_mouse_down = False
                        for ship_sprite in ship_sprites:
                            if ship_sprite.get_id() == selected:
                                if Grid.in_grid(own_grid, ship_sprite) and Ship.free_space(ship_sprite):
                                    ship_sprite.set_grid_pos(own_grid)
                                    placed_sprites.add(ship_sprite)
                                else:
                                    ship_sprite.ship_back()
                                    placed_sprites.remove(ship_sprite)
                                    Board.disable_startbutton()
                            if len(placed_sprites.sprites()) == len(ship_sprites.sprites()):
                                Board.enable_startbutton()
                        selected = None
                # Mausbewegung mit angehängtem Schiff - Schiff "draggen"
                elif event.type == pg.MOUSEMOTION:
                    if selected is not None:
                        x = event.pos[0]
                        y = event.pos[1]
                        # Objekt verschieben
                        for ship_sprite in ship_sprites:
                            if ship_sprite.get_id() == selected:
                                ship_sprite.rect.center = (x, y)
                                event.pos = ship_sprite.get_front()

            Board.manager.process_events(event)


            # --- FPS ---
            time_delta = clock.tick(60) / 1000.0
            Board.manager.update(time_delta)

            # --- Board mit neuer Schiffsposition aktualisieren ---
            Board.draw_board(game_running)

