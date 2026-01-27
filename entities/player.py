import os
from typing import Optional, Dict, List, Any

import pygame

import config
from entities.projectile import Projectile


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, create_bullet_group, save_data=None):
        super().__init__(groups)

        self.sprite_groups = groups
        self.bullet_group = create_bullet_group

        self.vulnerable = True
        self.hurt_time = 0
        self.invincibility_duration = 500

        self.health = 100
        self.max_health = 100

        self.image = pygame.Surface((config.PLAYER_SIZE, config.PLAYER_SIZE))
        self.rect = self.image.get_rect(topleft=pos)

        self.status = 'down'
        self.frame_index = 0

        self.walk_animation_speed = 0.15
        self.sprint_animation_speed = 0.25
        self.animation_speed = self.walk_animation_speed

        self.is_attacking = False
        self.attack_time = 0

        self.import_assets()

        self.image = self.animations[self.status][self.frame_index]

        self.direction = pygame.math.Vector2()
        self.speed = config.PLAYER_SPEED

        self.can_shoot = True
        self.shoot_time = 0
        self.cooldown = config.SHOOT_COOLDOWN
        self.can_power_shoot: bool = True
        self.power_shoot_time: int = 0
        self.power_shoot_cooldown: int = 800

        self.step_timer = 0
        self.step_delay = 350

        self.energy = 100
        self.max_energy = 100
        self.energy_drain_rate = 0.5
        self.energy_recover_rate = 0.05

        self.xp = 0
        self.level = 1
        self.xp_to_next_level = 100

        self.obstacle_sprites = obstacle_sprites
        self.hitbox = self.rect.inflate(-20, -26)

        self.skip_input: bool = True

        if save_data:
            self.load_from_save(save_data, pos)

    def import_assets(self) -> None:
        """Wczytuje grafiki: down_0-3, left_0-3, right_0-3, up_0-3"""
        path = os.path.join('assets', 'player')

        self.animations: Dict[str, List] = {
            'up': [],
            'down': [],
            'left': [],
            'right': [],
        }

        for animation_type in self.animations.keys():
            for i in range(4):
                file_name = f'{animation_type}_{i}.png'
                full_path = os.path.join(path, file_name)

                img = pygame.image.load(full_path).convert_alpha()
                img = pygame.transform.scale(
                    img, (config.PLAYER_SIZE, config.PLAYER_SIZE)
                )
                self.animations[animation_type].append(img)

        self.attack_spirites: Dict[str, pygame.Surface] = {}
        for direction in ['up', 'down', 'left', 'right']:
            file_name = f'attack_{direction}.png'
            full_path = os.path.join(path, file_name)
            try:
                img = pygame.image.load(full_path).convert_alpha()
                img = pygame.transform.scale(
                    img, (config.PLAYER_SIZE, config.PLAYER_SIZE)
                )
                self.attack_spirites[direction] = img
            except FileNotFoundError:
                if self.animations[direction]:
                    self.attack_spirites[direction] = self.animations[direction][0]
                else:
                    surf = pygame.Surface((config.PLAYER_SIZE, config.PLAYER_SIZE))
                    surf.fill('white')
                    self.attack_spirites[direction] = surf

        sfx_path = os.path.join('assets', 'sfx', 'walking_1.wav')
        try:
            self.step_sound: Optional[pygame.mixer.Sound] = pygame.mixer.Sound(
                sfx_path
            )
            self.step_sound.set_volume(config.SFX_VOLUME)
        except FileNotFoundError:
            print("Nie znaleziono pliku dźwiękowego: walking_1.wav")
            self.step_sound = None

        self.attack_sound = pygame.mixer.Sound(
            os.path.join('assets', 'sfx', 'attack.mp3')
        )
        self.attack_sound.set_volume(config.SFX_VOLUME)
        self.attack_sound_channel = pygame.mixer.Channel(0)

        self.level_up_sound = pygame.mixer.Sound(
            os.path.join('assets', 'sfx', 'next_level.mp3')
        )
        self.level_up_sound.set_volume(config.SFX_VOLUME)

    def load_from_save(
        self, save_data: Dict[str, Any], default_pos: tuple
    ) -> None:
        """Ladowanie stanu gracza z pliku zapisu"""
        self.level = save_data.get('level', 1)
        self.xp = save_data.get('xp', 0)
        self.xp_to_next_level = save_data.get('xp_to_next_level', 100)
        self.health = save_data.get('health', self.max_health)
        self.max_health = save_data.get('max_health', 100)
        self.energy = save_data.get('energy', self.max_energy)
        self.max_energy = save_data.get('max_energy', 100)

        pos_data = save_data.get('position', None)
        if pos_data:
            pos = (
                pos_data.get('x', default_pos[0]),
                pos_data.get('y', default_pos[1]),
            )
            self.rect = self.image.get_rect(topleft=pos)
            self.hitbox = self.rect.inflate(-20, -26)
        else:
            self.rect = self.image.get_rect(topleft=default_pos)
            self.hitbox = self.rect.inflate(-20, -26)

    def input(self) -> None:
        '''Obsluga poruszania sie postaci'''
        if self.skip_input:
            self.skip_input = False
            return

        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()

        if keys[pygame.K_w]:
            self.direction.y = -1
            self.status = 'up'
        elif keys[pygame.K_s]:
            self.direction.y = 1
            self.status = 'down'
        else:
            self.direction.y = 0

        if keys[pygame.K_a]:
            self.direction.x = -1
            self.status = 'left'
        elif keys[pygame.K_d]:
            self.direction.x = 1
            self.status = 'right'
        else:
            self.direction.x = 0

        if keys[pygame.K_LSHIFT] and self.energy > 0:
            self.speed = config.PLAYER_SPRINT_SPEED
            self.animation_speed = self.sprint_animation_speed
            self.energy -= self.energy_drain_rate

            if self.energy < 0:
                self.energy = 0
                self.speed = config.PLAYER_SPEED
                self.animation_speed = self.walk_animation_speed

        else:
            self.speed = config.PLAYER_SPEED
            self.animation_speed = self.walk_animation_speed
            if self.energy < self.max_energy:
                self.energy += self.energy_recover_rate

                if self.energy > self.max_energy:
                    self.energy = self.max_energy

        if mouse[0] and self.can_shoot:
            self.create_bullet()
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

            self.is_attacking = True
            self.attack_time = pygame.time.get_ticks()

        if mouse[2] and self.can_power_shoot and self.energy >= 30:
            self.create_powerful_shot()
            self.energy -= 30
            self.can_power_shoot = False
            self.power_shoot_time = pygame.time.get_ticks()

            self.is_attacking = True
            self.attack_time = pygame.time.get_ticks()

    def create_bullet(self) -> None:
        """Oblicza kierunek strzału i tworzy pocisk"""
        mouse_pos = pygame.mouse.get_pos()

        player_screen_pos = pygame.math.Vector2(
            config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2
        )
        direction = pygame.math.Vector2(mouse_pos) - player_screen_pos

        if direction.magnitude() > 0:
            direction = direction.normalize()

        Projectile(
            self.rect.center, direction, [self.sprite_groups[0], self.bullet_group]
        )

        self.attack_sound_channel.play(self.attack_sound)

    def create_powerful_shot(self) -> None:
        """Tworzy wzmocniony pocisk"""
        mouse_pos = pygame.mouse.get_pos()
        player_screen_pos = pygame.math.Vector2(
            config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2
        )

        direction = pygame.math.Vector2(mouse_pos) - player_screen_pos

        if direction.magnitude() > 0:
            direction = direction.normalize()

        Projectile(
            self.rect.center,
            direction,
            [self.sprite_groups[0], self.bullet_group],
            type='player',
            power=2,
        )

        self.attack_sound_channel.play(self.attack_sound)

    def cooldown_handler(self) -> None:
        """Odlicza czas do następnego strzału"""
        current_time = pygame.time.get_ticks()
        if not self.can_shoot:
            if current_time - self.shoot_time >= self.cooldown:
                self.can_shoot = True

        if not self.can_power_shoot:
            if (
                current_time - self.power_shoot_time >= self.power_shoot_cooldown
            ):
                self.can_power_shoot = True

    def play_step_sfx(self) -> None:
        """Odtwarza dźwięk kroku co określony czas, jeśli gracz się rusza"""
        if self.direction.magnitude() != 0:
            current_time = pygame.time.get_ticks()

            if current_time - self.step_timer > self.step_delay:
                if self.step_sound:
                    self.step_sound.play()
                self.step_timer = current_time

    def gain_xp(self, amount: int):
        """Zwieksza ilosc xp"""
        self.xp += amount
        print(f"zdobyl {amount} xp")

        while self.xp >= self.xp_to_next_level:
            self.level_up()

    def level_up(self) -> None:
        """Obsluga awansu bohatera na wyzszy poziom"""
        self.level += 1

        self.xp -= self.xp_to_next_level
        self.xp_to_next_level = int(self.xp_to_next_level * 1.75)

        self.max_health += 50
        self.max_energy += 10

        self.health = self.max_health
        self.energy = self.max_energy

        self.level_up_sound.play()


    def animate(self) -> None:
        """Obluga animacji gracza"""
        current_time = pygame.time.get_ticks()
        if self.is_attacking:
            if (
                current_time - self.attack_time
                < config.PLAYER_ATTACK_ANIMATION_DURATION
            ):
                self.image = self.attack_spirites[self.status]
            else:
                self.is_attacking = False

        animation = self.animations[self.status]
        if self.direction.magnitude() != 0:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(animation):
                self.frame_index = 0
        else:
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]

        if self.vulnerable:
            self.image.set_alpha(255)
        else:
            self.image.set_alpha(150)

    def move(self) -> None:
        """Poruszanie fracza i kolizje ze scianami"""
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * self.speed
        self.collision('horizontal')

        self.hitbox.y += self.direction.y * self.speed
        self.collision('vertical')

        self.rect.center = self.hitbox.center

    def invincibility_timer(self) -> None:
        """Zarzadzanie niesmietenelnoscia po otrzymaniu obrazen"""
        if not self.vulnerable:
            current_time = pygame.time.get_ticks()
            if (
                current_time - self.hurt_time >= self.invincibility_duration
            ):
                self.vulnerable = True

    def take_damage(self, amount: int) -> None:
        """Otrzymanie obrazen przez gracza"""
        if self.vulnerable:
            self.health -= amount
            self.vulnerable = False
            self.hurt_time = pygame.time.get_ticks()

            print(f"Otrzymano {amount} obrazen! HP: {self.health}")
            if self.health <= 0:
                print("GAME OVER")

    def collision(self, direction: str) -> None:
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):

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


    def update(self) -> None:
        self.input()
        self.play_step_sfx()
        self.animate()
        self.cooldown_handler()
        self.move()
        self.invincibility_timer()