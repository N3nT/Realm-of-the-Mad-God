import pygame
import os
import config

class UI:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, config.UI_FONT_SIZE)

        path = os.path.join("assets", "ui", 'ui.png')
        self.ui_image = pygame.image.load(path).convert_alpha()
        self.ui_image = pygame.transform.scale(self.ui_image, (250, 100))
        self.ui_rect = self.ui_image.get_rect(midbottom=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT - 10))

        self.hp_bar_start_pos = (42, 9)
        self.hp_bar_size = (200, 13)

        self.energy_bar_start_pos = (42, 45)
        self.energy_bar_size = (200, 13)

        self.xp_bar_start_pos = (42, 79)
        self.xp_bar_size = (200, 13)

    def show_bar(self, current, max_amount, start_pos, size, color):

        x = self.ui_rect.x + start_pos[0]
        y = self.ui_rect.y + start_pos[1]


        ratio = current / max_amount
        current_width = size[0] * ratio


        bar_rect = pygame.Rect(x, y, current_width, size[1])


        if current_width > 0:
            pygame.draw.rect(self.display_surface, color, bar_rect)

    def display(self, player):

        self.display_surface.blit(self.ui_image, self.ui_rect)


        self.show_bar(player.health, player.max_health,
        self.hp_bar_start_pos, self.hp_bar_size, config.HEALTH_COLOR)


        self.show_bar(player.energy, player.max_energy,
        self.energy_bar_start_pos, self.energy_bar_size, config.ENERGY_COLOR)

        self.show_bar(player.xp, player.xp_to_next_level, self.xp_bar_start_pos, self.xp_bar_size, config.XP_COLOR)
