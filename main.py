#!/usr/bin/env python
# stopwatch is a pygame based stopwatch
# Copyright (C) 2022 Alexandre Varas

######################################################################
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#######################################################################

from datetime import time

import pygame
import pygame.font
from pygame.colordict import THECOLORS
from pygame.locals import FULLSCREEN, KEYUP, K_c, K_r, K_s, K_ESCAPE, K_SPACE


BACKGROUNDS = {
    "menu": THECOLORS["black"],
    "button": THECOLORS["blue"],
    "stopwatch": THECOLORS["black"],
}
TEXT_COLORS = {
    "menu": THECOLORS["white"],
    "button": THECOLORS["green"],
    "stopwatch": THECOLORS["white"],
}
TEXT_SIZES = {
    "button": 50,
    "stopwatch": 100,
}
SEPARATOR = ":"
THE_STRING = "MM" + SEPARATOR + "SS" + SEPARATOR + "MS"
FONT_PATH = "data/mono.ttf"
FONT_SIZES = {
    "stopwatch": 500,
    "button": 50,
}


def get_resolution():
    pygame.init()
    return pygame.display.get_desktop_sizes()[0]


def get_font_artifacts(font_size):
    # get highest font size that fits resolution width
    resolution = get_resolution()
    # font_size = int(resolution[1] * 0.9)
    font_size_fits = False
    max_string_length = resolution[0] * 0.95

    while not font_size_fits:
        font = pygame.font.Font(FONT_PATH, font_size)
        font_rect = font.size(THE_STRING)
        if font_rect[0] > max_string_length:
            font_size = font_size - 10
        else:
            font_size_fits = True

    font = {
        "font": font,
        "font_rect": font_rect,
        "font_blit_point": ((resolution[0] / 2) - (font_rect[0] / 2), font_rect[1] / 3),
    }

    return font


FONTS = {
    "stopwatch": get_font_artifacts(FONT_SIZES["stopwatch"]),
    "button": get_font_artifacts(FONT_SIZES["button"]),
}


class Button:
    def __init__(self, text, position, size):
        self.text = text
        self.position = position
        self.size = size
        self.surface = pygame.Surface(size)

    def render(self):
        self.surface.fill(BACKGROUNDS["button"])
        font = FONTS["button"]["font"]
        text_surface = font.render(self.text, 1, TEXT_COLORS["button"])
        self.surface.blit(text_surface, (10, 10))


class Stopwatch:
    def __init__(self, surface_size):
        self.surface = pygame.Surface(surface_size)
        self.running = False
        self.start = 0
        self.start_tick = 0
        self.text = "0"

    def run(self):
        self.event_handler()

        if self.running:
            self.start = pygame.time.get_ticks() - self.start_tick

    def event_handler(self):
        event = pygame.event.poll()

        if event.type == KEYUP:
            if event.key == K_ESCAPE:
                raise EndLoopInterrupt
            elif event.key == K_SPACE:
                self.handle_space()
            elif event.key == K_r:
                self.handle_reset()
        pygame.event.clear()

    def handle_reset(self):
        self.start = 0
        self.running = False

    def handle_space(self):
        if not self.running:
            self.start_tick = pygame.time.get_ticks() - self.start
        self.running = not self.running

    def get_time(self):
        return self.start

    def render(self):
        self.surface.fill(BACKGROUNDS["stopwatch"])
        text_surface = get_text_surface(self.get_time())
        self.surface.blit(text_surface, (10, 10))


