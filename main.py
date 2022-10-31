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


BACKGROUND_COLOR = THECOLORS["black"]
TEXT_COLOR = THECOLORS["white"]

SEPARATOR = ":"
THE_STRING = "MM" + SEPARATOR + "SS" + SEPARATOR + "MS"
FONT_PATH = "data/mono.ttf"


class Stopwatch:
    def __init__(self, application, parent, position, size):
        self.parent = parent
        self.application = application
        self.position = position

        self.surface = pygame.Surface(size)

        self.start = 0
        self.start_tick = 0

    def run(self):
        self.event_handler()
        if self.application.running:
            self.start = pygame.time.get_ticks() - self.start_tick

        self.application.render_time(self.start)

    def event_handler(self):
        event = pygame.event.poll()
        if event.type == KEYUP:
            if event.key == K_ESCAPE:
                self.application.object = self.parent
            elif event.key == K_SPACE:
                self.handle_space()
            elif event.key == K_r:
                self.handle_reset()
        pygame.event.clear()

    def handle_reset(self):
        self.start = 0
        self.application.running = False

    def handle_space(self):
        if not self.application.running:
            self.start_tick = pygame.time.get_ticks() - self.start
        self.application.running = not self.application.running

    def render(self):
        self.surface.fill("blue")
        font = pygame.font.Font(FONT_PATH, 50)
        text_surface = font.render("Stopwatch", 1, "green")
        self.surface.blit(text_surface, (10, 10))
        self.rect = self.application.surface.blit(self.surface, self.position)


class Countdown:
    def __init__(self, application, parent, position, size):
        self.application = application
        self.parent = parent
        self.position = position

        self.surface = pygame.Surface(size)

        self.ticks_count = 5000
        self.ticks_remaining = self.ticks_count
        self.ticks_stop = 0

    def run(self):
        try:
            self.event_handler()
        except EndLoopInterrupt:
            return

        if self.application.running:
            _ticks = self.ticks_stop - pygame.time.get_ticks()
            if _ticks <= 0:
                raise EndLoopInterrupt
            ticks_remaining = abs(_ticks)
        else:
            ticks_remaining = self.ticks_count

        self.application.render_time(ticks_remaining)

    def event_handler(self):
        event = pygame.event.poll()
        if event.type == KEYUP:
            if event.key == K_ESCAPE:
                self.application.object = self.parent
                raise EndLoopInterrupt
            elif event.key == K_SPACE:
                self.handle_space()
        pygame.event.clear()

    def handle_space(self):
        if not self.application.running:
            self.ticks_stop = pygame.time.get_ticks() + self.ticks_count
            self.application.running = True

    def render(self):
        self.surface.fill("blue")
        font = pygame.font.Font(FONT_PATH, 50)
        text_surface = font.render("Countdown", 1, "green")
        self.surface.blit(text_surface, (10, 10))
        self.rect = self.application.surface.blit(self.surface, self.position)


class Menu:
    def __init__(self, application):
        self.application = application
        self.buttons = {}

        size = 400, 100
        position = 10, 10
        self.buttons["countdown"] = Countdown(self.application, self, position, size)

        position = size[0] + (position[0] * 2), 10
        self.buttons["stopwatch"] = Stopwatch(self.application, self, position, size)

    def run(self):
        self.render()

        self.event_handler()

    def event_handler(self):
        event = pygame.event.poll()
        if event.type == KEYUP:
            if event.key == K_ESCAPE:
                handle_exit()

            elif event.key == K_c:
                self.application.object = self.buttons["countdown"]

            elif event.key == K_s:
                self.application.object = self.buttons["stopwatch"]

        elif event.type == pygame.locals.MOUSEBUTTONUP:
            point = pygame.mouse.get_pos()
            for _, _object in self.buttons.items():
                if _object.rect.collidepoint(point):
                    self.application.object = _object
                    break

        pygame.event.clear()

    def render(self):
        self.application.surface.fill(BACKGROUND_COLOR)
        for _, button in self.buttons.items():
            button.render()


def handle_exit():
    raise EndLoopInterrupt


def get_surface():
    pygame.init()

    # create our main window SDL surface
    surface = pygame.display.set_mode(flags=FULLSCREEN)
    pygame.display.set_caption("Stopwatch")

    return surface


class EndLoopInterrupt(BaseException):
    pass


class Application:
    def __init__(self):
        self.surface = get_surface()
        self.surface.fill(BACKGROUND_COLOR)
        self.resolution = pygame.display.get_desktop_sizes()[0]
        self.set_font_artifacts()
        self.object = Menu(self)
        self.running = False

    def run(self):
        self.object.run()

    def get_time_surface(self, time_string):
        surface = self.font.render(time_string, 1, TEXT_COLOR)
        size = surface.get_width(), int(surface.get_height() * 3)
        surface = pygame.transform.scale(surface, size)
        return surface

    def set_font_artifacts(self):
        # get highest font size that fits resolution width
        font_size = int(self.resolution[1] * 0.9)
        font_size_fits = False
        max_string_length = self.resolution[0] * 0.95

        while not font_size_fits:
            font = pygame.font.Font(FONT_PATH, font_size)
            font_rect = font.size(THE_STRING)
            if font_rect[0] > max_string_length:
                font_size = font_size - 10
            else:
                font_size_fits = True

        self.font = font
        self.font_rect = font_rect
        self.font_blit_point = (self.resolution[0] / 2) - (font_rect[0] / 2), font_rect[
            1
        ] / 3

    def render_time(self, start):
        # render the time, by converting ticks to datetime.time + hundredth of a second
        hundredth_of_a_second = int(str(start)[-2:])  # hundredth of a second
        time_in_ms = time(
            (start // 1000) // 3600, ((start // 1000) // 60 % 60), (start // 1000) % 60
        )
        time_string = "{}{}{:02d}".format(
            time_in_ms.strftime("%M:%S"), SEPARATOR, hundredth_of_a_second
        )
        time_surface = self.get_time_surface(time_string)
        # fill the screen with white, to erase the previous time
        self.surface.fill(BACKGROUND_COLOR)
        self.surface.blit(time_surface, self.font_blit_point)  # draw the time


def main():
    application = Application()

    while True:

        application.run()

        pygame.display.flip()
        pygame.time.wait(33)


if __name__ == "__main__":
    main()
