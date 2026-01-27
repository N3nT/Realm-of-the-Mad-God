import os.path
import random
import sys
from typing import Dict, Tuple

import pygame

import config
from core.mapManager import MapManager
from core.saveManager import SaveManager
from core.ui import UI
from core.camera import CameraGroup
from entities.factory import MainFactory
from entities.player import Player


def collide_hitbox(sprite1, sprite2) -> bool:
    return sprite1.hitbox.colliderect(sprite2.hitbox)


class Game:
    """Główna klasa gry"""
    def __init__(self) -> None:
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode(config.SCREEN_SIZE)
        icon_surface = pygame.image.load(config.ICON_PATH)
        pygame.display.set_icon(icon_surface)
        pygame.display.set_caption("Real of the Mad God Clone")

        cursor_image = pygame.image.load(
            os.path.join('assets', 'ui', 'cursor.png')
        )
        cursor_image = pygame.transform.scale(cursor_image, (32, 32))
        cursor = pygame.cursors.Cursor((0, 0), cursor_image)
        pygame.mouse.set_cursor(cursor)

        self.clock = pygame.time.Clock()

        self.all_sprites = CameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()

        self.factory = MainFactory()

        self.setup_music()
        self.setup_player()
        self.ui = UI()
        self.map_manager = MapManager(
            self.all_sprites,
            self.obstacle_sprites,
            self.spawn_enemy_at_pos,
            self.player,
        )

        self.font = pygame.font.Font(
            os.path.join('assets', 'DungeonFont.ttf'), 24
        )
        self.game_state = 'menu'

        self.start_time = 0
        self.final_time = 0
        self.elapsed_time_on_load = 0
        self.kill_stats: Dict[str, int] = {}

    def setup_player(self) -> None:
        """Tworzenie gracza i ładowanie zapisu gry"""
        save_data = SaveManager.load_game()
        if save_data:
            self.elapsed_time_on_load = save_data.get('game_time', 0)
        self.player = Player(
            (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2),
            [self.all_sprites],
            self.obstacle_sprites,
            self.player_bullets,
            save_data=save_data,
        )

    def setup_music(self) -> None:
        """Inicjalizacja muzyki w tle"""
        music_folder = os.path.join('assets', 'music')
        self.playlist = []

        if os.path.exists(music_folder):
            for file in os.listdir(music_folder):
                if file.endswith('.mp3') or file.endswith('.ogg'):
                    self.playlist.append(os.path.join(music_folder, file))

        self.current_track = 0

        if self.playlist:
            self.play_music()
    
    def play_music(self) -> None:
        """Odtwarzanie muzyki z playlisty"""
        if self.playlist:
            try:
                pygame.mixer.music.load(self.playlist[self.current_track])
                pygame.mixer.music.set_volume(config.MUSIC_VOLUME)
                pygame.mixer.music.play()

                self.MUSIC_END = pygame.USEREVENT + 1
                pygame.mixer.music.set_endevent(self.MUSIC_END)
            except pygame.error:
                print("Błąd odtwarzania pliku muzycznego")

    def update_playlist(self) -> None:
        """Aktualizacja playlisty muzycznej"""
        self.current_track += 1
        if self.current_track >= len(self.playlist):
            self.current_track = 0
        self.play_music()

    def setup_enemies(self) -> None:
        """Tworzenie enemy"""
        current_level_factory = MainFactory()
        current_level_factory.create_ghost(
            (600, 100),
            [self.all_sprites, self.enemy_group],
            self.player,
            self.enemy_bullets,
            self.obstacle_sprites,
        )
        current_level_factory.create_politician(
            (500, 150),
            [self.all_sprites, self.enemy_group],
            self.player,
            self.player_bullets,
            self.obstacle_sprites,
        )
        current_level_factory.create_butcher(
            (400, 150),
            [self.all_sprites, self.enemy_group],
            self.player,
            self.player_bullets,
            self.obstacle_sprites,
        )
        current_level_factory.create_bat(
            (300, 150),
            [self.all_sprites, self.enemy_group],
            self.player,
            self.player_bullets,
            self.obstacle_sprites,
        )

    def check_collision(self) -> None:
        """Sprawdzanie kolizji między obiektami"""
        for sprite in list(self.player_bullets):
            if hasattr(sprite, 'sprite_type') and sprite.sprite_type in [
                'wall',
                'enemy',
            ]:
                print(
                    f"ERROR: Found {sprite.sprite_type} in player_bullets group! "
                    "Removing it."
                )
                sprite.kill()

        hits = pygame.sprite.groupcollide(
            self.enemy_group, self.player_bullets, False, False, collide_hitbox
        )
        if hits:
            bullets_to_remove = []
            for enemy in hits:
                bullets = hits[enemy]
                valid_bullets = [
                    b
                    for b in bullets
                    if hasattr(b, 'type') and b.type == 'player'
                ]
                if valid_bullets:
                    was_alive = enemy.health > 0
                    for bullet in valid_bullets:
                        is_piercing = getattr(bullet, 'power', 1) == 2
                        enemy_id = id(enemy)
                        if is_piercing:
                            if enemy_id not in bullet.hit_enemies:
                                damage = 20
                                enemy.take_damage(damage)
                                bullet.hit_enemies.add(enemy_id)
                        else:
                            damage = getattr(bullet, 'damage', 10)
                            enemy.take_damage(damage)
                            bullets_to_remove.append(bullet)

                    if was_alive and enemy.health <= 0:
                        name = getattr(enemy, 'enemy_name', 'unknown')

                        try:
                            self.kill_stats[name] += 1
                        except KeyError:
                            self.kill_stats[name] = 1

                        print(self.kill_stats)
                        self.player.gain_xp(enemy.xp_reward)

            for bullet in bullets_to_remove:
                bullet.kill()

        hits = pygame.sprite.spritecollide(
            self.player, self.enemy_bullets, True
        )
        if hits:
            for bullet in hits:
                self.player.health -= 10
                print(f"HP Gracza: {self.player.health}")
                self.player.take_damage(10)

        pygame.sprite.groupcollide(
            self.player_bullets, self.obstacle_sprites, True, False, collide_hitbox
        )
        if hasattr(self, 'enemy_bullets'):
            pygame.sprite.groupcollide(
                self.enemy_bullets, self.obstacle_sprites, True, False
            )

        body_hits = pygame.sprite.spritecollide(
            self.player, self.enemy_group, False
        )
        if body_hits:
            self.player.take_damage(20)

        if self.player.health <= 0:
            self.game_state = 'game_over'
            self.final_time = pygame.time.get_ticks() - self.start_time
            SaveManager.delete_save()

    def spawn_enemy_at_pos(self, pos: Tuple[float, float]) -> None:
        """Tworzenie przeciwnika w określonej pozycji"""
        max_enemies = 120

        if self.player and hasattr(self.player, 'level'):
            max_enemies = 50 + (self.player.level * 2)
            max_enemies = min(max_enemies, 200)

        if len(self.enemy_group) >= max_enemies:
            return

        min_spawn_distance = 150
        spawn_pos = pygame.math.Vector2(pos)

        for enemy in self.enemy_group:
            enemy_pos = pygame.math.Vector2(enemy.rect.center)
            distance = (spawn_pos - enemy_pos).magnitude()
            if distance < min_spawn_distance:
                return

        enemy_type = random.choice(
            ['ghost', 'butcher', 'politician', 'bat', 'skeleton',
             'black_magic', 'mage']
        )
        groups = [self.all_sprites, self.enemy_group]
        getattr(self.factory, f"create_{enemy_type}")(
            pos, groups, self.player, self.enemy_bullets, self.obstacle_sprites
        )

    def reset_game(self) -> None:
        """Resetowanie stanu gry"""
        self.all_sprites.empty()
        self.obstacle_sprites.empty()
        self.player_bullets.empty()
        self.enemy_group.empty()
        self.enemy_bullets.empty()

        self.kill_stats = {k: 0 for k in self.kill_stats}
        self.start_time = pygame.time.get_ticks()
        self.elapsed_time_on_load = 0

        SaveManager.delete_save()

        self.setup_player()
        self.player.level = 1
        self.map_manager = MapManager(
            self.all_sprites,
            self.obstacle_sprites,
            self.spawn_enemy_at_pos,
            self.player,
        )

    def run(self) -> None:
        """Główna pętla gry"""
        while True:
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if hasattr(self, 'MUSIC_END') and event.type == self.MUSIC_END:
                    self.update_playlist()

            if self.game_state == 'menu':
                self.ui.show_menu()

                for event in events:
                    if (
                        SaveManager.has_save()
                        and self.ui.continue_button.is_clicked(event)
                    ):
                        self.game_state = 'game'
                    elif self.ui.play_button.is_clicked(event):
                        self.reset_game()
                        self.game_state = 'game'
                    elif self.ui.exit_button.is_clicked(event):
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.reset_game()
                            self.game_state = 'game'
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()

            elif self.game_state == 'game':
                self.screen.fill('black')

                if self.start_time == 0:
                    self.start_time = pygame.time.get_ticks()
                current_time = pygame.time.get_ticks()
                self.final_time = (
                    (current_time - self.start_time) + self.elapsed_time_on_load
                )

                for event in events:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        SaveManager.save_game(self.player, self.final_time)
                        self.game_state = 'menu'

                if self.player.rect:
                    self.map_manager.update(self.player.rect.center)

                for sprite in self.all_sprites:
                    if (
                        hasattr(sprite, 'sprite_type')
                        and sprite.sprite_type == 'enemy'
                    ):
                        sprite.update(self.enemy_group)
                    else:
                        sprite.update()

                self.check_collision()

                self.all_sprites.custom_draw(self.player)
                self.ui.display(self.player)

            elif self.game_state == 'game_over':
                self.ui.show_game_over(
                    self.final_time, self.player.level, self.kill_stats
                )

                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.reset_game()
                            self.game_state = 'game'
                        if event.key == pygame.K_ESCAPE:
                            self.game_state = 'menu'

            pygame.display.flip()
            self.clock.tick(config.FPS)