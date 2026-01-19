from abc import ABC, abstractmethod

from entities.enemy import Ghost, Politician, Butcher, Bat


class EnemyFactory(ABC):
    """Abstrakcyjna fabryka do tworzenia przeciwników"""
    @abstractmethod
    def create_ghost(self, pos, groups, player, bullet_group):
        pass

    @abstractmethod
    def create_politician(self, pos, groups, player, bullet_group):
        pass

    @abstractmethod
    def create_butcher(self, pos, groups, player, bullet_group):
        pass

    @abstractmethod
    def create_bat(self, pos, groups, player, bullet_group):
        pass

class TestFactory(EnemyFactory):
    """Testowa fabryka do testowania przeciwników"""
    def create_ghost(self, pos, groups, player, bullet_group):
        return Ghost(pos, groups, player, enemy_name='ghost', hp=50, speed=0, bullet_group=bullet_group)

    def create_politician(self, pos, groups, player, bullet_group):
        return Politician(pos, groups, player, enemy_name='politician', hp=50, speed=0, bullet_group=bullet_group)

    def create_butcher(self, pos, groups, player, bullet_group):
        return Butcher(pos, groups, player, enemy_name='butcher', hp=50, speed=2, bullet_group=bullet_group)

    def create_bat(self, pos, groups, player, bullet_group):
        return Bat(pos, groups, player, enemy_name='bat', hp=50, speed=0, bullet_group=bullet_group)