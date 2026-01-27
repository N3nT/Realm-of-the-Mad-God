import os
import random

import pygame

from entities.particle import DeathEffect
from entities.projectile import Projectile


class Enemy(pygame.sprite.Sprite):
    def __init__(
        self,
        pos: tuple,
        groups: list,
        player,
        enemy_name: str,
        hp: int,
        speed: float,
        size: tuple,
        bullet_group,
        xp_reward: int,
        obstacle_sprites: list,
        shoot_type: str = None,
        stop_distance: int = 0,
    ) -> None:
        super().__init__(groups)
        self.sprite_type = 'enemy'
        self.bar_max_width = 40
        self.bar_height = 5

        self.player = player
        self.speed = speed
        self.health = hp
        self.max_health = hp
        self.size = size
        self.sprite_groups = groups
        self.bullet_group = bullet_group
        self.xp_reward = xp_reward

        self.frame_index = 0
        self.animation_speed = 0.15
        self.enemy_name = enemy_name

        self.import_graphics(enemy_name)
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.direction = pygame.math.Vector2()
        self.stop_distance = stop_distance
        self.shoot_type = shoot_type
        self.projectile_type = random.randint(0, 1) if shoot_type else None
        self.can_shoot = True
        self.shoot_time = 0
        self.cooldown = 1500

        self._is_hit = False
        self.hit_time = 0
        self.hit_duration = 150

        self.obstacle_sprites = obstacle_sprites
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)

    def import_graphics(self, name: str) -> None:
        self.frames = []
        path = os.path.join('assets', 'enemies', name)

        for i in range(3):
            file_name = f"{name}_{i}.png"
            full_path = os.path.join(path, file_name)
            try:
                self.image = pygame.image.load(full_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, self.size)
                self.frames.append(self.image)
            except (FileNotFoundError, TypeError):
                print(f"OSTRZEŻENIE: Nie znaleziono pliku: {full_path}")
                pass

    def get_player_distance_direction(self, player) -> tuple:
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)

        diff_vec = player_vec - enemy_vec
        distance = diff_vec.magnitude()

        if distance > 0:
            direction = diff_vec.normalize()
        else:
            direction = pygame.math.Vector2()

        return (distance, direction)

    def collision(self, direction: str, enemy_group=None) -> None:
        if not self.obstacle_sprites:
            return

        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right

            if enemy_group:
                for sprite in enemy_group:
                    if sprite is not self and sprite.hitbox.colliderect(self.hitbox):
                        if self.direction.x > 0:
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0:
                            self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom

            if enemy_group:
                for sprite in enemy_group:
                    if sprite is not self and sprite.hitbox.colliderect(self.hitbox):
                        if self.direction.y > 0:
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0:
                            self.hitbox.top = sprite.hitbox.bottom

    def move(self, enemy_group=None) -> None:
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * self.speed
        self.collision('horizontal', enemy_group)

        self.hitbox.y += self.direction.y * self.speed
        self.collision('vertical', enemy_group)

        self.rect.center = self.hitbox.center

    def shoot(self) -> None:
        if self.shoot_type and self.can_shoot:
            distance, direction = self.get_player_distance_direction(self.player)

            if distance < 500:
                Projectile(
                    self.rect.center,
                    direction,
                    [self.sprite_groups[0], self.bullet_group],
                    type='enemy',
                    enemy_projectile_type=self.projectile_type,
                )
                self.can_shoot = False
                self.shoot_time = pygame.time.get_ticks()

    def take_damage(self, damage: int) -> None:
        self.health -= damage
        self._is_hit = True
        self.hit_time = pygame.time.get_ticks()

        print(
            f"{type(self).__name__} took {damage} damage. "
            f"Health: {self.health}/{self.max_health}"
        )
        if self.health <= 0:
            DeathEffect(self.rect.center, [self.sprite_groups[0]])
            self.kill()

    def hit_reaction(self) -> None:
        if self._is_hit:
            current_time = pygame.time.get_ticks()
            if current_time - self.hit_time >= self.hit_duration:
                self._is_hit = False

        original_img = self.frames[int(self.frame_index)]

        if self.direction.x < 0:
            self.image = pygame.transform.flip(original_img, True, False)
        else:
            self.image = original_img.copy()

        if self._is_hit:
            hurt_surf = self.image.copy()
            hurt_surf.fill((200, 0, 0, 255), special_flags=pygame.BLEND_RGB_ADD)
            self.image = hurt_surf

    def shoot_cooldown_handler(self) -> None:
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.cooldown:
                self.can_shoot = True

    def animate(self) -> None:
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        original_img = self.frames[int(self.frame_index)]

        if self.direction.x < 0:
            self.image = pygame.transform.flip(original_img, True, False)
        else:
            self.image = original_img.copy()

        if self._is_hit:
            hurt_surf = self.image.copy()
            hurt_surf.fill((200, 0, 0, 255), special_flags=pygame.BLEND_RGB_ADD)
            self.image = hurt_surf

    def repel_neighbors(self, enemy_group=None) -> pygame.math.Vector2:
        repel_vector = pygame.math.Vector2(0, 0)
        min_separation = 110

        if enemy_group is None:
            return repel_vector

        for sprite in enemy_group:
            if (
                sprite is not self
                and hasattr(sprite, 'sprite_type')
                and sprite.sprite_type == 'enemy'
            ):
                enemy_vec = pygame.math.Vector2(self.rect.center)
                other_vec = pygame.math.Vector2(sprite.rect.center)

                diff = enemy_vec - other_vec
                dist = diff.magnitude()

                if 0 < dist < min_separation:
                    strength = ((min_separation - dist) / min_separation) ** 1.5
                    if dist > 0:
                        diff = diff.normalize()
                        repel_vector += diff * strength

        return repel_vector

    def update(self, enemy_group=None) -> None:
        dist, direction = self.get_player_distance_direction(self.player)
        self.direction = direction

        if enemy_group:
            repel = self.repel_neighbors(enemy_group)
            self.direction += repel * 5.0

        if dist < self.stop_distance:
            self.direction = pygame.math.Vector2()

        if dist > 2000:
            self.kill()

        self.move(enemy_group)
        self.hit_reaction()
        self.animate()
        self.shoot()
        self.shoot_cooldown_handler()


