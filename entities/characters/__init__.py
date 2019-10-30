from .enemy import Enemy
from .goomba import Goomba
from .corpse import Corpse
from .level_entity import LevelEntity, MovementParameters
from .mario import Mario, MarioEffects
from .brick import Brick
from .coin import Coin
from .coin_block import CoinBlock
from .mushroom_block import MushroomBlock

import entities.characters.triggers  # force triggers to be loaded

__all__ = ['Mario', 'Enemy', 'Goomba', 'Corpse', 'LevelEntity', 'MovementParameters', 'Brick', 'Coin', 'CoinBlock',
           'MushroomBlock']
