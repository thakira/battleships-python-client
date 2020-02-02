# REST-Kommunikation

import requests
import json
from model.User import User
import model.Ship as Ship
import jwt
from model.ActualGame import ActualGame
import wget
import pygame as pg
import time
from model.Events import MyEvents
import threading

# Spieler und aktuelles Spielobjekt initial erzeugen
player = User()
actual_game = ActualGame()

url = "http://lyra.et-inf.fho-emden.de:16213/"


def post_register(login_data):
    done = False
    response = None
    new_url = url + 'user/new_account'
    while not done:
        try:
            
            response = requests.post(new_url, json=login_data)
        except:
            server_error = pg.event.Event(MyEvents.EVENT_SERVER_ERROR,
                                          {"message": ("Serverfehler während der Registrierung, "
                                                       "versuche es noch einmal")})
            pg.event.post(server_error)
            time.sleep(5)
        if response.status_code == 200:
            registered = pg.event.Event(MyEvents.EVENT_REGISTERED, {"message": ("Registrierung erfolgreich.")})
            pg.event.post(registered)
            done = True
        else:
            request_error = pg.event.Event(MyEvents.EVENT_REQUEST_ERROR,
                                           {"message": ("Registrierung fehlgeschlagen."
                                                        "Versuche es erneut. ")})
            pg.event.post(request_error)
            time.sleep(1)


# Login, vom Server erhaltene Variablen in player schreiben
def post_login(login_data):
    done = False
    response = None
    new_url = url + 'login'
    while not done:
        try:
            response = requests.post(new_url, json=login_data)
        except:
            server_error = pg.event.Event(MyEvents.EVENT_SERVER_ERROR, {"message": ("Serverfehler Login! "
                                                                          "Versuche es erneut.")})
            pg.event.post(server_error)
            time.sleep(5)
        if response.status_code == 200:
            response = response.json()
            token = response['token']
            decoded = jwt.decode(token, verify=False)
            player.user_id = int(decoded['jti'])
            player.username = login_data['username']
            player.token = token
            logged_in = pg.event.Event(MyEvents.EVENT_LOGGED_IN, {"message": "Login erfolgreich: "})
            pg.event.post(logged_in)
            done = True
        else:
            request_error = pg.event.Event(MyEvents.EVENT_REQUEST_ERROR,
                                           {"message" : ("Login nicht möglich. Versuche es erneut. ")})
            pg.event.post(request_error)
            time.sleep(1)


# Hintergrundbild vom Server laden
def get_background():
    done = False
    response = None
    new_url = url + 'image/background_image'
    while not done:
        try:
            wget.download(new_url, '../images/bg-battle.jpg')
        except:
            server_error = pg.event.Event(MyEvents.EVENT_SERVER_ERROR, {"message" : ("Serverfehler beim Download des "
                                                                          "Hintergrundbildes. Versuche es erneut.")})
            pg.event.post(server_error)
            time.sleep(5)
        done = True

# Spiel auf dem Server stoppen
def get_stop():
    done = False
    response = None
    new_url = url + 'games/stop/' + str(player.user_id)
    while not done:
        try:
            
            response = requests.get(new_url, headers={'Content-Type': 'application/json',
                                                    'Authorization': 'Bearer {}'.format(player.token)})
        except:
            server_error = pg.event.Event(MyEvents.EVENT_SERVER_ERROR,
                                          {"message" : "Serverfehler beim Stoppen des Spiels. Versuche es erneut."})
            pg.event.post(server_error)
            time.sleep(5)
        done = True


