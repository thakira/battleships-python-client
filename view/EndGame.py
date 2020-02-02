# Spielende-Bildschirm


from pygame.locals import *
import pygame_gui as gui
from controller.RestClient import *


def end_game(message):
    # aktualisierte Statistiken vom Server abrufen
    get_statistics()
    # Spiel auf dem Server beenden
    if not get_stop():
        get_stop()

    # Fenstergröße
    size_end = (730, 250)
    splash = pg.display.set_mode(size_end)
    manager = gui.UIManager(size_end, '../docs/gui_theme.json')
    pg.display.set_caption('Schiffe versenken')
    bg_start = pg.image.load('../images/shipblue.jpg')
    bg_start = pg.transform.scale(bg_start, size_end)
    font_endgame = pg.font.Font(None, 30)
    font_title = pg.font.Font(None, 40)
    text_title = font_title.render(message, True, Color(228, 235, 243))
    # Statistiken anzeigen
    text_statistics = font_endgame.render('Spiele: ' + str(player.games) + ', davon gewonnen: '
                                          + str(player.wins) + ', davon verloren: ' + str(player.games - player.wins),
                                          True, Color(228, 235, 243))
    # Spiel-Beenden Button
    quit_button = gui.elements.UIButton(relative_rect=pg.Rect((215, 110), (300, 80)),
                                            text='Spiel beenden', manager=manager)
    clock = pg.time.Clock()
    end_menu = True

    # Schleife zur Eingabe der Nutzerdaten starten
    while end_menu:
        time_delta = clock.tick(60)/1000.0
        # Events abfragen
        for event in pg.event.get():
            # Wenn Fenster geschlossen wird
            if event.type == QUIT:
                end_menu = False
                get_stop()
                exit()
            # Wenn Esc gedrückt wird
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    get_stop()
                    end_menu = False
                    exit()
            elif event.type == pg.USEREVENT:
                if event.user_type == 'ui_button_pressed':
                    if event.ui_element == quit_button:
                        end_menu = False
                        exit()
            manager.process_events(event)
        # Bildschirm aufbauen und aktualisieren
        manager.update(time_delta)
        splash.blit(bg_start,(0,0))
        splash.blit(text_title, (int(115), 40))
        splash.blit(text_statistics, (20, 220))
        manager.draw_ui(splash)
        pg.display.update()


