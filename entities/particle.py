import os

import pygame


class DeathEffect(pygame.sprite.Sprite):
    def __init__(self, pos: tuple, groups: list) -> None:
        super().__init__(groups)

        path = os.path.join('assets', 'dead.png')
        self.image = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.rect = self.image.get_rect(center=pos)

        self.spawn_time = pygame.time.get_ticks()
        self.lifetime: int = 2000
        self.alpha: int = 255

    def update(self) -> None:
        current_time = pygame.time.get_ticks()

        if current_time - self.spawn_time > 1000:
            self.alpha -= 5

            if self.alpha <= 0:
                self.kill()
            else:
                self.image.set_alpha(self.alpha)