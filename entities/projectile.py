import pygame
import config
import math
import os


class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction, groups):
        super().__init__(groups)

        path = os.path.join('assets', 'projectile', 'projectile_0.png')
        original_image = pygame.image.load(path).convert_alpha()
        original_image = pygame.transform.scale(original_image, (100, 100))


        self.direction = direction
        self.speed = config.BULLET_SPEED
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = config.BULLET_LIFETIME

        angle = math.degrees(math.atan2(-self.direction.y, self.direction.x))

        self.image = pygame.transform.rotate(original_image, angle)

        self.rect = self.image.get_rect(center=pos)

    def update(self):
        self.rect.center += self.direction * self.speed

        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()