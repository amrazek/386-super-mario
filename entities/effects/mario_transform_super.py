from util import make_vector
from entities.characters.mario import MarioEffectSuper
from state.game_state import GameState, state_stack
from animation import OneShotAnimation
from util import world_to_screen
import config


"""small -> big

small form
intermediate form
small form
intermediate form
small
intermediate
large
small 
intermediate
large
"""


class MarioTransformSuper(GameState):
    def __init__(self, level, mario):
        super().__init__(None)

        self.running_game = state_stack.top

        self.level = level
        self.mario = mario

        atlas = level.asset_manager.character_atlas

        facing = 1 if mario.movement.is_facing_right else 0

        little_mario = ["mario_stand_left", "mario_stand_right"][facing]
        middle = ["super_mario_transform_left", "super_mario_transform_right"][facing]
        super_mario = ["super_mario_stand_left", "super_mario_stand_right"][facing]

        little_mario = atlas.load_static(little_mario)
        middle = atlas.load_static(middle)
        super_mario = atlas.load_static(super_mario)

        # tweak little mario frame size to match super mario
        fixed_little = super_mario.image.copy()
        fixed_little.fill(config.transparent_color)
        fixed_little.blit(little_mario.image, (0, little_mario.image.get_height()))
        fixed_little = fixed_little.convert()

        powerup = level.asset_manager.sounds['powerup']

        self.animation = self.build_animation(powerup.get_length(), fixed_little, middle.image, super_mario.image)
        mario.enabled = False

        # since we're positioning by top-left corner and super mario is larger than small mario,
        # we need a corrective offset
        self._offset = make_vector(0, -little_mario.image.get_height())

        powerup.play()

    def update(self, dt):
        # don't update running game
        self.animation.update(dt)

    def draw(self, screen):
        self.running_game.draw(screen)
        screen.blit(self.animation.image, world_to_screen(self.mario.position + self._offset, self.level.view_rect))

    def deactivated(self):
        self.mario.effects |= MarioEffectSuper

        # the top-left coordinate of mario needs to be moved to account for a larger sprite
        self.mario.position = self.mario.position + self._offset
        self.mario.enabled = True
        self.mario.input_state.reset()

    def build_animation(self, duration, small, middle, large):
        frames = []
        pieces = [small, middle]

        for x in range(0, 9):
            # triple up on frames so we can make the animation appear to move faster just before it finishes
            frames.append(pieces[x % len(pieces)])
            frames.append(pieces[x % len(pieces)])
            frames.append(pieces[x % len(pieces)])

        pieces = [small, middle, large]

        for x in range(0, 6):
            frames.append(pieces[x % len(pieces)])
            frames.append(pieces[x % len(pieces)])

        frames.append(small)
        frames.append(large)

        return OneShotAnimation(frames, duration, self._animation_finished)

    def _animation_finished(self):
        # have to manipulate game state stack directly since this state was originally designed
        # to be pushed over RunLevel, but now it's over RunSession
        # we don't want RunSession's activate to fire
        assert state_stack.top is self
        state_stack.states.pop()
        self.deactivated()

    @property
    def finished(self):
        return False

    @staticmethod
    def apply_transform(level, mario):
        # transform little mario into super mario
        transform = MarioTransformSuper(level, mario)
        state_stack.states.append(transform)
