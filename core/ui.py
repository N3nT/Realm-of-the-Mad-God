import os

import pygame

import config
from core.saveManager import SaveManager


class Button:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        font: pygame.font.Font,
        text_color: str = 'white',
        button_color: str = '#333333',
        hover_color: str = '#555555',
    ) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.text_color = text_color
        self.button_color = button_color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface: pygame.Surface) -> None:
        color = self.hover_color if self.is_hovered else self.button_color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, 'white', self.rect, 2)

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def update(self, mouse_pos: tuple) -> None:
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event: pygame.event.Event) -> bool:
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.is_hovered
        )

class ImageButton:
    def __init__(
        self, x: int, y: int, normal_image_path: str, hover_image_path: str
    ) -> None:
        self.normal_image = pygame.image.load(normal_image_path).convert_alpha()
        self.hover_image = pygame.image.load(hover_image_path).convert_alpha()
        self.rect = self.normal_image.get_rect(topleft=(x, y))
        self.is_hovered = False

    def draw(self, surface: pygame.Surface) -> None:
        image = self.hover_image if self.is_hovered else self.normal_image
        surface.blit(image, self.rect)

    def update(self, mouse_pos: tuple) -> None:
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event: pygame.event.Event) -> bool:
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.is_hovered
        )

class UI:
    def __init__(self) -> None:
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, config.UI_FONT_SIZE)

        path = os.path.join("assets", "ui", 'ui.png')
        self.ui_image = pygame.image.load(path).convert_alpha()
        self.ui_image = pygame.transform.scale(self.ui_image, (250, 100))
        self.ui_rect = self.ui_image.get_rect(
            midbottom=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT - 10)
        )

        start_path = os.path.join("assets", "ui", 'start.png')
        start_image_original = pygame.image.load(start_path).convert_alpha()
        self.start_image = pygame.transform.scale(
            start_image_original, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        )
        self.start_rect = self.start_image.get_rect(topleft=(0, 0))

        end_path = os.path.join("assets", "ui", 'end.png')
        end_image_original = pygame.image.load(end_path).convert_alpha()
        self.end_image = pygame.transform.scale(
            end_image_original, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        )
        self.end_rect = self.end_image.get_rect(topleft=(0, 0))

        self.hp_bar_start_pos = (42, 9)
        self.hp_bar_size = (200, 13)

        self.energy_bar_start_pos = (42, 45)
        self.energy_bar_size = (200, 13)

        self.xp_bar_start_pos = (42, 79)
        self.xp_bar_size = (200, 13)

        play_image_path = os.path.join('assets', 'ui', 'play.png')
        play_hover_path = os.path.join('assets', 'ui', 'play_hover.png')
        exit_image_path = os.path.join('assets', 'ui', 'exit.png')
        exit_hover_path = os.path.join('assets', 'ui', 'exit_hover.png')
        continue_image_path = os.path.join('assets', 'ui', 'continue.png')
        continue_hover_path = os.path.join('assets', 'ui', 'continue_hover.png')

        play_img = pygame.image.load(play_image_path).convert_alpha()
        play_hover_img = pygame.image.load(play_hover_path).convert_alpha()
        exit_img = pygame.image.load(exit_image_path).convert_alpha()
        exit_hover_img = pygame.image.load(exit_hover_path).convert_alpha()
        continue_img = pygame.image.load(continue_image_path).convert_alpha()
        continue_hover_img = pygame.image.load(continue_hover_path).convert_alpha()

        scale_factor = 0.5
        play_width = int(play_img.get_width() * scale_factor)
        play_height = int(play_img.get_height() * scale_factor)

        play_img = pygame.transform.scale(play_img, (play_width, play_height))
        play_hover_img = pygame.transform.scale(play_hover_img, (play_width, play_height))
        exit_img = pygame.transform.scale(exit_img, (play_width, play_height))
        exit_hover_img = pygame.transform.scale(exit_hover_img, (play_width, play_height))
        continue_img = pygame.transform.scale(continue_img, (play_width, play_height))
        continue_hover_img = pygame.transform.scale(
            continue_hover_img, (play_width, play_height)
        )

        button_spacing = 20
        center_x = config.SCREEN_WIDTH // 2 - play_width // 2

        total_height = (play_height * 3) + (button_spacing * 2)
        start_y = (config.SCREEN_HEIGHT // 2) - (total_height // 2) + 100

        continue_x = center_x
        continue_y = start_y

        play_x = center_x
        play_y = start_y + play_height + button_spacing

        exit_x = center_x
        exit_y = start_y + (play_height * 2) + (button_spacing * 2)

        self.continue_button = ImageButton(
            continue_x, continue_y, continue_image_path, continue_hover_path
        )
        self.continue_button.normal_image = continue_img
        self.continue_button.hover_image = continue_hover_img
        self.continue_button.rect = continue_img.get_rect(topleft=(continue_x, continue_y))

        self.play_button = ImageButton(play_x, play_y, play_image_path, play_hover_path)
        self.play_button.normal_image = play_img
        self.play_button.hover_image = play_hover_img
        self.play_button.rect = play_img.get_rect(topleft=(play_x, play_y))

        self.exit_button = ImageButton(exit_x, exit_y, exit_image_path, exit_hover_path)
        self.exit_button.normal_image = exit_img
        self.exit_button.hover_image = exit_hover_img
        self.exit_button.rect = exit_img.get_rect(topleft=(exit_x, exit_y))

    def show_bar(
        self, current: float, max_amount: float, start_pos: tuple, size: tuple, color: str
    ) -> None:
        x = self.ui_rect.x + start_pos[0]
        y = self.ui_rect.y + start_pos[1]

        ratio = current / max_amount
        current_width = size[0] * ratio

        bar_rect = pygame.Rect(x, y, current_width, size[1])

        if current_width > 0:
            pygame.draw.rect(self.display_surface, color, bar_rect)

    def display(self, player) -> None:
        self.display_surface.blit(self.ui_image, self.ui_rect)

        self.show_bar(
            player.health,
            player.max_health,
            self.hp_bar_start_pos,
            self.hp_bar_size,
            config.HEALTH_COLOR,
        )

        self.show_bar(
            player.energy,
            player.max_energy,
            self.energy_bar_start_pos,
            self.energy_bar_size,
            config.ENERGY_COLOR,
        )

        self.show_bar(
            player.xp,
            player.xp_to_next_level,
            self.xp_bar_start_pos,
            self.xp_bar_size,
            config.XP_COLOR,
        )

    def draw_text(
        self, text: str, font: pygame.font.Font, color: str, pos_x: int, pos_y: int, align: str = "center"
    ) -> None:
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect()

        if align == "center":
            text_rect.center = (pos_x, pos_y)
        elif align == "topleft":
            text_rect.topleft = (pos_x, pos_y)

        self.display_surface.blit(text_surf, text_rect)

    def show_menu(self) -> None:
        self.display_surface.blit(self.start_image, self.start_rect)

        mouse_pos = pygame.mouse.get_pos()
        self.play_button.update(mouse_pos)
        self.exit_button.update(mouse_pos)

        has_save = SaveManager.has_save()
        if has_save:
            self.continue_button.update(mouse_pos)
            self.continue_button.draw(self.display_surface)

        self.play_button.draw(self.display_surface)

        self.exit_button.draw(self.display_surface)

    def show_game_over(self, final_time: int, level: int, kill_stats: dict) -> None:
        self.display_surface.blit(self.end_image, self.end_rect)

        end_font = pygame.font.Font(None, 32)
        end_font_small = pygame.font.Font(None, 24)

        minutes = final_time // 60000
        seconds = (final_time % 60000) // 1000
        time_str = f"Czas przetrwania: {minutes:02}:{seconds:02}"

        frame_left_margin = 450
        frame_top_margin = 240
        line_spacing = 35

        self.draw_text(
            time_str, end_font, 'white', frame_left_margin, frame_top_margin, align="topleft"
        )

        self.draw_text(
            f"Poziom: {level}",
            end_font,
            'yellow',
            frame_left_margin,
            frame_top_margin + line_spacing,
            align="topleft",
        )

        enemies_start_y = frame_top_margin + line_spacing * 2 + 20
        self.draw_text(
            "Pokonani Wrogowie:",
            end_font_small,
            'white',
            frame_left_margin,
            enemies_start_y,
            align="topleft",
        )

        y_offset = enemies_start_y + line_spacing
        for name, count in kill_stats.items():
            self.draw_text(
                f"{name.capitalize()}: {count}",
                end_font_small,
                'gray',
                frame_left_margin,
                y_offset,
                align="topleft",
            )
            y_offset += 28

        self.draw_text(
            "Wcisnij R aby zagrać ponownie",
            end_font_small,
            'white',
            config.SCREEN_WIDTH // 2,
            580,
            align="center",
        )