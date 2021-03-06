from abc import ABC, abstractmethod
from .level_entity import LevelEntity
import constants


class Enemy(LevelEntity, ABC):
    def __init__(self, level, rect):
        super().__init__(rect)

        assert level is not None

        self.level = level

    @property
    def layer(self):
        return constants.Enemy

    @abstractmethod
    def update(self, dt, view_rect):
        pass

    @abstractmethod
    def draw(self, screen, view_rect):
        pass

    @abstractmethod
    def die(self):
        pass

    @abstractmethod
    def destroy(self):
        pass
