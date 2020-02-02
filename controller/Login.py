from controller.RestClient import *
from controller.Placement import place_ships


# Anmelden
def login(login_data):
    post_login(login_data)
    if MyEvents.EVENT_LOGGED_IN:
        get_statistics()
    # Schiffe platzieren Bildschirm anzeigen
        place_ships(True)
    else:
        print("Serverfehler - bitte probieren Sie es später noch einmal")


# Registrieren
def register(login_data):
    # Wenn Registrieren erfolgreich, Login direkt ausführen
    post_register(login_data)
    if MyEvents.EVENT_REGISTERED:
        login(login_data)
        if MyEvents.EVENT_LOGGED_IN:
            # Schiffe platzieren Bildschirm aufrufen
            place_ships(True)
    else:
        print("Serverfehler - bitte probieren Sie es später noch einmal")