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


THE_STRING = "00:00:00,00"
FONT_PATH = "data/mono.ttf"


def main():
    pygame.init()
    resolution = pygame.display.get_desktop_sizes()[0]

    # create our main window SDL surface
    surface = pygame.display.set_mode(flags=FULLSCREEN)
    pygame.display.set_caption("Stopwatch")

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

    on = False  # wheter the stopwatch is running or not
    a = 0  # milliseconds from start
    start_tick = 0  # the number of ticks when we began counting

    while True:
        event = pygame.event.poll()

        if event.type == KEYUP:
            if event.key == K_ESCAPE:
                break

            if event.key == K_SPACE:
                if not on:
                    # starting the timer, so set the tick count reference to the current tick count
                    # plus the last tick count
                    start_tick = pygame.time.get_ticks() - a

                # swap value
                on = not on

            elif event.key == K_r:
                # initialize the tick count
                a = 0
                on = False

        if on:
            # get the amount of ticks(milliseconds) that passed from the start
            a = pygame.time.get_ticks() - start_tick

        # render the time, by converting ticks to datetime.time + hundredth of a second
        t = time((a // 1000) // 3600, ((a // 1000) // 60 % 60), (a // 1000) % 60)
        h_o_s = int(str(a)[-2:])  # hundredth of a second
        t_string = "{},{:02d}".format(t.strftime("%H:%M:%S"), h_o_s)

        tempsurface = font.render(t_string, 1, THECOLORS["black"])
        size = tempsurface.get_width(), int(tempsurface.get_height() * 4.5)
        tempsurface = pygame.transform.scale(tempsurface, size)

        # fill the screen with white, to erase the previous time
        surface.fill(THECOLORS["white"])
        surface.blit(tempsurface, font_blit_point)  # draw the time

        pygame.display.flip()
        pygame.time.wait(100)


if __name__ == "__main__":
    main()
