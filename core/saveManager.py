import json
import os
from typing import Dict, Any, Optional


class SaveManager:
    """Zarzadzanie zapisem i wczytywaniem stanu gry"""

    SAVE_FILE = 'game_save.json'

    @staticmethod
    def save_game(player, game_time: int) -> bool:
        """Zapisz aktualny stan gry do pliku"""
        save_data: Dict[str, Any] = {
            'level': player.level,
            'xp': player.xp,
            'xp_to_next_level': player.xp_to_next_level,
            'health': player.health,
            'max_health': player.max_health,
            'energy': player.energy,
            'max_energy': player.max_energy,
            'position': {'x': player.rect.x, 'y': player.rect.y},
            'game_time': game_time,
        }

        try:
            with open(SaveManager.SAVE_FILE, 'w') as f:
                json.dump(save_data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    @staticmethod
    def load_game() -> Optional[Dict[str, Any]]:
        """Wczytaj stan gry z pliku"""
        if not os.path.exists(SaveManager.SAVE_FILE):
            return None

        try:
            with open(SaveManager.SAVE_FILE, 'r') as f:
                save_data = json.load(f)
            return save_data
        except Exception as e:
            print(f"Error loading game: {e}")
            return None

    @staticmethod
    def has_save() -> bool:
        """Sprawdź, czy istnieje plik zapisu"""
        return os.path.exists(SaveManager.SAVE_FILE)

    @staticmethod
    def delete_save() -> bool:
        """Usuń plik zapisu"""
        if os.path.exists(SaveManager.SAVE_FILE):
            try:
                os.remove(SaveManager.SAVE_FILE)
                return True
            except Exception as e:
                print(f"Error deleting save: {e}")
                return False
        return False
