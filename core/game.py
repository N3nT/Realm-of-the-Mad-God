import pygame
import sys
import config
from entities.player import Player


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(config.SCREEN_SIZE)
        icon_surface = pygame.image.load(config.ICON_PATH)
        pygame.display.set_icon(icon_surface)
        pygame.display.set_caption("Real of the Mad God Clone")
        self.clock = pygame.time.Clock()

        self.all_sprites = pygame.sprite.Group()
        self.setup()

    def setup(self):
        self.player = Player((config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2), [self.all_sprites])

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.all_sprites.update()
            self.screen.fill('black')
            self.all_sprites.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(config.FPS)