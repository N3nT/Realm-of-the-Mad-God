import os

# window setting
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

# player settings
PLAYER_SIZE = 80
PLAYER_SPEED = 5

# Ustawienia broni
BULLET_SPEED = 12 #px
BULLET_LIFETIME = 1000 #ms
SHOOT_COOLDOWN = 400 #ms

ICON_PATH = os.path.join("assets", "icon.png")
FPS = 60