import pygame
import sys

# --- INICJALIZACJA ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Menu w Pygame")

# --- KOLORY I CZCIONKI ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
GREEN = (0, 255, 0)

# Używamy domyślnej czcionki systemowej lub wczytujemy własną
FONT = pygame.font.SysFont("arial", 40)


# --- KLASA PRZYCISKU ---
class Button:
    def __init__(self, text, x, y, width, height, base_color, hover_color):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.base_color = base_color
        self.hover_color = hover_color
        self.current_color = base_color

        # Renderowanie tekstu
        self.text_surf = FONT.render(self.text, True, BLACK)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def update(self, mouse_pos):
        # Zmiana koloru po najechaniu myszką
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
        else:
            self.current_color = self.base_color

    def draw(self, screen):
        # Rysowanie prostokąta przycisku
        pygame.draw.rect(screen, self.current_color, self.rect)
        # Rysowanie ramki (opcjonalne)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        # Rysowanie tekstu
        screen.blit(self.text_surf, self.text_rect)

    def is_clicked(self, mouse_pos, event):
        # Sprawdzenie czy przycisk został kliknięty
        if self.rect.collidepoint(mouse_pos) and event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Lewy przycisk myszy
                return True
        return False


# --- FUNKCJA GRY (WŁAŚCIWA ROZGRYWKA) ---
def play_game():
    while True:
        SCREEN.fill(BLACK)

        # Tekst w grze
        play_text = FONT.render("JESTEŚ W GRZE! (ESC by wrócić)", True, WHITE)
        SCREEN.blit(play_text, (150, 250))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return  # Powrót do menu (wyjście z funkcji)

        pygame.display.update()


# --- FUNKCJA GŁÓWNA (MENU) ---
def main_menu():
    # Tworzenie przycisków
    play_button = Button("GRAJ", 300, 200, 200, 80, GRAY, GREEN)
    quit_button = Button("WYJŚCIE", 300, 350, 200, 80, GRAY, (255, 100, 100))

    run = True
    while run:
        SCREEN.fill(WHITE)
        mouse_pos = pygame.mouse.get_pos()

        # Tytuł Menu
        title_text = FONT.render("MENU GŁÓWNE", True, BLACK)
        SCREEN.blit(title_text, (260, 100))

        # Obsługa zdarzeń
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Logika przycisków
            if play_button.is_clicked(mouse_pos, event):
                play_game()  # Uruchomienie pętli gry

            if quit_button.is_clicked(mouse_pos, event):
                pygame.quit()
                sys.exit()

        # Rysowanie przycisków
        for button in [play_button, quit_button]:
            button.update(mouse_pos)
            button.draw(SCREEN)

        pygame.display.update()


# Uruchomienie programu
if __name__ == "__main__":
    main_menu()