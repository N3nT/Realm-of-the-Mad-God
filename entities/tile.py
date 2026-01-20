import pygame
import config
import os  # Konieczny import do obsługi ścieżek


class Tile(pygame.sprite.Sprite):
    # Dodajemy argument 'connections' z domyślną wartością ""
    def __init__(self, pos, groups, sprite_type, surface=None, connections=""):
        super().__init__(groups)
        self.sprite_type = sprite_type

        if surface:
            self.image = surface
        else:
            if sprite_type == 'wall':
                try:
                    path = os.path.join('assets', 'wall.png')
                    original_image = pygame.image.load(path).convert_alpha()
                    original_image = pygame.transform.scale(original_image, (config.TILE_SIZE, config.TILE_SIZE))

                    self.image = original_image  # Domyślny obrazek

                    # --- LOGIKA OBRACANIA ---

                    # Jeśli ściana ma sąsiadów TYLKO góra/dół (jest pionowa)
                    # Oraz NIE MA sąsiadów bocznych -> Obróć o 90 stopni
                    is_vertical = ('N' in connections or 'S' in connections)
                    is_horizontal = ('W' in connections or 'E' in connections)

                    if is_vertical and not is_horizontal:
                        self.image = pygame.transform.rotate(original_image, 90)

                    # (Opcjonalnie) Tutaj mógłbyś ładować zupełnie inne obrazki
                    # np. if connections == "NSEW": self.image = load('wall_cross.png')

                except Exception as e:
                    print(e)
                    self.image = pygame.Surface((config.TILE_SIZE, config.TILE_SIZE))
                    self.image.fill((100, 100, 100))
            else:
                self.image = pygame.Surface((config.TILE_SIZE, config.TILE_SIZE))
                self.image.fill('white')

        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-40, -40)