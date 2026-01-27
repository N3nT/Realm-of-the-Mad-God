import math
import os
from typing import Set

import pygame

import config


class Projectile(pygame.sprite.Sprite):
    def __init__(
        self,
        pos: tuple,
        direction: pygame.math.Vector2,
        groups: list,
        type: str = 'player',
        power: int = 1,
        enemy_projectile_type: int = 0,
    ) -> None:
        super().__init__(groups)

        if type == 'player':
            if power == 1:
                file_name = 'player_projectile_0.png'
                self.speed = config.BULLET_SPEED
                self.lifetime = config.BULLET_LIFETIME
                self.damage = 10
                size = (65, 65)
            else:
                file_name = 'player_projectile_1.png'
                self.speed = 10
                self.lifetime = config.BULLET_LIFETIME
                self.damage = 100
                size = (80, 80)
        else:
            file_name = f'enemy_projectile_{enemy_projectile_type}.png'
            self.speed = 6
            self.lifetime = 5000
            self.damage = 20
            size = (40, 40)

        try:
            path = os.path.join('assets', 'projectile', file_name)
            original_image = pygame.image.load(path).convert_alpha()
            original_image = pygame.transform.scale(original_image, size)
        except FileNotFoundError:
            print(f"{path} not found")
            original_image = pygame.Surface((10, 10))
            color = 'yellow' if type == 'player' else 'red'
            original_image.fill(color)

        self.direction = direction
        self.spawn_time = pygame.time.get_ticks()
        self.type = type
        self.power = power
        self.hit_enemies: Set[int] = set()

        angle = math.degrees(math.atan2(self.direction.y, self.direction.x))
        self.image = pygame.transform.rotate(original_image, -angle)

        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(-20, -20)

    def update(self) -> None:
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

        self.hitbox.center = self.rect.center

        if pygame.time.get_ticks() - self.spawn_time > 1000:
            self.kill()