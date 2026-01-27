import os
import pygame

class CameraGroup(pygame.sprite.Group):
    """Grupa sprite z obsługą kamery"""
    def __init__(self) -> None:
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_width() // 2
        self.half_height = self.display_surface.get_height() // 2
        self.offset = pygame.math.Vector2()

        self.floor_surf = pygame.image.load(
            os.path.join('assets', 'floor_flat.png')
        ).convert()
        self.floor_rect = self.floor_surf.get_rect()

        self.bg_width = self.floor_rect.width
        self.bg_height = self.floor_rect.height
        self.font = pygame.font.Font(
            os.path.join('assets', 'DungeonFont.ttf'), 24
        )

    def custom_draw(self, player) -> None:
        """Rysuj sprite'y z uwzględnieniem kamery"""
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        start_col = int(self.offset.x // self.bg_width)
        start_row = int(self.offset.y // self.bg_height)

        cols_visible = int(self.display_surface.get_width() // self.bg_width) + 2
        rows_visible = int(self.display_surface.get_height() // self.bg_height) + 2

        for row in range(rows_visible):
            for col in range(cols_visible):
                x = (start_col + col) * self.bg_width - self.offset.x
                y = (start_row + row) * self.bg_height - self.offset.y

                self.display_surface.blit(self.floor_surf, (x, y))

        for sprite in sorted(
            self.sprites(), key=lambda sprite: sprite.rect.centery
        ):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

            if (
                hasattr(sprite, 'xp_reward')
                and sprite.health < sprite.max_health
            ):
                bar_x = (
                    offset_pos[0]
                    + (sprite.rect.width // 2)
                    - (sprite.bar_max_width // 2)
                )
                bar_y = offset_pos[1] - 10
                ratio = sprite.health / sprite.max_health
                current_bar_width = sprite.bar_max_width * ratio
                bg_rect = pygame.Rect(
                    bar_x, bar_y, sprite.bar_max_width, sprite.bar_height
                )
                pygame.draw.rect(self.display_surface, '#111111', bg_rect)
                if current_bar_width > 0:
                    hp_rect = pygame.Rect(
                        bar_x, bar_y, current_bar_width, sprite.bar_height
                    )
                    pygame.draw.rect(self.display_surface, 'red', hp_rect)

            if sprite == player:
                level_text = f"Lvl: {player.level}"
                text_surf = self.font.render(level_text, True, 'white')

                text_rect = text_surf.get_rect(
                    centerx=offset_pos[0] + sprite.rect.width // 2,
                    bottom=offset_pos[1] - 10,
                )

                shadow_surf = self.font.render(level_text, True, 'black')
                shadow_rect = text_rect.copy()
                shadow_rect.x += 1
                shadow_rect.y += 1
                self.display_surface.blit(shadow_surf, shadow_rect)

                self.display_surface.blit(text_surf, text_rect)