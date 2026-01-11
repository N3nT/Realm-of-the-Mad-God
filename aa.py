import pygame
from opensimplex import OpenSimplex  # ZMIANA: Inna biblioteka
import random

# --- KONFIGURACJA ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
TILE_SIZE = 40
CHUNK_SIZE = 8
SEED = random.randint(0, 1000)
SCALE = 0.1

gen = OpenSimplex(seed=SEED)

COLORS = {
    "deep_water": (20, 20, 150),
    "water": (30, 30, 200),
    "sand": (230, 215, 150),
    "grass": (34, 139, 34),
    "forest": (0, 100, 0),
    "mountain": (100, 100, 100),
    "snow": (240, 240, 240)
}


# --- FUNKCJE GENERUJĄCE ---

def get_biome(x, y):
    """Zwraca kolor na podstawie współrzędnych świata (x, y) używając OpenSimplex."""

    # ZMIANA: OpenSimplex używa noise2 zamiast pnoise2
    # Zwraca wartość od ok. -1 do 1
    value = gen.noise2(x * SCALE, y * SCALE)

    # Mapowanie wartości szumu na typ terenu
    if value < -0.4:
        return COLORS["deep_water"]
    elif value < -0.1:
        return COLORS["water"]
    elif value < 0.0:
        return COLORS["sand"]
    elif value < 0.35:
        return COLORS["grass"]
    elif value < 0.6:
        return COLORS["forest"]
    elif value < 0.8:
        return COLORS["mountain"]
    else:
        return COLORS["snow"]


def generate_chunk(chunk_x, chunk_y):
    surface = pygame.Surface((CHUNK_SIZE * TILE_SIZE, CHUNK_SIZE * TILE_SIZE))

    for r in range(CHUNK_SIZE):
        for c in range(CHUNK_SIZE):
            world_x = chunk_x * CHUNK_SIZE + c
            world_y = chunk_y * CHUNK_SIZE + r

            color = get_biome(world_x, world_y)

            pygame.draw.rect(surface, color,
                             (c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    return surface


# --- GŁÓWNA PĘTLA ---

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Map Generator - OpenSimplex Version")
    clock = pygame.time.Clock()

    camera_x = 0
    camera_y = 0
    speed = 10

    loaded_chunks = {}

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: camera_x -= speed
        if keys[pygame.K_RIGHT]: camera_x += speed
        if keys[pygame.K_UP]: camera_y -= speed
        if keys[pygame.K_DOWN]: camera_y += speed

        start_chunk_x = int(camera_x // (CHUNK_SIZE * TILE_SIZE))
        start_chunk_y = int(camera_y // (CHUNK_SIZE * TILE_SIZE))

        chunks_visible_x = (WINDOW_WIDTH // (CHUNK_SIZE * TILE_SIZE)) + 2
        chunks_visible_y = (WINDOW_HEIGHT // (CHUNK_SIZE * TILE_SIZE)) + 2

        screen.fill((0, 0, 0))

        for cy in range(start_chunk_y - 1, start_chunk_y + chunks_visible_y):
            for cx in range(start_chunk_x - 1, start_chunk_x + chunks_visible_x):
                coord = (cx, cy)
                if coord not in loaded_chunks:
                    loaded_chunks[coord] = generate_chunk(cx, cy)

                draw_x = cx * CHUNK_SIZE * TILE_SIZE - camera_x
                draw_y = cy * CHUNK_SIZE * TILE_SIZE - camera_y

                screen.blit(loaded_chunks[coord], (draw_x, draw_y))

        # Czyszczenie pamięci
        current_keys = list(loaded_chunks.keys())
        for key in current_keys:
            if abs(key[0] - start_chunk_x) > 10 or abs(key[1] - start_chunk_y) > 10:
                del loaded_chunks[key]

        pygame.draw.rect(screen, (255, 0, 0),
                         (WINDOW_WIDTH // 2 - 10, WINDOW_HEIGHT // 2 - 10, 20, 20))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()