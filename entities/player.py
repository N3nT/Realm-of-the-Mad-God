import pygame
import config
import os
from entities.projectile import Projectile

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, create_bullet_group):
        super().__init__(groups)

        self.sprite_groups = groups
        self.bullet_group = create_bullet_group

        self.vulnerable = True
        self.hurt_time = 0
        self.invincibility_duration = 500

        self.health = 1000
        self.max_health = 1000

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

        self.step_timer = 0
        self.step_delay = 350

        self.energy = 100
        self.max_energy = 100
        self.energy_drain_rate = 0.5
        self.energy_recover_rate = 0.05

        self.xp = 0
        self.level = 1
        self.xp_to_next_level = 100

    def import_assets(self):
        """Wczytuje grafiki: down_0-3, left_0-3, right_0-3, up_0-3"""
        path = os.path.join('assets', 'player')

        self.animations = {'up': [], 'down': [], 'left': [], 'right': []}

        for animation_type in self.animations.keys():
            for i in range(4):
                file_name = f'{animation_type}_{i}.png'
                full_path = os.path.join(path, file_name)

                img = pygame.image.load(full_path).convert_alpha()
                img = pygame.transform.scale(img, (config.PLAYER_SIZE, config.PLAYER_SIZE))
                self.animations[animation_type].append(img)

        self.attack_spirites = {}
        for dir in ['up', 'down', 'left', 'right']:
            file_name = f'attack_{dir}.png'
            full_path = os.path.join(path, file_name)
            try:
                img = pygame.image.load(full_path).convert_alpha()
                img = pygame.transform.scale(img, (config.PLAYER_SIZE, config.PLAYER_SIZE))
                self.attack_spirites[dir] = img
            except FileNotFoundError:
                # Jeśli brakuje pliku ataku, użyjemy 1. klatki zwykłego chodzenia jako zamiennika
                if self.animations[dir]:
                    self.attack_sprites[dir] = self.animations[dir][0]
                else:
                    surf = pygame.Surface((config.PLAYER_SIZE, config.PLAYER_SIZE))
                    surf.fill('white')
                    self.attack_sprites[dir] = surf

        sfx_path = os.path.join('assets', 'sfx', 'walking_1.wav')
        try:
            self.step_sound = pygame.mixer.Sound(sfx_path)
            self.step_sound.set_volume(config.SFX_VOLUME)
        except FileNotFoundError:
            print("Nie znaleziono pliku dźwiękowego: walking_1.wav")
            self.step_sound = None

        self.attack_sound = pygame.mixer.Sound(os.path.join('assets', 'sfx', 'attack.mp3'))
        self.attack_sound.set_volume(config.SFX_VOLUME)

    def input(self):
        '''Obsluga poruszania sie postaci'''
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

    def create_bullet(self):
        """Oblicza kierunek strzału i tworzy pocisk"""
        mouse_pos = pygame.mouse.get_pos()
        # Gracz jest zawsze na środku ekranu, więc odejmujemy środek ekranu od pozycji myszy
        player_screen_pos = pygame.math.Vector2(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)

        # Obliczamy wektor kierunku
        direction = (pygame.math.Vector2(mouse_pos) - player_screen_pos)

        # Normalizujemy (żeby pocisk leciał ze stałą prędkością, a nie szybciej gdy mysz jest daleko)
        if direction.magnitude() > 0:
            direction = direction.normalize()

        # Tworzymy pocisk w miejscu, gdzie stoi gracz
        Projectile(self.rect.center, direction, [self.sprite_groups[0], self.bullet_group])

        self.attack_sound.play()

    def cooldown_handler(self):
        """Odlicza czas do następnego strzału"""
        current_time = pygame.time.get_ticks()
        if not self.can_shoot:
            if current_time - self.shoot_time >= self.cooldown:
                self.can_shoot = True

    def play_step_sfx(self):
        """Odtwarza dźwięk kroku co określony czas, jeśli gracz się rusza"""
        # Sprawdzamy czy gracz się rusza
        if self.direction.magnitude() != 0:
            current_time = pygame.time.get_ticks()

            # Jeśli minął odpowiedni czas od ostatniego kroku
            if current_time - self.step_timer > self.step_delay:
                if self.step_sound:
                    self.step_sound.play()  # Odtwórz dźwięk
                self.step_timer = current_time  # Zresetuj timer

    def gain_xp(self, amount):
        self.xp += amount
        print(f"zdobyl {amount} xp")

        while self.xp >= self.xp_to_next_level:
            self.level_up()

    def level_up(self):
        self.level += 1

        self.xp -= self.xp_to_next_level
        self.xp_to_next_level = int(self.xp_to_next_level * 1.75)

        self.max_health += 50
        self.max_energy += 10

        self.health = self.max_health
        self.energy = self.max_energy


    def animate(self):
        # Animacje ataku
        current_time = pygame.time.get_ticks()
        if self.is_attacking:
            if current_time - self.attack_time < config.PLAYER_ATTACK_ANIMATION_DURATION:
                self.image = self.attack_spirites[self.status]
                return
            else:
                # Jeśli czas minął, wyłącz flagę ataku
                self.is_attacking = False

        # Animacje chodzenia
        animation = self.animations[self.status]
        if self.direction.magnitude() != 0:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(animation):
                self.frame_index = 0
        else:
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]

    def move(self):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.rect.center += self.direction * self.speed

    def invincibility_timer(self):
        if not self.vulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.hurt_time >= self.invincibility_duration:
                self.vulnerable = True
                # Opcjonalnie: przywróć normalną grafikę (jeśli robiłbyś miganie)
                self.image.set_alpha(255)  # Pełna widoczność

    def take_damage(self, amount):
        if self.vulnerable:
            self.health -= amount
            self.vulnerable = False
            self.hurt_time = pygame.time.get_ticks()

            self.image.set_alpha(150)

            print(f"Otrzymano {amount} obrażeń! HP: {self.health}")
            if self.health <= 0:
                print("GAME OVER")

    def update(self):
        self.input()
        self.play_step_sfx()
        self.animate()
        self.cooldown_handler()
        self.move()
        self.invincibility_timer()