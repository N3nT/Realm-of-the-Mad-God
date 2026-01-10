import pygame
import config
import os
from entities.projectile import Projectile

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)

        self.sprite_groups = groups

        self.image = pygame.Surface((config.PLAYER_SIZE, config.PLAYER_SIZE))
        self.rect = self.image.get_rect(topleft=pos)

        self.status = 'down'
        self.frame_index = 0
        self.animation_speed = 0.15

        self.import_assets()

        self.image = self.animations[self.status][self.frame_index]

        self.direction = pygame.math.Vector2()
        self.speed = config.PLAYER_SPEED

        # --- NOWE: System walki ---
        self.can_shoot = True
        self.shoot_time = 0
        self.cooldown = config.SHOOT_COOLDOWN

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

        # --- NOWE: Strzelanie (Lewy Przycisk Myszy) ---
        if mouse[0] and self.can_shoot:
            self.create_bullet()
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

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
        # Przekazujemy self.sprite_groups, żeby pocisk trafił do CameraGroup i był rysowany
        Projectile(self.rect.center, direction, self.sprite_groups)

    def cooldown_handler(self):
        """Odlicza czas do następnego strzału"""
        current_time = pygame.time.get_ticks()
        if not self.can_shoot:
            if current_time - self.shoot_time >= self.cooldown:
                self.can_shoot = True

    def animate(self):
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

    def update(self):
        self.input()
        self.animate()
        self.cooldown_handler()
        self.move()