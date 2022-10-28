#!/usr/bin/env python
# stopwatch is a pygame based stopwatch
# Copyright (C) 2011 Alejandro Varas
# based on code taken from http://www.bonf.net/2007/05/18/so/

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

from datetime import time, timedelta

import pygame
import pygame.font
from pygame.colordict import THECOLORS
from pygame.locals import *


def main():
    font_path = "data/talldark.ttf"
    fullscreen = True
    video_flags = fullscreen and FULLSCREEN
    print(video_flags)
    pygame.init()

    # get the highest resolution
    resolution = pygame.display.list_modes()[0]

    # create our main window SDL surface
    surface = pygame.display.set_mode(resolution, video_flags)
    pygame.display.set_caption("Stopwatch -- stopwatch.alej0.tk")

    # get highest font size that fits resolution width
    font_size = int(resolution[1] / 1.2)
    font_size_fits = False
    max_string_length = resolution[0] / 8 * 7

    while not font_size_fits:
        font = pygame.font.Font(font_path, font_size)
        font_rect = font.size("00:00:00,00")
        if font_rect[0] > max_string_length:
            font_size = font_size - 10
        else:
            font_size_fits = True

    # get the point to draw the font in the midle of the screen
    font_blit_point = resolution[0] / 16, resolution[1] / 2 - font_rect[1] / 2


    on = False #wheter the stopwatch is running or not
    a = 0 # milliseconds from start
    start_tick = 0 # the number of ticks when we began counting

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

            elif event.key == K_f:
                # swap video mode widowed, fullscreen
                fullscreen = not fullscreen
                video_flags = (fullscreen and FULLSCREEN) | (not fullscreen and RESIZABLE)
                pygame.display.set_mode(resolution, video_flags)

        if on:
            # get the amount of ticks(milliseconds) that passed from the start
            a = (pygame.time.get_ticks() - start_tick)

        # render the time, by converting ticks to datetime.time + hundredth of a second
        t = time((a // 1000) // 3600, ((a // 1000) // 60 % 60), (a // 1000) % 60)
        h_o_s = str(a)[-3:][:2] # hundredth of a second
        t_string = ','.join((t.strftime("%H:%M:%S"), h_o_s))
        tempsurface = font.render(t_string, 1, THECOLORS["black"])

        surface.fill(THECOLORS["white"]) #fill the screen with white, to erase the previous time
        surface.blit(tempsurface, font_blit_point) # draw the time

        pygame.display.flip()
        pygame.time.wait(100)


if __name__ == '__main__':
    main()
