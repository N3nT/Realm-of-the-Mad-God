import os

import pygame

import config


class Tile(pygame.sprite.Sprite):
    def __init__(
        self, pos: tuple, groups: list, sprite_type: str, surface=None, connections: str = ""
    ) -> None:
        super().__init__(groups)
        self.sprite_type = sprite_type

        if surface:
            self.image = surface
        else:
            if sprite_type == 'wall':
                try:
                    path = os.path.join('assets', 'wall.png')
                    original_image = pygame.image.load(path).convert_alpha()
                    original_image = pygame.transform.scale(
                        original_image, (config.TILE_SIZE, config.TILE_SIZE)
                    )

                    self.image = original_image

                    is_vertical = 'N' in connections or 'S' in connections
                    is_horizontal = 'W' in connections or 'E' in connections

                    if is_vertical and not is_horizontal:
                        self.image = pygame.transform.rotate(original_image, 90)

                except Exception as e:
                    print(e)
                    self.image = pygame.Surface((config.TILE_SIZE, config.TILE_SIZE))
                    self.image.fill((100, 100, 100))
            else:
                self.image = pygame.Surface((config.TILE_SIZE, config.TILE_SIZE))
                self.image.fill('white')

        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-40, -40)