import os.path

import pygame
import sys
import config
from entities.player import Player
from entities.factory import TestFactory
from core.ui import UI
from core.MapManager import MapManager
from entities.tile import Tile

def collide_hitbox(sprite1, sprite2):
    return sprite1.hitbox.colliderect(sprite2.hitbox)

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_width() // 2
        self.half_height = self.display_surface.get_height() // 2
        self.offset = pygame.math.Vector2()

        # Tło (mapa)
        self.floor_surf = pygame.image.load(os.path.join('assets', 'floor_flat.png')).convert()
        self.floor_rect = self.floor_surf.get_rect()

        self.bg_width = self.floor_rect.width
        self.bg_height = self.floor_rect.height
        self.font = pygame.font.Font(os.path.join('assets', 'DungeonFont.ttf'), 24)

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        start_col = int(self.offset.x // self.bg_width)
        start_row = int(self.offset.y // self.bg_height)

        cols_visible = int(self.display_surface.get_width() // self.bg_width) + 2
        rows_visible = int(self.display_surface.get_height() // self.bg_height) + 2

        for row in range(rows_visible):
            for col in range(cols_visible):
                # Obliczamy pozycję X i Y konkretnego kafelka w świecie
                # (start_col + col) to indeks kafelka
                x = (start_col + col) * self.bg_width - self.offset.x
                y = (start_row + row) * self.bg_height - self.offset.y

                self.display_surface.blit(self.floor_surf, (x, y))

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

            if hasattr(sprite, 'xp_reward') and sprite.health < sprite.max_health:
                bar_x = offset_pos[0] + (sprite.rect.width // 2) - (sprite.bar_max_width // 2)
                bar_y = offset_pos[1] - 10
                ratio = sprite.health / sprite.max_health
                current_bar_width = sprite.bar_max_width * ratio
                bg_rect = pygame.Rect(bar_x, bar_y, sprite.bar_max_width, sprite.bar_height)
                pygame.draw.rect(self.display_surface, '#111111', bg_rect)
                if current_bar_width > 0:
                    hp_rect = pygame.Rect(bar_x, bar_y, current_bar_width, sprite.bar_height)
                    pygame.draw.rect(self.display_surface, 'red', hp_rect)

            if sprite == player:
                level_text = f"Lvl: {player.level}"
                text_surf = self.font.render(level_text, True, 'white')

                text_rect = text_surf.get_rect(
                    centerx=offset_pos[0] + sprite.rect.width // 2,
                    bottom=offset_pos[1] - 10  # 10 px nad grafiką
                )

                shadow_surf = self.font.render(level_text, True, 'black')
                shadow_rect = text_rect.copy()
                shadow_rect.x += 1
                shadow_rect.y += 1
                self.display_surface.blit(shadow_surf, shadow_rect)

                self.display_surface.blit(text_surf, text_rect)



class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode(config.SCREEN_SIZE)
        icon_surface = pygame.image.load(config.ICON_PATH)
        pygame.display.set_icon(icon_surface)
        pygame.display.set_caption("Real of the Mad God Clone")
        self.clock = pygame.time.Clock()

        self.all_sprites = CameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()

        self.factory = TestFactory()

        self.setup_music()
        self.setup_player()
        # self.setup_enemies()
        self.ui = UI()
        self.map_manager = MapManager(self.all_sprites, self.obstacle_sprites, self.spawn_enemy_at_pos)

    def setup_player(self):
        self.player = Player((config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2), [self.all_sprites], self.obstacle_sprites,self.player_bullets)

    def setup_music(self):
        music_folder = os.path.join('assets', 'music')
        self.playlist = []

        if os.path.exists(music_folder):
            for file in os.listdir(music_folder):
                if file.endswith('.mp3') or file.endswith('.ogg'):
                    self.playlist.append(os.path.join(music_folder, file))

        self.current_track = 0

        if self.playlist:
            self.play_music()

    def setup_enemies(self):
        current_level_factory = TestFactory()
        current_level_factory.create_ghost((600, 100), [self.all_sprites, self.enemy_group], self.player, self.enemy_bullets, self.obstacle_sprites)
        current_level_factory.create_politician((500, 150), [self.all_sprites, self.enemy_group], self.player, self.player_bullets, self.obstacle_sprites)
        current_level_factory.create_butcher((400, 150), [self.all_sprites, self.enemy_group], self.player, self.player_bullets, self.obstacle_sprites)
        current_level_factory.create_bat((300, 150), [self.all_sprites, self.enemy_group], self.player, self.player_bullets, self.obstacle_sprites)

    def check_collision(self):
        hits = pygame.sprite.groupcollide(self.enemy_group, self.player_bullets, False, True)
        if hits:
            for enemy in hits:
                was_alive = enemy.health > 0
                enemy.take_damage(10)

                if was_alive and enemy.health <= 0:
                    self.player.gain_xp(enemy.xp_reward)

        hits = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
        if hits:
            for bullet in hits:
                self.player.health -= 10
                print(f"HP Gracza: {self.player.health}")
                self.player.take_damage(10)

        pygame.sprite.groupcollide(self.player_bullets, self.obstacle_sprites, True, False, collide_hitbox)
        if hasattr(self, 'enemy_bullets'):
            pygame.sprite.groupcollide(self.enemy_bullets, self.obstacle_sprites, True, False)

        body_hits = pygame.sprite.spritecollide(self.player, self.enemy_group, False)
        if body_hits:
            self.player.take_damage(20)

        if self.player.health <= 0:
            # todo przejdz widoku koncowego
            print("GAME OVER")


    def play_music(self):
        """Odtwarza bieżący utwór z playlisty"""
        if self.playlist:
            try:
                # Ładowanie i odtwarzanie
                pygame.mixer.music.load(self.playlist[self.current_track])
                pygame.mixer.music.set_volume(config.MUSIC_VOLUME)
                pygame.mixer.music.play()  # Gra raz, potem zdarzenie MUSIC_END wywoła kolejne

                # Ustawiamy zdarzenie, które wykona się, gdy muzyka się skończy
                # Dzięki temu zrobimy pętlę po playliście
                self.MUSIC_END = pygame.USEREVENT + 1
                pygame.mixer.music.set_endevent(self.MUSIC_END)
            except pygame.error:
                print("Błąd odtwarzania pliku muzycznego")

    def update_playlist(self):
        """Przełącza na następny utwór"""
        self.current_track += 1
        if self.current_track >= len(self.playlist):
            self.current_track = 0  # Zapętlenie playlisty
        self.play_music()

    def spawn_enemy_at_pos(self, pos):
        import random

        enemy_type = random.choice(['ghost', 'butcher', 'politician', 'bat'])

        groups = [self.all_sprites, self.enemy_group]

        if enemy_type == 'ghost':
            self.factory.create_ghost(
                pos,
                groups,
                self.player,
                self.enemy_bullets,
                self.obstacle_sprites
            )

        elif enemy_type == 'politician':
            self.factory.create_politician(
                pos,
                groups,
                self.player,
                self.player_bullets,
                self.obstacle_sprites
            )

        elif enemy_type == 'butcher':
            self.factory.create_butcher(
                pos,
                groups,
                self.player,
                self.player_bullets,
                self.obstacle_sprites
            )

        elif enemy_type == 'bat':
            self.factory.create_bat(
                pos,
                groups,
                self.player,
                self.player_bullets,
                self.obstacle_sprites
            )


    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if hasattr(self, 'MUSIC_END') and event.type == self.MUSIC_END:
                self.update_playlist()

            self.map_manager.update(self.player.rect.center)
            self.all_sprites.update()
            self.check_collision()
            self.screen.fill('black')
            self.all_sprites.custom_draw(self.player)
            self.ui.display(self.player)
            pygame.display.flip()
            self.clock.tick(config.FPS)