import pygame
from pygame import Rect
from .element import Element
from .element import Anchor
from .text import Text
from util import make_vector
from .drawing import smart_draw
import config


class Button(Element):
    def __init__(self, position, size, background, font, anchor=Anchor.TOP_LEFT, text=None, on_click_callback=None,
                 text_color=config.default_text_color, mouseover_image=None):
        if size is None or (size[0] == 0 and size[1] == 0):
            size = background.get_rect().size

        super().__init__(position, Rect(*position, *size), anchor, )
        self._background = background
        self._background_mouseover = mouseover_image or background
        self._text = None

        if text is not None:
            self._text = Text(make_vector(size[0] // 2 + 1, size[1] // 2 + 2), text, font,
                              text_color, anchor=Anchor.CENTER)

            self.add_child(self._text)

        self.on_click = on_click_callback
        self._click_down = False
        self._mouseover = False
        self.layout()

    def draw(self, screen, view_rect):
        smart_draw(screen, self._background if not self._mouseover else self._background_mouseover, self.rect)

        super().draw(screen, view_rect)

    def handle_event(self, evt, game_events):
        super().handle_event(evt, game_events)

        if not evt.consumed:
            if evt.type == pygame.MOUSEBUTTONDOWN:
                self._click_down = self.rect.collidepoint(evt.pos)

                if self._click_down:
                    self.consume(evt)
                    self.make_active()

            elif evt.type == pygame.MOUSEBUTTONUP:
                inside = self.rect.collidepoint(evt.pos)

                if inside and self._click_down:
                    self.clicked()
                    self.consume(evt)

                self._click_down = False

        if evt.type == pygame.MOUSEMOTION:
            self._mouseover = self.rect.collidepoint(*evt.pos)

    def clicked(self):
        if self.on_click:
            self.on_click()
