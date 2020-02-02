# Spielablauf

# externe Bibliotheken und benötigte eigene Klassen importieren
from model.Grid import Grid
import view.Board as Board
from controller.RestClient import *
from model.Events import *
from view.EndGame import end_game

#Logdatei erstellen
log = open("../docs/log.txt", "w")

# globale Variablen
placed_sprites = Ship.get_placed_sprites()

clock = pg.time.Clock()
my_hits = []
my_shots = []
my_misses = []
enemy_hits = []
enemy_misses = []
sunken_enemies = []


# Falls eigenes Schiff gesunken
def own_sunk():
    # Alle eigenen Schiffe durchgehen, um herauszufinden, welches versenkt wurde
    ships = Ship.get_ships()
    actual_ship = actual_game.sunk['ship_type']
    for ship in ships:
        if int(ship.column) == int(actual_game.sunk['col']) and int(ship.row) == actual_game.sunk['row']:
            # Schiffsgröße ermitteln und das jeweils dazugehörige "versunken"-Image passend skalieren
            # und im Objekt hinterlegen
            if actual_ship == 2:
                if actual_game.sunk['horizontal']:
                    image = pg.image.load("../images/Zweier_sunk.png")
                    image = pg.transform.scale(image,
                                               ((Board.ownGrid.cell_size * actual_ship), Board.ownGrid.cell_size))
                else:
                    image = pg.image.load("../images/Zweier_sunk_vertical.png")
                    image = pg.transform.scale(image,
                                               (Board.ownGrid.cell_size, Board.ownGrid.cell_size * actual_ship))
            elif actual_ship == 3:
                if actual_game.sunk['horizontal']:
                    image = pg.image.load("../images/Dreier_sunk.png")
                    image = pg.transform.scale(image,
                                               ((Board.ownGrid.cell_size * actual_ship), Board.ownGrid.cell_size))
                else:
                    image = pg.image.load("../images/Dreier_sunk_vertical.png")
                    image = pg.transform.scale(image,
                                               (Board.ownGrid.cell_size, Board.ownGrid.cell_size * actual_ship))
            elif actual_ship == 4:
                if actual_game.sunk['horizontal']:
                    image = pg.image.load("../images/Vierer_sunk.png")
                    image = pg.transform.scale(image,
                                               ((Board.ownGrid.cell_size * actual_ship), Board.ownGrid.cell_size))
                else:
                    image = pg.image.load("../images/Vierer_sunk_vertical.png")
                    image = pg.transform.scale(image,
                                               (Board.ownGrid.cell_size, Board.ownGrid.cell_size * actual_ship))
            elif actual_ship == 5:
                if actual_game.sunk['horizontal']:
                    image = pg.image.load("../images/Fuenfer_sunk.png")
                    image = pg.transform.scale(image,
                                               ((Board.ownGrid.cell_size * actual_ship), Board.ownGrid.cell_size))
                else:
                    image = pg.image.load("../images/Fuenfer_sunk_vertical.png")
                    image = pg.transform.scale(image,
                                               (Board.ownGrid.cell_size, Board.ownGrid.cell_size * actual_ship))
            ship.image = image
    return


# falls gegnerisches Schiff versenkt
def enemy_sunk():
    pos = Grid.get_hit_coords(Board.enemyGrid,actual_game.sunk['col'], actual_game.sunk['row'])
    ship_type = actual_game.sunk['ship_type']
    # Je nach Schiffstyp passendes Bild zuordnen und skalieren und an Board zur Anzeige übergeben
    if ship_type == 2:
        if actual_game.sunk['horizontal']:
            image = "../images/Zweier_sunk.png"
        else:
            image = "../images/Zweier_sunk_vertical.png"
    if ship_type == 3:
        if actual_game.sunk['horizontal']:
            image = "../images/Dreier_sunk.png"
        else:
            image = "../images/Dreier_sunk_vertical.png"
    if ship_type == 4:
        if actual_game.sunk['horizontal']:
            image = "../images/Vierer_sunk.png"
        else:
            image = "../images/Vierer_sunk_vertical.png"
    if ship_type == 5:
        if actual_game.sunk['horizontal']:
            image = "../images/Fuenfer_sunk.png"
        else:
            image = "../images/Fuenfer_sunk_vertical.png"

    image = pg.image.load(image)

    if actual_game.sunk['horizontal']:
        image = pg.transform.scale(image, (Board.enemyGrid.cell_size * ship_type, Board.enemyGrid.cell_size))
    else:
        image = pg.transform.scale(image, (Board.enemyGrid.cell_size, Board.enemyGrid.cell_size * ship_type))
    sunken_enemies.append((image, pos))
    return


