import pygame
import random
import config
from entities.tile import Tile


class MapManager:
    def __init__(self, all_sprites, obstacle_sprites, spawn_callback):
        self.all_sprites = all_sprites
        self.obstacle_sprites = obstacle_sprites
        self.spawn_callback = spawn_callback
        self.active_chunks = {}

        self.CHUNK_SIZE_TILES = 20
        self.CHUNK_PIXEL_SIZE = self.CHUNK_SIZE_TILES * config.TILE_SIZE

    def update(self, player_pos):
        px, py = player_pos
        current_chunk_x = int(px // self.CHUNK_PIXEL_SIZE)
        current_chunk_y = int(py // self.CHUNK_PIXEL_SIZE)

        target_chunks = []
        for x in range(current_chunk_x - 1, current_chunk_x + 2):
            for y in range(current_chunk_y - 1, current_chunk_y + 2):
                target_chunks.append((x, y))

        for chunk_coord in target_chunks:
            if chunk_coord not in self.active_chunks:
                self.generate_chunk(chunk_coord)

        for chunk_coord in list(self.active_chunks.keys()):
            if chunk_coord not in target_chunks:
                self.unload_chunk(chunk_coord)

    def generate_chunk(self, chunk_coord):
        cx, cy = chunk_coord

        seed = (cx * 73856093) ^ (cy * 19349663)
        rng = random.Random(seed)
        structure_type = rng.choice(['empty', 'pillars', 'random_walls', 'ruins'])
        start_x = cx * self.CHUNK_PIXEL_SIZE
        start_y = cy * self.CHUNK_PIXEL_SIZE
        wall_positions = set()  # przechowuje krotki (x, y) w układzie siatki

        for row in range(self.CHUNK_SIZE_TILES):
            for col in range(self.CHUNK_SIZE_TILES):
                place_wall = False

                if structure_type == 'pillars' and col % 4 == 0 and row % 4 == 0:
                    place_wall = True
                elif structure_type == 'random_walls' and rng.random() < 0.15:
                    place_wall = True
                elif structure_type == 'ruins':
                    is_border = row == 0 or row == self.CHUNK_SIZE_TILES - 1 or col == 0 or col == self.CHUNK_SIZE_TILES - 1
                    if is_border and not ((col == 10) or (row == 10)):
                        place_wall = True
                else:
                    if rng.random() < 0.02:
                        if pygame.math.Vector2(start_x, start_y).magnitude() > 600:
                            self.spawn_callback((start_x, start_y))

                if place_wall:
                    wall_positions.add((col, row))

        chunk_walls = []

        for (col, row) in wall_positions:
            tile_x = start_x + (col * config.TILE_SIZE)
            tile_y = start_y + (row * config.TILE_SIZE)

            neighbor_n = (col, row - 1) in wall_positions  # Północ (Góra)
            neighbor_s = (col, row + 1) in wall_positions  # Południe (Dół)
            neighbor_w = (col - 1, row) in wall_positions  # Zachód (Lewo)
            neighbor_e = (col + 1, row) in wall_positions  # Wschód (Prawo)

            connections = ""
            if neighbor_n: connections += "N"
            if neighbor_s: connections += "S"
            if neighbor_w: connections += "W"
            if neighbor_e: connections += "E"

            wall = Tile(
                (tile_x, tile_y),
                [self.all_sprites, self.obstacle_sprites],
                'wall',
                connections=connections
            )
            chunk_walls.append(wall)

        self.active_chunks[chunk_coord] = chunk_walls

    def unload_chunk(self, chunk_coord):
        walls = self.active_chunks[chunk_coord]

        for wall in walls:
            wall.kill()

        del self.active_chunks[chunk_coord]