
import pygame as pg

# Sprite-Gruppen für platzierte und noch nicht platzierte Schiffe erstellen
placed_sprites = pg.sprite.Group()
ship_sprites = pg.sprite.Group()

# Schiff Objekte
class Ship(pg.sprite.Sprite):

    def __init__(self, id, type, x, y, cell_size):
        pg.sprite.Sprite.__init__(self)
        self.height = int(cell_size)
        self.length = type * self.height
        self.ship_id = id
        self.ship_type = type
        self.horizontal = True
        self.row = -1
        self.column = -1
        if type == 2:
            self.image = pg.image.load('../Images/Zweier.png')
        elif type == 3:
            self.image = pg.image.load('../Images/Dreier.png')
        elif type == 4:
            self.image = pg.image.load('../Images/Vierer.png')
        elif type == 5:
            self.image = pg.image.load('../Images/Fuenfer.png')
        self.image = pg.transform.scale(self.image, (self.length, self.height))
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.initial_rect_x = x
        self.initial_rect_y = y
        self.front = self.get_front()
        ship_sprites.add(self)

    # umliegendes Rechteck des Schiffes abfragen
    def get_rect(self):
        return self.rect

    # ID eines Schiffes abfragen
    def get_id(self):
        return self.ship_id

    # Koordinaten der Schiffspitze erhalten
    def get_front(self):
        if self.horizontal:
            self.front = self.rect.midleft
        elif not self.horizontal:
            self.front = self.rect.midtop
        return self.front

    # Schiff rotieren
    def rotate(self):
        if self.horizontal:
            self.image = pg.transform.rotate(self.image, -90)
            self.horizontal = False

        elif not self.horizontal:
            self.image = pg.transform.rotate(self.image, 90)
            self.horizontal = True
        self.rect.size = self.image.get_size()
        self.length = self.rect.size[0]
        self.height = self.rect.size[1]
        pg.mouse.set_pos(self.front)
        return self.get_front()

    # Schiffsposition verändern
    def set_grid_pos(self, ownGrid):
        grid_pos = ownGrid.get_ship_coords(self)
        self.column = grid_pos[0][1]
        self.row = grid_pos[0][0]
        self.rect.x = grid_pos[1][0]
        self.rect.y = grid_pos[1][1]
        pg.mouse.set_pos(self.front)
        return

    # Schiff zurück auf Ausgangsposition schieben
    def ship_back(self):
        while not self.horizontal:
            self.rotate()
        self.rect.x = self.initial_rect_x
        self.rect.y = self.initial_rect_y
        return


# Kollision mit anderen Schiffen abfragen
def free_space(ship_sprite):
    collision = False
    if len(placed_sprites) == 0:
        return True
    else:
        for placed_sprite in placed_sprites:
            if ship_sprite.get_rect().colliderect(placed_sprite.rect.inflate(-20, -20)):
                collision = True
    if not collision:
        return True
    else:
        return False

# Schiffe erstellen
def create_ships(size, cell_size):
    ship_2_1 = Ship(0, 2, 50, int(size[1] / 3 + 10), cell_size)
    ship_2_2 = Ship(1, 2, 160, int(size[1] / 3 + 10), cell_size)
    # ship_2_3 = Ship(2, 2, 50, int(size[1] / 3 + 10) + 60, cell_size)
    # ship_2_4 = Ship(3, 2, 160, int(size[1] / 3 + 10) + 60, cell_size)
    # ship_3_1 = Ship(4, 3, 50, int(size[1] / 3 + 10) + 120, cell_size)
    # ship_3_2 = Ship(5, 3, 210, int(size[1] / 3 + 10) + 120, cell_size)
    # ship_3_3 = Ship(6, 3, 50, int(size[1] / 3 + 10) + 180, cell_size)
    # ship_4_1 = Ship(7, 4, 50, int(size[1] / 3 + 10) + 240, cell_size)
    # ship_4_2 = Ship(8, 4, 50, int(size[1] / 3 + 10) + 300, cell_size)
    # ship_5_1 = Ship(9, 5, 50, int(size[1] / 3 + 10) + 360, cell_size)


# Liste mit noch nicht platzierten Schiffobjekten erhalten
def get_ships():
    return ship_sprites


# Liste mit platzierten Schiffobjekten erhalten
def get_placed_sprites():
    return placed_sprites


# JSON der Schiffobjekte für den REST-Versand an den Server erstellen
def get_dict():
    ships = []
    for ship in placed_sprites:
        ship = {"ship_type": ship.ship_type, "row": ship.row
                , "col": ship.column, "horizontal": ship.horizontal}
        ships.append(ship)
    return ships


