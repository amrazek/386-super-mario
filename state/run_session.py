import pygame
from .game_state import GameState
from assets.statistics import Statistics
from assets.level import Level
import entities.entity_manager
from .run_level import RunLevel
from state.game_state import state_stack
from scoring import Labels
from event import EventHandler
from .level_begin import LevelBegin
from .game_over import GameOver
from .time_over import TimeOut


class RunSession(GameState, EventHandler):
    """A session persists between levels, and is mainly about keep tracking of score, lives. A session ends
    when the player has run out of lives or has beaten all levels"""
    def __init__(self, assets):
        super().__init__()

        assert assets is not None

        self._finished = False
        self.assets = assets
        self.scoring_labels = Labels()
        self.mario_stats = Statistics(self.scoring_labels)
        self.mario_stats.reset()

        self.levels = [('level-1-1.level', "WORLD 1-1"),
                       ('level-1-2.level', "WORLD 1-2"),
                       ('level-1-3.level', "WORLD 1-3"),
                       ('level-1-4.level', "WORLD 1-4")]

        self.current_level = None
        self.level_runner = None

    def update(self, dt):
        if not self.finished:
            self.level_runner.update(dt)

            if self.current_level.mario.enabled:
                self.mario_stats.update(dt)

            if self.level_runner.finished:
                self.change_state()

    def draw(self, screen):
        if not self.finished:
            self.level_runner.draw(screen)
            self.scoring_labels.show_labels(screen)

    @property
    def finished(self):
        return self._finished

    def change_state(self):
        if self.current_level and self.current_level.timed_out:
            self.mario_stats.lives -= 1

        if self.mario_stats.lives == 0:
            state_stack.push(GameOver(self.scoring_labels))
            self._finished = True
        else:
            show_timeout = self.current_level.timed_out if self.current_level else False

            # play again if didn't clear it or haven't tried yet
            self.current_level = self.current_level or Level(self.assets,
                                                             entities.entity_manager.EntityManager.create_default(),
                                                             self.mario_stats)

            if self.current_level.cleared and len(self.levels) > 0:
                self.levels.pop(0)

            if len(self.levels) > 0:
                # load and play next level
                self.current_level = Level(self.assets,
                                           entities.entity_manager.EntityManager.create_default(),
                                           self.mario_stats)

                self.current_level.load_from_path("levels/" + self.levels[0][0])
                self.current_level.title = self.levels[0][1]

                self.level_runner = RunLevel(self.game_events, self.assets, self.current_level, self.mario_stats,
                                             self.scoring_labels)
                state_stack.push(self.level_runner)

                # add level begin message
                state_stack.push(LevelBegin(self.assets, self.current_level, self.scoring_labels, self.mario_stats))

                # show timeout on top of that, if we just timed out
                if show_timeout:
                    # overlay with level begin message
                    # don't push, because it will deactivate level begin and start music early
                    self.scoring_labels.prep_labels()
                    state_stack.states.append(TimeOut(self.game_events, self.mario_stats, self.scoring_labels))

            else:
                # todo: won the game!
                print("won (some of) the game!")
                self._finished = True

    def activated(self):
        if self.finished:
            return

        if not self.level_runner or self.level_runner.finished:
            if self.current_level and self.current_level.cleared:
                # show clear message if finished world
                # todo: push clear message
                self.level_runner = None
                self.change_state()
            else:
                self.change_state()  # move to next state (loss, victory, or level start)
        elif self.level_runner:
            self.level_runner.activated()
            self.current_level.begin()
        else:
            # no level runner -> we either just started, or finished a clear message
            self.change_state()

        self.game_events.register(self)

    def deactivated(self):
        if self.level_runner is not None:
            self.level_runner.deactivated()

        self.game_events.unregister(self)

    def handle_event(self, evt, game_events):
        if evt.type == pygame.KEYDOWN and evt.key == pygame.K_ESCAPE:
            self._finished = True
