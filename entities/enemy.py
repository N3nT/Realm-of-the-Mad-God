import pygame
import os

from entities.projectile import Projectile
from entities.particle import DeathEffect


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player, enemy_name, hp, speed, size, bullet_group, xp_reward, obstacle_sprites, shoot_type=None, stop_distance=0, ):
        super().__init__(groups)
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
        self.can_shoot = True
        self.shoot_time = 0
        self.cooldown = 1500

        self._is_hit = False
        self.hit_time = 0
        self.hit_duration = 150 #ms

        self.obstacle_sprites = obstacle_sprites
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)

    def import_graphics(self, name):
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

    def get_player_distance_direction(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)

        # Obliczamy wektor różnicy (od wroga do gracza)
        diff_vec = player_vec - enemy_vec
        distance = diff_vec.magnitude()

        if distance > 0:
            # Normalize skaluje wektor do długości 1 (sam kierunek)
            direction = diff_vec.normalize()
        else:
            direction = pygame.math.Vector2()

        return (distance, direction)

    def collision(self, direction):
        # Jeśli wróg nie ma listy przeszkód pomiń sprawdzanie
        if not self.obstacle_sprites:
            return

        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:  # Szedł w prawo
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:  # Szedł w lewo
                        self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:  # Szedł w dół
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:  # Szedł w górę
                        self.hitbox.top = sprite.hitbox.bottom

    def move(self):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * self.speed
        self.collision('horizontal')

        self.hitbox.y += self.direction.y * self.speed
        self.collision('vertical')

        self.rect.center = self.hitbox.center

    def shoot(self):
        if self.shoot_type and self.can_shoot:
            distance, direction = self.get_player_distance_direction(self.player)

            if distance < 500:
                Projectile(self.rect.center, direction, [self.sprite_groups[0], self.bullet_group], type='enemy')
                self.can_shoot = False
                self.shoot_time = pygame.time.get_ticks()

    def take_damage(self, damage):
        self.health -= damage
        self._is_hit = True
        self.hit_time = pygame.time.get_ticks()

        print(f"{type(self)} dostal {damage}")
        if self.health <= 0:
            DeathEffect(self.rect.center, [self.sprite_groups[0]])
            self.kill()

    def hit_reaction(self):
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

    def shoot_cooldown_handler(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.cooldown:
                self.can_shoot = True

    def animate(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        original_img = self.frames[int(self.frame_index)]

        if self.direction.x < 0:
            self.image = pygame.transform.flip(original_img, True, False)
        else:
            self.image = original_img.copy() # Robimy kopię, żeby nie zamalować oryginału w pamięci

        if self._is_hit:
            hurt_surf = self.image.copy()
            hurt_surf.fill((200, 0, 0, 255), special_flags=pygame.BLEND_RGB_ADD)
            self.image = hurt_surf

    def repel_neighbors(self):
        repel_vector = pygame.math.Vector2(0, 0)

        for sprite in self.groups()[0]:

            if sprite is not self and hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy':

                enemy_vec = pygame.math.Vector2(self.rect.center)
                other_vec = pygame.math.Vector2(sprite.rect.center)

                diff = enemy_vec - other_vec
                dist = diff.magnitude()

                if 0 < dist < 50:
                    diff = diff.normalize()
                    repel_vector += diff

        return repel_vector

    def update(self):
        dist, direction = self.get_player_distance_direction(self.player)
        self.direction = direction

        repel = self.repel_neighbors()
        self.direction += repel * 1

        if dist < self.stop_distance:
            self.direction = pygame.math.Vector2()  # Stop

        if dist > 2000:
            self.kill()

        self.move()
        self.hit_reaction()
        self.animate()
        self.shoot()
        self.shoot_cooldown_handler()


class Ghost(Enemy):
    # (szerokosc, wysokosc)
    def __init__(self, pos, groups, player, enemy_name, hp, speed, bullet_group, obstacle_sprites):
        super().__init__(pos, groups, player, enemy_name, hp, speed, (60, 80), bullet_group, 10, obstacle_sprites,'enemy')

class Politician(Enemy):
    def __init__(self, pos, groups, player, enemy_name, hp, speed, bullet_group, obstacle_sprites):
        super().__init__(pos, groups, player, enemy_name, hp, speed, (55, 80), bullet_group, 69, obstacle_sprites)

class Butcher(Enemy):
    def __init__(self, pos, groups, player, enemy_name, hp, speed, bullet_group, obstacle_sprites):
        super().__init__(pos, groups, player, enemy_name, hp, speed, (80, 110), bullet_group, 150, obstacle_sprites)

class Bat(Enemy):
    def __init__(self, pos, groups, player, enemy_name, hp, speed, bullet_group, obstacle_sprites):
        super().__init__(pos, groups, player, enemy_name, hp, speed, (70, 70), bullet_group, 20, obstacle_sprites)
