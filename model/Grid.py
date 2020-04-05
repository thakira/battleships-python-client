# Kästchenmuster für Schiffe erstellen
import pygame as pg


class Grid:

    def __init__(self, grid_size, grid_pos_x, grid_pos_y):
        # Gridgrösse = halbe Größe des Spielefensters
        self.grid_size = grid_size
        self.cell_size = int(grid_size/10)
        self.grid_pos_x = grid_pos_x
        self.grid_pos_y = grid_pos_y
        # Anzeige für Grid erstellen
        self.surface = pg.Surface((self.grid_size, self.grid_size))
        self.surface.set_alpha(180)
        self.surface.fill((155, 181, 196))

        # Array für Zelleninhalte erstellen
        self.cells = []
        for self.row in range(10):
            self.cells.append([])
            for self.column in range(10):
                self.cells[self.row].append(0)  # Append a cell

        # Hintergrund und Zwischenlinien zeichnen
        for x in range(0, self.grid_size, self.cell_size):
            pg.draw.lines(self.surface, (255, 255, 255), False,
                          [[0, x], [self.grid_size, x]], 1)
            pg.draw.lines(self.surface, (255, 255, 255), False,
                          [[x, 0], [x, self.grid_size]], 1)

        # Spielfeld erstellen

    def get_grid_surface(self):
        return self.surface

    # Abfrage, ob Schiff innerhalb des Grids mit halbem Kästchen außerhalb Toleranz
    def in_grid(self, ship_sprite):
        if self.grid_pos_x - self.cell_size//2 < ship_sprite.rect.x < self.grid_pos_x:
            ship_sprite.rect.x = self.grid_pos_x
        if self.grid_pos_y - self.cell_size//2 < ship_sprite.rect.y < self.grid_pos_y:
            ship_sprite.rect.y = self.grid_pos_y
        if self.grid_pos_x + self.grid_size + self.cell_size//2 > ship_sprite.rect.x + ship_sprite.rect.w > self.grid_pos_x + self.grid_size:
            ship_sprite.rect.x = (self.grid_pos_x+self.grid_size)-ship_sprite.rect.w
        if self.grid_pos_y + self.grid_size + self.cell_size//2 > ship_sprite.rect.y + ship_sprite.rect.h > self.grid_pos_y + self.grid_size:
            ship_sprite.rect.y = (self.grid_pos_y + self.grid_size)- ship_sprite.rect.h
        if ship_sprite.rect.x >= self.grid_pos_x and ship_sprite.rect.y >= self.grid_pos_y:
            if ship_sprite.rect.x + ship_sprite.rect.w <= self.grid_pos_x + self.grid_size and ship_sprite.rect.y + ship_sprite.rect.h <= self.grid_pos_y + self.grid_size:
                return True

    # Abfrage, ob der Mauszeiger sich innerhalb des Grids befindet
    def mouse_in_grid(self, pos):
        if self.grid_pos_x < pos[0] < self.grid_pos_x + self.grid_size:
            if self.grid_pos_y < pos[1] < self.grid_pos_y + self.grid_size:
                return True

    # Feldbezeichnungen errechnen
    def get_ship_coords(self, ship):
        column = (ship.get_front()[0] - self.grid_pos_x) // self.cell_size
        row = (ship.get_front()[1] - self.grid_pos_y) // self.cell_size
        coords = (row, column)
        ship_x = column * self.cell_size + self.grid_pos_x
        ship_y = row * self.cell_size + self.grid_pos_y
        ship_rect = (ship_x, ship_y)
        return coords, ship_rect

    # Column und Row aus den übergebebenen Bildschirmkoordinaten ermitteln
    def get_grid_coords(self, pos):
        column = (pos[0] - self.grid_pos_x) // self.cell_size
        row = (pos[1] - self.grid_pos_y) // self.cell_size
        coords = (row, column)
        x = column * self.cell_size + self.grid_pos_x
        y = row * self.cell_size + self.grid_pos_y
        cellcenter = (x, y)
        return coords, cellcenter

    # aus übergebenenen Column und Row Bildschirmkoordinaten errechnen
    def get_hit_coords(self, column, row):
        x = int(self.grid_pos_x + (column * self.cell_size))
        y = int(self.grid_pos_y + ((row) * self.cell_size))
        return x, y


