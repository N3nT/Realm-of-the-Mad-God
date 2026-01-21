from abc import ABC, abstractmethod

from entities.enemy import Ghost, Politician, Butcher, Bat


class EnemyFactory(ABC):
    """Abstrakcyjna fabryka do tworzenia przeciwników"""
    @abstractmethod
    def create_ghost(self, pos, groups, player, bullet_group, obstacle_sprites):
        pass

    @abstractmethod
    def create_politician(self, pos, groups, player, bullet_group, obstacle_sprites):
        pass

    @abstractmethod
    def create_butcher(self, pos, groups, player, bullet_group, obstacle_sprites):
        pass

    @abstractmethod
    def create_bat(self, pos, groups, player, bullet_group, obstacle_sprites):
        pass

class TestFactory(EnemyFactory):
    """Testowa fabryka do testowania przeciwników"""
    def create_ghost(self, pos, groups, player, bullet_group, obstacle_sprites):
        return Ghost(pos, groups, player, enemy_name='ghost', hp=50, speed=3, bullet_group=bullet_group, obstacle_sprites=obstacle_sprites)

    def create_politician(self, pos, groups, player, bullet_group, obstacle_sprites):
        return Politician(pos, groups, player, enemy_name='politician', hp=50, speed=2.25, bullet_group=bullet_group, obstacle_sprites=obstacle_sprites)

    def create_butcher(self, pos, groups, player, bullet_group, obstacle_sprites):
        return Butcher(pos, groups, player, enemy_name='butcher', hp=50, speed=2, bullet_group=bullet_group,obstacle_sprites=obstacle_sprites)

    def create_bat(self, pos, groups, player, bullet_group, obstacle_sprites):
        return Bat(pos, groups, player, enemy_name='bat', hp=50, speed=3, bullet_group=bullet_group, obstacle_sprites=obstacle_sprites)