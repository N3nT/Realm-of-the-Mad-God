from abc import ABC, abstractmethod

from entities.enemy import Ghost, Politician, Butcher, Bat


class EnemyFactory(ABC):
    """Abstrakcyjna fabryka do tworzenia przeciwników"""
    @abstractmethod
    def create_ghost(self, pos, groups, player):
        pass

    def create_politician(self, pos, groups, player):
        pass

    @abstractmethod
    def create_butcher(self, pos, groups, player):
        pass

    @abstractmethod
    def create_bat(self, pos, groups, player):
        pass

class TestFactory(EnemyFactory):
    """Testowa fabryka do testowania przeciwników"""
    def create_ghost(self, pos, groups, player):
        return Ghost(pos, groups, player, enemy_name='ghost', hp=50, speed=0)

    def create_politician(self, pos, groups, player):
        return Politician(pos, groups, player, enemy_name='politician', hp=50, speed=0)

    def create_butcher(self, pos, groups, player):
        return Butcher(pos, groups, player, enemy_name='butcher', hp=50, speed=0)

    def create_bat(self, pos, groups, player):
        return Bat(pos, groups, player, enemy_name='bat', hp=50, speed=0)