# Startmenu

# Bibliotheken pygame, Oberflächenelemente & Konstanten für Pygame importieren
import pygame as pg
from pygame.locals import *
import pygame_gui as gui
import controller.Login as Login


# erster Startbildschirm (Wahl Anmelden/Registrieren)
def splash_start():
    pg.init()
    size = (730, 250)
    splash = pg.display.set_mode(size)
    manager = gui.UIManager(size, '../docs/gui_theme.json')
    pg.display.set_caption('Schiffe versenken')
    bg_start = pg.image.load('../images/shipblue.jpg')
    bg_start = pg.transform.scale(bg_start, size)
    font_title = pg.font.Font(None, 80)
    text_title = font_title.render('Schiffe versenken', True, Color(228, 235, 243))
    login_button = gui.elements.UIButton(relative_rect=pg.Rect((150, 120), (200, 80)),
                                         text='Anmelden', tool_tip_text="Du hast bereits Logindaten?", manager=manager)
    register_button = gui.elements.UIButton(relative_rect=pg.Rect((380, 120), (200, 80)),
                                            text='Registrieren', tool_tip_text="Neu hier? - Jetzt Benutzer erstellen", manager=manager)
    login_button_klein = None
    register_button_klein = None
    clock = pg.time.Clock()
    startmenu = True

    # Schleife zur Eingabe der Nutzerdaten starten
    while startmenu:
        time_delta = clock.tick(60)/1000.0

        # Events abfragen
        for event in pg.event.get():
            # Wenn Fenster geschlossen wird
            if event.type == QUIT:
                startmenu = False
                exit()
            # Wenn Esc gedrückt wird
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    startmenu = False
                    exit()
            if event.type == pg.USEREVENT:
                if event.user_type == 'ui_button_pressed':
                    # Wenn Anmelden-Button auf dem Auswahlbildschirm gedrückt
                    if event.ui_element == login_button:
                        login_button.kill()
                        register_button.kill()
                        # Anmelde-Dialog anzeigen
                        login_button_klein = gui.elements.UIButton(relative_rect=pg.Rect((270,180), (200, 60)),
                                                                   text='Anmelden', manager=manager)
                        gui.elements.ui_label.UILabel(relative_rect=pg.Rect((150, 85), (110,21)),
                                                                       text='Benutzername', manager=manager)
                        gui.elements.ui_label.UILabel(relative_rect=pg.Rect((150, 125), (70, 21)),
                                                                       text='Passwort', manager=manager)
                        username_input = gui.elements.ui_text_entry_line.UITextEntryLine(relative_rect=
                                                                                         pg.Rect((150, 100), (400, 20)),
                                                                                         manager=manager)
                        password_input = gui.elements.ui_text_entry_line.UITextEntryLine(relative_rect=
                                                                                         pg.Rect((150, 140), (400, 20)),
                                                                                         manager=manager)
                        # Eingaben Textfelder abfragen
                        username_input.process_event(event)
                        password_input.process_event(event)
                    if event.ui_element == login_button_klein:
                        # Wenn Anmelden-Button gedrückt -> eingegebene Informationen in Variable übernehmen,
                        # weiter mit Login
                        login_data = {'username': str(username_input.get_text()),
                                      'password':  str(password_input.get_text())}
                        startmenu = False
                        Login.login(login_data)
                        # Wenn Registrieren-Button auf dem Auswahlbildschirm gedrückt
                    if event.ui_element == register_button:
                        register_button.set_relative_position((270,180))
                        register_button.set_dimensions((200, 60))
                        login_button.kill()
                        register_button.kill()
                        # Registrieren - Dialog anzeigen
                        register_button_klein = gui.elements.UIButton(relative_rect=pg.Rect((270,180), (200, 60)),
                                                                      text='Registrieren', manager=manager)
                        gui.elements.ui_label.UILabel(relative_rect=pg.Rect((160, 85), (110,21)),
                                                                       text='Benutzername', manager=manager)
                        gui.elements.ui_label.UILabel(relative_rect=pg.Rect((160, 125), (80, 21)),
                                                                       text='Passwort', manager=manager)
                        username_input = \
                            gui.elements.ui_text_entry_line.UITextEntryLine(relative_rect=
                                                                            pg.Rect((160, 100), (400, 24)),
                                                                            manager=manager)
                        password_input = gui.elements.ui_text_entry_line.UITextEntryLine(relative_rect=
                                                                                         pg.Rect((160, 140), (400, 24)),
                                                                                         manager=manager)
                        # Eingaben Textfelder abfragen
                        username_input.process_event(event)
                        password_input.process_event(event)
                        # Wenn Registrieren-Button gedrückt -> eingegebene Informationen in Variable übernehmen,
                        # weiter mit Registrieren
                    if event.ui_element == register_button_klein:
                        login_data = {'username' : str(username_input.get_text()),
                                      'password' : str(password_input.get_text())}
                        startmenu = False
                        Login.register(login_data)
            manager.process_events(event)

        # Bildschirm aufbauen und aktualisieren
        manager.update(time_delta)
        splash.blit(bg_start,(0,0))
        splash.blit(text_title, (120, 20))
        manager.draw_ui(splash)
        pg.display.update()

# startmenu = Startklasse
if __name__ == "__main__":
    splash_start()
