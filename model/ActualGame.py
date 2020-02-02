# Objekt für das aktuelle Spiel
class ActualGame:
    def __init__(self):
        self.game_id = None
        self.enemy_id = 0
        self.turn = 0
        self.enemy_name = ""
        self.active_player = 0
        self.next_player = 0
        self.row = 99
        self.col = 99
        self.result = ""
        self.sunk = 0
        self.end = "False"
        self.winner = 0
        self.repeat = False
        self.status = ""


