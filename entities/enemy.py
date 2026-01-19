import pygame
import os

from entities.projectile import Projectile
from entities.particle import DeathEffect


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player, enemy_name, hp, speed, size, bullet_group, xp_reward, shoot_type=None, stop_distance=0):
        super().__init__(groups)
        self.player = player
        self.speed = speed
        self.health = hp
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

    def get_player_data(self):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(self.player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()

        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()

        return distance, direction

    def move(self):
        '''Przeciwnik idzie do gracza, zatrzymuje sie w odpowiedniej odleglosci'''
        distance, direction = self.get_player_data()

        if self.stop_distance < distance < 600:  # Reaguje z odległości 600px
            self.direction = direction
            self.rect.center += self.direction * self.speed
        else:
            self.direction = pygame.math.Vector2()

    def shoot(self):
        if self.shoot_type and self.can_shoot:
            distance, direction = self.get_player_data()

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

        # 1. Pobieramy klatkę
        original_img = self.frames[int(self.frame_index)]

        # 2. Obracamy (jeśli idzie w lewo)
        if self.direction.x < 0:
            self.image = pygame.transform.flip(original_img, True, False)
        else:
            self.image = original_img.copy() # Robimy kopię, żeby nie zamalować oryginału w pamięci

        # 3. NOWE: Nakładamy czerwony filtr
        if self._is_hit:
            # Tworzymy czerwoną powierzchnię
            hurt_surf = self.image.copy()
            # BLEND_RGB_ADD dodaje wartości kolorów (R+255, G+0, B+0)
            # Sprawia to, że obrazek robi się jaskrawo czerwony/białawy
            hurt_surf.fill((200, 0, 0, 255), special_flags=pygame.BLEND_RGB_ADD)
            self.image = hurt_surf

    def update(self):
        self.move()
        self.hit_reaction()
        self.animate()
        self.shoot()
        self.shoot_cooldown_handler()


class Ghost(Enemy):
    # (szerokosc, wysokosc)
    def __init__(self, pos, groups, player, enemy_name, hp, speed, bullet_group):
        super().__init__(pos, groups, player, enemy_name, hp, speed, (60, 80), bullet_group, 10, 'enemy')

class Politician(Enemy):
    def __init__(self, pos, groups, player, enemy_name, hp, speed, bullet_group):
        super().__init__(pos, groups, player, enemy_name, hp, speed, (55, 80), bullet_group, 69)

class Butcher(Enemy):
    def __init__(self, pos, groups, player, enemy_name, hp, speed, bullet_group):
        super().__init__(pos, groups, player, enemy_name, hp, speed, (80, 110), bullet_group, 150)

class Bat(Enemy):
    def __init__(self, pos, groups, player, enemy_name, hp, speed, bullet_group):
        super().__init__(pos, groups, player, enemy_name, hp, speed, (70, 70), bullet_group, 20)