class Ghost(Enemy):
    def __init__(
        self,
        pos: tuple,
        groups: list,
        player,
        enemy_name: str,
        hp: int,
        speed: float,
        bullet_group,
        obstacle_sprites: list,
    ) -> None:
        super().__init__(
            pos,
            groups,
            player,
            enemy_name,
            hp,
            speed,
            (60, 80),
            bullet_group,
            10,
            obstacle_sprites,
            'enemy',
        )


class Politician(Enemy):
    def __init__(
        self,
        pos: tuple,
        groups: list,
        player,
        enemy_name: str,
        hp: int,
        speed: float,
        bullet_group,
        obstacle_sprites: list,
    ) -> None:
        super().__init__(
            pos, groups, player, enemy_name, hp, speed, (55, 80), bullet_group, 69, obstacle_sprites
        )


class Butcher(Enemy):
    def __init__(
        self,
        pos: tuple,
        groups: list,
        player,
        enemy_name: str,
        hp: int,
        speed: float,
        bullet_group,
        obstacle_sprites: list,
    ) -> None:
        super().__init__(
            pos,
            groups,
            player,
            enemy_name,
            hp,
            speed,
            (80, 110),
            bullet_group,
            150,
            obstacle_sprites,
        )


class Bat(Enemy):
    def __init__(
        self,
        pos: tuple,
        groups: list,
        player,
        enemy_name: str,
        hp: int,
        speed: float,
        bullet_group,
        obstacle_sprites: list,
    ) -> None:
        super().__init__(
            pos, groups, player, enemy_name, hp, speed, (70, 70), bullet_group, 20, obstacle_sprites
        )


class Skeleton(Enemy):
    def __init__(
        self,
        pos: tuple,
        groups: list,
        player,
        enemy_name: str,
        hp: int,
        speed: float,
        bullet_group,
        obstacle_sprites: list,
    ) -> None:
        super().__init__(
            pos, groups, player, enemy_name, hp, speed, (80, 90), bullet_group, 100, obstacle_sprites
        )


class BlackMagic(Enemy):
    def __init__(
        self,
        pos: tuple,
        groups: list,
        player,
        enemy_name: str,
        hp: int,
        speed: float,
        bullet_group,
        obstacle_sprites: list,
    ) -> None:
        super().__init__(
            pos,
            groups,
            player,
            enemy_name,
            hp,
            speed,
            (75, 95),
            bullet_group,
            120,
            obstacle_sprites,
            shoot_type='enemy',
            stop_distance=250,
        )


class Mage(Enemy):
    def __init__(
        self,
        pos: tuple,
        groups: list,
        player,
        enemy_name: str,
        hp: int,
        speed: float,
        bullet_group,
        obstacle_sprites: list,
    ) -> None:
        super().__init__(
            pos,
            groups,
            player,
            enemy_name,
            hp,
            speed,
            (70, 90),
            bullet_group,
            110,
            obstacle_sprites,
            shoot_type='enemy',
            stop_distance=200,
        )