# Spielstart-schleife
def start_game():
    pg.event.clear()
    clock.tick(300)
    start_thread(games_new)
    queue = True
    while queue:
        Board.draw_board(True)
        # Abbruchbedingungen für das Spiel (Esc-Taste, X gedrückt)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                queue = False
                end_game("Spiel abgebrochen")

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    queue = False
                    end_game("Spiel abgebrochen")

            # Falls ein Request nicht die erwartete Response bekommt, wird er erneut ausgeführt
            if event.type == MyEvents.EVENT_REQUEST_ERROR:
                log.write(event.message + "\n")
            # Falls der Server nicht erreichbar ist
            if event.type == MyEvents.EVENT_SERVER_ERROR:
                log.write(event.message + "\n")
                # In die Warteschlange auf der Server eingereiht
            if event.type == MyEvents.EVENT_GAME_QUEUED:
                log.write(event.message + "\n")
                actual_game.status = "Suche Gegner..."
                continue
                # Gegner wurde gefunden und ein neues Spiel gestartet
            if event.type == MyEvents.EVENT_GAME_FOUND:
                log.write(event.message + "\n")
                actual_game.status = ("Spiel startet, Dein Gegner ist " + str(actual_game.enemy_name))
                start_thread(post_ships)
                # Die Schiffspositionen wurden an den Server versandt, der Gegner hat seine jedoch noch nicht geschickt
            if event.type == MyEvents.EVENT_SHIPS_POSTED:
                log.write(event.message + "\n")
                event_enemy_turn = pg.event.Event(MyEvents.EVENT_ENEMY_TURN, {"message": "Gegner ist dran"})
                pg.event.post(event_enemy_turn)
                actual_game.status = (str(actual_game.enemy_name) + " ist dran!")
                queue = False
                play(True)
                # Die Schiffe wurden an den Server gesandt und da die Schiffe des Gegners bereits da sind, kann das
                # Spiel starten
            if event.type == MyEvents.EVENT_GAME_STARTS:
                log.write(event.message + "\n")
                event_own_turn = pg.event.Event(MyEvents.EVENT_OWN_TURN, {"message": "Du bist dran"})
                pg.event.post(event_own_turn)
                actual_game.status = "Du bist dran!"
                queue = False
                play(True)

# Steuerungsschleife für den Spielablauf
def play(game_running):
    # FPS festlegen
    clock.tick(60)
    while game_running:
        Board.draw_board(True)
        # EventListe abfragen
        for event in pg.event.get():
            # Falls das Spielfenster geschlossen wurde
            if event.type == pg.QUIT:
                game_running = False
                end_game("Spiel abgebrochen")
            # Falls ESC gedrückt wurde
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    game_running = False
                    end_game("Spiel abgebrochen")

            # dieser Spieler ist am Zug
            if event.type == MyEvents.EVENT_OWN_TURN:
                log.write(event.message + "\n")
                actual_game.status = "Du bist dran!"
                actual_game.active_player = actual_game.next_player
            # Wenn die Maustaste gedrückt wurde und die Maus sich im gegnerischen Grid befandt, Zug auswerten
            if event.type == pg.MOUSEBUTTONDOWN:
                if actual_game.active_player == int(player.user_id):
                    if Grid.mouse_in_grid(Board.enemyGrid, pg.mouse.get_pos()):
                        coords = (Board.enemyGrid.get_grid_coords(pg.mouse.get_pos()))
                        shot = (coords[0])
                        start_thread_args(send_turn, shot)

            # Der Gegner ist am Zug
            if event.type == MyEvents.EVENT_ENEMY_TURN:
                log.write(event.message + "\n")
                actual_game.status = (str(actual_game.enemy_name) + " ist dran!")
                start_thread(get_turn)

            # Warten auf den Zug des Gegners (Antwort des Servers)
            if event.type == MyEvents.EVENT_WAIT_4_TURN:
                log.write(event.message + "\n")
                actual_game.status = "Warte auf Gegner..."
                continue

            # gegenerischer Zug wurde vom Server gesandt
            if event.type == MyEvents.EVENT_TURN_ARRIVED:
                log.write(event.message + "\n")
                column = actual_game.col
                row = actual_game.row
                # Reihe/Spalte Angabe aus gegnerischem Schuß in Bildschirmkoordinaten umrechnen
                shot = Grid.get_hit_coords(Board.ownGrid, column, row)
                # Treffer auf dem Bildschirm eigenen Grid anzeigen
                if actual_game.result == "HIT":
                    enemy_hits.append(shot)
                    # Wenn Schiff versunken, Schiffsbild ersetzen gegen "versunkenes Schiff"
                    if actual_game.sunk:
                        own_sunk()
                # Nicht getroffenen Schuß im eigenen Grid einblenden
                elif actual_game.result == "WATER":
                    enemy_misses.append(shot)
                if actual_game.end:
                    end_game("Spiel beendet! " + actual_game.enemy_name + " hat gewonnen!")
                if actual_game.next_player == int(player.user_id):
                    event_own_turn= pg.event.Event(MyEvents.EVENT_OWN_TURN, {"message": "Du bist dran"})
                    pg.event.post(event_own_turn)
                elif actual_game.next_player == int(actual_game.enemy_id):
                    event_enemy_turn = pg.event.Event(MyEvents.EVENT_ENEMY_TURN, {"message": "Gegner ist dran"})
                    pg.event.post(event_enemy_turn)

            # Auswertung des Servers des eigenen Zuges
            if event.type == MyEvents.EVENT_TURN_POSTED:
                log.write(event.message + "\n")
                coords = Board.enemyGrid.get_hit_coords(actual_game.col, actual_game.row)
                if actual_game.result == "HIT":
                    my_hits.append(coords)
                    # wenn versunken, Methode zur Einblendung des Schiffbildes aufrufen
                    if actual_game.sunk:
                        enemy_sunk()
                    # Wenn nicht getroffen, Wasser auf gegnerischem Grid einblenden
                elif actual_game.result == "WATER":
                    my_misses.append(coords)
                if actual_game.end:
                    end_game("Spiel beendet! Du hast gewonnen!")
                if actual_game.next_player == int(player.user_id):
                    event_own_turn = pg.event.Event(MyEvents.EVENT_OWN_TURN, {"message": "Du bist dran!"})
                    pg.event.post(event_own_turn)
                elif actual_game.next_player == int(actual_game.enemy_id):
                    event_enemy_turn = pg.event.Event(MyEvents.EVENT_ENEMY_TURN, {"message": "Gegner ist dran!"})
                    pg.event.post(event_enemy_turn)






