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
from pygame.locals import FULLSCREEN, KEYUP, K_r, K_ESCAPE, K_SPACE


BACKGROUND_COLOR = THECOLORS["black"]
TEXT_COLOR = THECOLORS["white"]

SEPARATOR = ":"
THE_STRING = "MM" + SEPARATOR + "SS" + SEPARATOR + "MS"
FONT_PATH = "data/mono.ttf"


def main():
    surface = get_surface()
    resolution = pygame.display.get_desktop_sizes()[0]

    font, font_rect, font_blit_point = get_font_artifacts(resolution)

    running = False  # wheter the stopwatch is running or not
    start = 0  # milliseconds from start
    start_tick = 0  # the number of ticks when we began counting

    while True:
        try:
            running, start, start_tick = get_status(running, start, start_tick)
        except EndLoopInterrupt:
            break

        render_time(start, font, surface, font_blit_point)

        # update display
        pygame.display.flip()
        pygame.time.wait(33)


def get_font_artifacts(resolution):
    # get highest font size that fits resolution width
    font_size = int(resolution[1] * 0.9)
    font_size_fits = False
    max_string_length = resolution[0] * 0.95

    while not font_size_fits:
        font = pygame.font.Font(FONT_PATH, font_size)
        font_rect = font.size(THE_STRING)
        if font_rect[0] > max_string_length:
            font_size = font_size - 10
        else:
            font_size_fits = True

    # get the point to draw the font in the midle of the screen
    font_blit_point = (resolution[0] / 2) - (font_rect[0] / 2), font_rect[1] / 3

    return font, font_rect, font_blit_point


def get_status(running, start, start_tick):
    event = pygame.event.poll()

    if event.type == KEYUP:
        if event.key == K_ESCAPE:
            raise EndLoopInterrupt

        if event.key == K_SPACE:
            if not running:
                # starting the timer, so set the tick count reference to the current tick count
                # plus the last tick count
                start_tick = pygame.time.get_ticks() - start

            # swap value
            running = not running

        elif event.key == K_r:
            # initialize the tick count
            start = 0
            running = False

    if running:
        # get the amount of ticks(milliseconds) that passed from the start
        start = pygame.time.get_ticks() - start_tick

    return running, start, start_tick


def get_surface():
    pygame.init()

    # create our main window SDL surface
    surface = pygame.display.set_mode(flags=FULLSCREEN)
    pygame.display.set_caption("Stopwatch")

    return surface


def get_time_surface(time_string, font):
    surface = font.render(time_string, 1, TEXT_COLOR)
    size = surface.get_width(), int(surface.get_height() * 3)
    surface = pygame.transform.scale(surface, size)
    return surface


def render_time(start, font, surface, font_blit_point):
    # render the time, by converting ticks to datetime.time + hundredth of a second
    hundredth_of_a_second = int(str(start)[-2:])  # hundredth of a second
    time_in_ms = time((start // 1000) // 3600, ((start // 1000) // 60 % 60), (start // 1000) % 60)
    time_string = "{}{}{:02d}".format(time_in_ms.strftime("%M:%S"), SEPARATOR, hundredth_of_a_second)

    time_surface = get_time_surface(time_string, font)
    # fill the screen with white, to erase the previous time
    surface.fill(BACKGROUND_COLOR)
    surface.blit(time_surface, font_blit_point)  # draw the time


class EndLoopInterrupt(BaseException):
    pass


if __name__ == "__main__":
    main()