# Gegner suchen, Spielvariablen in aktuellem Spielobjekt speichern
class games_new(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.done = False
        self.daemon = True

    def run(self):
        response = None
        new_url = url + 'games/new/' + str(player.user_id)
        while not self.done:
            try:

                response = requests.get(new_url, headers={'Content-Type': 'application/json',
                                                'Authorization': 'Bearer {}'.format(player.token)})
            except:
                server_error = pg.event.Event(MyEvents.EVENT_SERVER_ERROR,
                                              {"message" : "Serverfehler beim Warten auf ein Spiel. Versuche es erneut."})
                pg.event.post(server_error)
                time.sleep(5)
            if response.status_code == 200:
                result = response.json()
                actual_game.game_id = result["game_id"]
                actual_game.enemy_name = result["enemy_name"]
                actual_game.enemy_id = result["enemy_id"]
                game_started = pg.event.Event(MyEvents.EVENT_GAME_FOUND, {"message" : ("Spiel erfolgreich erstellt." +
                                                                                       str(response.status_code) + ", " +
                                                                                       str(response.content))})
                pg.event.post(game_started)
                self.done = True
            else:
                game_queued = pg.event.Event(MyEvents.EVENT_GAME_QUEUED, {"message": ("Warte auf Gegner... " +
                                                                                      str(response.status_code) + ", " +
                                                                                      str(response.content))})
                pg.event.post(game_queued)
                time.sleep(1)


# platzierte Schiffe an Server senden
class post_ships(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.done = False
        self.daemon = True

    def run(self):
        response = None
        ships = json.dumps(Ship.get_dict(), indent=4)
        new_url = url + 'games/' + str(actual_game.game_id) + '/' + str(player.user_id) + '/ships'
        while not self.done:
            try:
                response = requests.post(new_url, data=ships, headers={'Content-Type': 'application/json',
                                                                      'Authorization': 'Bearer {}'.format(player.token)})
            except:
                server_error = pg.event.Event(MyEvents.EVENT_SERVER_ERROR,
                                              {"message": ("Serverfehler beim Übertragen der Schiffe. "
                                                           "Versuche es noch einmal.")})
                pg.event.post(server_error)
                time.sleep(5)
            if response.status_code == 200:
                # Wenn beide Spieler ihre Schiffe erfolgreich übertragen haben, Spiel starten
                result = response.json()
                actual_game.turn = result["turn"]
                actual_game.next_player = result["next_player"]
                actual_game.active_player = result["next_player"]
                game_starts = pg.event.Event(MyEvents.EVENT_GAME_STARTS, {"message": ("Schiffe erfolgreich übertragen, "
                                                                            "Spiel startet! " + str(response.status_code)
                                                                                      + ", " + str(response.content))})
                pg.event.post(game_starts)
                self.done = True
            # Wenn der zweite Spieler noch keine Schiffe übertragen hat
            elif response.status_code == 202:
                actual_game.next_player = actual_game.enemy_id
                actual_game.turn = 0
                ships_placed = pg.event.Event(MyEvents.EVENT_SHIPS_POSTED, {"message": ("Schiffe erfolgreich übertragen, "
                                                                              "warte auf Schiffe des Gegners " +
                                                                                        str(response.status_code) + ", " +
                                                                                        str(response.content))})
                pg.event.post(ships_placed)
                self.done = True
            else:
                request_error = pg.event.Event(MyEvents.EVENT_REQUEST_ERROR,
                                               {"message": "Fehler beim Übertragen der Schiffe. Versuche es noch einmal." +
                                                                                str(response.status_code) + ", " +
                                                                                str(response.content)})
                pg.event.post(request_error)
                time.sleep(1)


# Auf Spielzug des Gegners warten
class get_turn(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.done = False
        self.daemon = True

    def run(self):
        response = None
        new_url = url + 'games/' + str(actual_game.game_id) + '/turn/' + str(actual_game.turn + 1)
        while not self.done:
            try:

                response = requests.get(new_url, headers={'Content-Type': 'application/json',
                                           'Authorization': 'Bearer {}'.format(player.token)})
            except:
                server_error = pg.event.Event(MyEvents.EVENT_SERVER_ERROR,
                                              {"message": ("Serverfehler beim Warten auf den Zug des Gegners. "
                                                           "Versuche es noch einmal.")})
                pg.event.post(server_error)
                time.sleep(5)
            if response.status_code == 200:
                result = response.json()
                actual_game.turn = result["turn"]
                actual_game.row = result["row"]
                actual_game.col = result["col"]
                actual_game.result = result["result"]
                actual_game.sunk = result["sunk"]
                actual_game.next_player = result["next"]
                actual_game.active_player = result["active_player"]
                actual_game.end = result["end"]
                actual_game.winner = result["winner"]
                event_turn_arrived = pg.event.Event(MyEvents.EVENT_TURN_ARRIVED, {"message": ("Zug des Gegners: " +
                                                                                               str(response.status_code)
                                                                                               + ", " + str(response.content))})
                pg.event.post(event_turn_arrived)
                self.done = True
            else:
                wait_4_turn = pg.event.Event(MyEvents.EVENT_WAIT_4_TURN, {"message": ("Warte auf Zug des Gegners: " +
                                                                                      str(response.status_code) + ", " +
                                                                                      str(response.content))})
                pg.event.post(wait_4_turn)
                time.sleep(1)


# eigenen Spielzug an Server senden
class send_turn(threading.Thread):
    def __init__(self, shot):
        threading.Thread.__init__(self)
        self.shot = shot
        self.done = False
        self.daemon = True

    def run(self):
        response = None
        new_url = url + "game/" + str(actual_game.game_id) + "/" + str(player.user_id)\
              + "/move?turn=" + str(actual_game.turn + 1) + "&col=" + str(self.shot[1])\
              + "&row=" + str(self.shot[0])
        while not self.done:
            try:
                response = requests.get(new_url, headers={'Content-Type': 'application/json',
                                       'Authorization': 'Bearer {}'.format(player.token)})
            except:
                server_error = pg.event.Event(MyEvents.EVENT_SERVER_ERROR,
                                              {"message": ("Serverfehler beim Senden des Zugs. Versuche es noch einmal.")})
                pg.event.post(server_error)
                time.sleep(5)
            if response.status_code == 200:
                result = response.json()
                actual_game.turn = result["turn"]
                actual_game.row = result["row"]
                actual_game.col = result["col"]
                actual_game.result = result["result"]
                actual_game.sunk = result["sunk"]
                actual_game.next_player = result["next"]
                actual_game.active_player = result["active_player"]
                actual_game.end = result["end"]
                actual_game.winner = result["winner"]
                # event_turn_posted = pg.event.Event(Events.EVENT_TURN_POSTED, {"message": ("Antwort auf eigenen Zug:" +
                #                                                             str(response.status_code) + ", " +
                #                                                             str(response.content))})
                event_turn_posted = pg.event.Event(MyEvents.EVENT_TURN_POSTED, {"message": "Antwort auf eigenen Zug"})
                pg.event.post(event_turn_posted)
                self.done = True
            if response.status_code == 423:
                actual_game.turn = actual_game.turn - 1
                already_shot = pg.event.Event(MyEvents.EVENT_ALREADY_SHOT,
                                              {"message": ("Du hast hier bereits hingeschossen! " +
                                                           str(response.status_code) + ", " + str(response.content))})
                pg.event.post(already_shot)
                self.done = True
            else:
                request_error = pg.event.Event(MyEvents.EVENT_REQUEST_ERROR,
                                               {"message": ("Fehler beim Senden des eigenen Zugs. Versuche es noch einmal."
                                                            + str(response.status_code) + ", " + str(response.content))})
                pg.event.post(request_error)
                time.sleep(1)


# Statistiken vom Server abrufen
def get_statistics():
    done = False
    response = None
    new_url = url + 'statistics/' + str(player.user_id)
    while not done:
        try:
            
            response = requests.get(new_url, headers={'Content-Type': 'application/json',
                                       'Authorization': 'Bearer {}'.format(player.token)})
        except:
            server_error = pg.event.Event(MyEvents.EVENT_SERVER_ERROR,
                                          {"message": ("Serverfehler beim Abrufen der Statistiken. "
                                                       "Versuche es erneut.")})
            pg.event.post(server_error)
            time.sleep(5)
        if response.status_code == 200:
            result = response.json()
            player.games = result["games"]
            player.wins = result["wins"]
            # statistics = pg.event.Event(MyEvents.EVENT_STATISTICS, {"message": "Statistiken abgerufen"})
            # pg.event.post(statistics)
            done = True
        else:
            pg.event.Event(MyEvents.EVENT_REQUEST_ERROR, {"message": ("Fehler beim Abrufen der Statistiken. "
                                                            "Versuche es erneut." + str(response.status_code) +
                                                                        ", " + str(response.content))})
            time.sleep(1)


def start_thread(target):
    target = target()
    target.start()
    return


def start_thread_args(target, args):
    target = target(args)
    target.start()
    return
