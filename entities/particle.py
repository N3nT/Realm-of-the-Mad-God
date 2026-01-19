import pygame
import os

class DeathEffect(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)

        path = os.path.join('assets', 'dead.png')
        self.image = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.rect = self.image.get_rect(center=pos)

        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 2000  #ms
        self.alpha = 255

    def update(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.spawn_time > 1000:
            self.alpha -= 5  # Zmniejszamy widoczność co klatkę (szybkość znikania)

                # Zabezpieczenie, żeby nie zeszło poniżej 0
            if self.alpha <= 0:
                self.kill()
            else:
                    # Nakładamy nową przezroczystość
                self.image.set_alpha(self.alpha)