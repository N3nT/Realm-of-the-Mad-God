import pygame
import config
import math
import os


class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction, groups, type='player'):
        super().__init__(groups)

        # sprawdzenie kto uzywa pocisku
        if type == 'player':
            file_name = 'player_projectile_0.png'
            self.speed = config.BULLET_SPEED
            self.lifetime = config.BULLET_LIFETIME
        else:
            file_name = 'enemy_projectile_0.png'
            self.speed = 6
            self.lifetime = 1500

        try:
            path = os.path.join('assets', 'projectile', file_name)
            original_image = pygame.image.load(path).convert_alpha()
            original_image = pygame.transform.scale(original_image, (65, 65))
        except FileNotFoundError:
            print(f"{path} not found")
            original_image = pygame.Surface((10, 10))
            color = 'yellow' if type == 'player' else 'red'
            original_image.fill(color)

        self.direction = direction
        # path = os.path.join('assets', 'projectile', 'player_projectile_0.png')
        # original_image = pygame.image.load(path).convert_alpha()
        # original_image = pygame.transform.scale(original_image, (100, 100))
        self.spawn_time = pygame.time.get_ticks()


        angle = math.degrees(math.atan2(-self.direction.y, self.direction.x))

        self.image = pygame.transform.rotate(original_image, angle)

        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(-20, -20)
        self.type = type

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

        self.hitbox.center = self.rect.center

        if pygame.time.get_ticks() - self.spawn_time > 1000:
            self.kill()