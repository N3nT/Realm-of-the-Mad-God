from abc import ABC, abstractmethod

from entities.enemy import (
    Bat,
    BlackMagic,
    Butcher,
    Ghost,
    Mage,
    Politician,
    Skeleton,
)


class EnemyFactory(ABC):
    """Abstrakcyjna fabryka do tworzenia przeciwników"""

    @abstractmethod
    def create_ghost(
        self, pos: tuple, groups: list, player, bullet_group, obstacle_sprites
    ):
        pass

    @abstractmethod
    def create_politician(
        self, pos: tuple, groups: list, player, bullet_group, obstacle_sprites
    ):
        pass

    @abstractmethod
    def create_butcher(
        self, pos: tuple, groups: list, player, bullet_group, obstacle_sprites
    ):
        pass

    @abstractmethod
    def create_bat(
        self, pos: tuple, groups: list, player, bullet_group, obstacle_sprites
    ):
        pass

    @abstractmethod
    def create_skeleton(
        self, pos: tuple, groups: list, player, bullet_group, obstacle_sprites
    ):
        pass

    @abstractmethod
    def create_black_magic(
        self, pos: tuple, groups: list, player, bullet_group, obstacle_sprites
    ):
        pass

    @abstractmethod
    def create_mage(
        self, pos: tuple, groups: list, player, bullet_group, obstacle_sprites
    ):
        pass


class MainFactory(EnemyFactory):
    """Glówna fabryka do tworzenia przeciwników"""

    def create_ghost(
        self, pos: tuple, groups: list, player, bullet_group, obstacle_sprites
    ):
        return Ghost(
            pos,
            groups,
            player,
            enemy_name='ghost',
            hp=50,
            speed=3,
            bullet_group=bullet_group,
            obstacle_sprites=obstacle_sprites,
        )

    def create_politician(
        self, pos: tuple, groups: list, player, bullet_group, obstacle_sprites
    ):
        return Politician(
            pos,
            groups,
            player,
            enemy_name='politician',
            hp=50,
            speed=2.25,
            bullet_group=bullet_group,
            obstacle_sprites=obstacle_sprites,
        )

    def create_butcher(
        self, pos: tuple, groups: list, player, bullet_group, obstacle_sprites
    ):
        return Butcher(
            pos,
            groups,
            player,
            enemy_name='butcher',
            hp=50,
            speed=2,
            bullet_group=bullet_group,
            obstacle_sprites=obstacle_sprites,
        )

    def create_bat(
        self, pos: tuple, groups: list, player, bullet_group, obstacle_sprites
    ):
        return Bat(
            pos,
            groups,
            player,
            enemy_name='bat',
            hp=50,
            speed=3,
            bullet_group=bullet_group,
            obstacle_sprites=obstacle_sprites,
        )

    def create_skeleton(
        self, pos: tuple, groups: list, player, bullet_group, obstacle_sprites
    ):
        return Skeleton(
            pos,
            groups,
            player,
            enemy_name='skeleton',
            hp=80,
            speed=2.5,
            bullet_group=bullet_group,
            obstacle_sprites=obstacle_sprites,
        )

    def create_black_magic(
        self, pos: tuple, groups: list, player, bullet_group, obstacle_sprites
    ):
        return BlackMagic(
            pos,
            groups,
            player,
            enemy_name='black_magic',
            hp=70,
            speed=2,
            bullet_group=bullet_group,
            obstacle_sprites=obstacle_sprites,
        )

    def create_mage(
        self, pos: tuple, groups: list, player, bullet_group, obstacle_sprites
    ):
        return Mage(
            pos,
            groups,
            player,
            enemy_name='mage',
            hp=65,
            speed=2.5,
            bullet_group=bullet_group,
            obstacle_sprites=obstacle_sprites,
        )