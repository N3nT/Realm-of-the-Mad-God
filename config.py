import os

# window setting
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

# player settings
PLAYER_SIZE = 80
PLAYER_SPEED = 5

# spell settings
BULLET_SPEED = 12
BULLET_LIFETIME = 1000
SHOOT_COOLDOWN = 400

# audio settings

MUSIC_VOLUME = 0.05
SFX_VOLUME = 0.5

ICON_PATH = os.path.join("assets", "icon.png")
FPS = 60