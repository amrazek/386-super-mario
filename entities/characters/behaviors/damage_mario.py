from .behavior import Behavior
from ...effects import MarioDeath
from entities.collider import Collider, ColliderManager, Collision
from entities import Layer
from util import make_vector, world_to_screen
import config
from .interactive import Interactive


class DamageMario(Interactive):
    """A hitbox which will damage mario, if he is not invincible"""
    def __init__(self, level, entity, hitbox_offset, hitbox_size):
        super().__init__(level, entity, hitbox_offset, hitbox_size, self.on_mario_collision)

    def on_mario_collision(self, collision):
        # todo: logic which downgrades mario?

        mario = collision.hit_collider.entity

        self.level.despawn_mario()
        self.level.entity_manager.register(MarioDeath(self.level, self.level.mario.position))

    def destroy(self):
        pass
