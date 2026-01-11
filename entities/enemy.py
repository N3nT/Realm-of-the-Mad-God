import pygame
import os

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player, enemy_name, hp, speed):
        super().__init__(groups)
        self.player = player
        self.speed = speed
        self.health = hp

        self.frame_index = 0
        self.animation_speed = 0.15
        self.enemy_name = enemy_name

        self.import_graphics(enemy_name)
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.direction = pygame.math.Vector2()


    def import_graphics(self, name):
        self.frames = []
        path = os.path.join('assets', 'enemies', name)

        for i in range(3):
            file_name = f"{name}_{i}.png"
            full_path = os.path.join(path, file_name)
            try:
                self.image = pygame.image.load(full_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (60, 60))
                self.frames.append(self.image)
            except (FileNotFoundError, TypeError):
                print(f"OSTRZEŻENIE: Nie znaleziono pliku: {full_path}")
                pass

    def move(self):
        '''Przeciwnik idzie do gracza'''
        player_vec = pygame.math.Vector2(self.player.rect.center)
        my_vec = pygame.math.Vector2(self.rect.center)

        diff = player_vec - my_vec
        dist = diff.magnitude()

        if 20 < dist < 600:  # Reaguje z odległości 600px
            self.direction = diff.normalize()
            self.rect.center += self.direction * self.speed
        else:
            self.direction = pygame.math.Vector2()

    def animate(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        orginal_img = self.frames[int(self.frame_index)]

        # Obracanie obrazka jesli postac idzie w lewo
        if self.direction.x < 0:
            self.image = pygame.transform.flip(orginal_img, True, False)
        else:
            self.image = orginal_img

    def update(self):
        self.move()
        self.animate()


class Ghost(Enemy):
    def __init__(self, pos, groups, player, enemy_name, hp, speed):
        super().__init__(pos, groups, player, enemy_name, hp, speed)

class Politician(Enemy):
    def __init__(self, pos, groups, player, enemy_name, hp, speed):
        super().__init__(pos, groups, player, enemy_name, hp, speed)

class Butcher(Enemy):
    def __init__(self, pos, groups, player, enemy_name, hp, speed):
        super().__init__(pos, groups, player, enemy_name, hp, speed)

class Bat(Enemy):
    def __init__(self, pos, groups, player, enemy_name, hp, speed):
        super().__init__(pos, groups, player, enemy_name, hp, speed)