class Countdown:
    def __init__(self, surface_size):
        self.surface = pygame.Surface(surface_size)
        self.running = False
        self.ticks_count = 5000
        self.ticks_remaining = self.ticks_count
        self.ticks_stop = 0
        self.text = str(self.ticks_remaining)

    def run(self):
        self.event_handler()

        if self.running:
            _ticks = self.ticks_stop - pygame.time.get_ticks()
            if _ticks <= 0:
                raise EndLoopInterrupt
            ticks_remaining = abs(_ticks)
        else:
            ticks_remaining = self.ticks_count
        self.ticks_remaining = ticks_remaining

    def event_handler(self):
        event = pygame.event.poll()
        if event.type == KEYUP:
            if event.key == K_ESCAPE:
                raise EndLoopInterrupt
            elif event.key == K_SPACE:
                self.handle_space()
        pygame.event.clear()

    def handle_space(self):
        if not self.running:
            self.ticks_stop = pygame.time.get_ticks() + self.ticks_count
            self.running = True

    def get_time(self):
        return self.ticks_remaining

    def render(self):
        self.surface.fill(BACKGROUNDS["stopwatch"])
        text_surface = get_text_surface(self.get_time())
        self.surface.blit(text_surface, (10, 10))


class Menu:
    def __init__(self, application):
        self.application = application
        self.surface_size = (
            self.application.surface.get_width(),
            self.application.surface.get_height(),
        )
        self.surface = pygame.Surface(self.surface_size)

        self.buttons = {}
        size = 400, 100
        position = 10, 10

        self.buttons["countdown"] = {
            "button": Button("Countdown", position, size),
            "class": Countdown,
        }

        position = size[0] + (position[0] * 2), 10
        self.buttons["stopwatch"] = {
            "button": Button("Stopwatch", position, size),
            "class": Stopwatch,
        }

    def run(self):
        self.event_handler()

    def event_handler(self):
        event = pygame.event.poll()
        if event.type == KEYUP:
            if event.key == K_ESCAPE:
                handle_exit()

            elif event.key == K_c:
                self.application.childapp = Countdown(self.surface_size)

            elif event.key == K_s:
                self.application.childapp = Stopwatch(self.surface_size)

        elif event.type == pygame.locals.MOUSEBUTTONUP:
            point = pygame.mouse.get_pos()

            for _, _object in self.buttons.items():
                if _object["button"].rect.collidepoint(point):
                    self.application.childapp = _object["class"](self.surface_size)
                    break

        pygame.event.clear()

    def render(self):
        self.surface.fill(BACKGROUNDS["menu"])
        for _, _object in self.buttons.items():
            _object["button"].render()

            _object["button"].rect = self.surface.blit(
                _object["button"].surface, _object["button"].position
            )


def handle_exit():
    raise EndLoopInterrupt


def get_surface():
    # create our main window SDL surface
    surface = pygame.display.set_mode(flags=FULLSCREEN)
    pygame.display.set_caption("Stopwatch")

    return surface


def get_time_surface(time_string):
    surface = FONTS["stopwatch"]["font"].render(
        time_string, 1, TEXT_COLORS["stopwatch"]
    )
    size = surface.get_width(), int(surface.get_height() * 3)
    surface = pygame.transform.scale(surface, size)
    return surface


def get_time_string(start):
    hundredth_of_a_second = int(str(start)[-2:])  # hundredth of a second
    time_in_ms = time(
        (start // 1000) // 3600, ((start // 1000) // 60 % 60), (start // 1000) % 60
    )
    time_string = "{}{}{:02d}".format(
        time_in_ms.strftime("%M:%S"), SEPARATOR, hundredth_of_a_second
    )
    return time_string


def get_text_surface(time):
    # render the time, by converting ticks to datetime.time + hundredth of a second
    time_string = get_time_string(time)
    time_surface = get_time_surface(time_string)
    # fill the screen with white, to erase the previous time
    return time_surface


class EndLoopInterrupt(BaseException):
    pass


class Application:
    def __init__(self):
        self.surface = get_surface()
        self.childapp = Menu(self)

    def run(self):
        try:
            self.render()
            self.childapp.run()
        except EndLoopInterrupt:
            self.childapp = self.childapp.parent

    def render(self):
        self.childapp.render()
        self.surface.blit(self.childapp.surface, (0, 0))


def main():
    application = Application()

    while True:

        application.run()

        pygame.display.flip()
        pygame.time.wait(33)


if __name__ == "__main__":
    main()
