import os.path

import pygame
import sys
import config
from entities.player import Player

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode(config.SCREEN_SIZE)
        icon_surface = pygame.image.load(config.ICON_PATH)
        pygame.display.set_icon(icon_surface)
        pygame.display.set_caption("Real of the Mad God Clone")
        self.clock = pygame.time.Clock()

        self.all_sprites = pygame.sprite.Group()
        self.setup_music()
        self.setup_player()

    def setup_player(self):
        self.player = Player((config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2), [self.all_sprites])

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


    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if hasattr(self, 'MUSIC_END') and event.type == self.MUSIC_END:
                self.update_playlist()

            self.all_sprites.update()
            self.screen.fill('black')
            self.all_sprites.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(config.FPS)