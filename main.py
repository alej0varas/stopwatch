#!/usr/bin/env python2.6
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


import pygame, pygame.font
from pygame.locals import *

#yuck, global vars ^_^
font = None
surface = None
resolution = (1366, 768) 

pygame.init() #initialize pygame

font_path = "data/talldark.ttf"
font = pygame.font.Font(font_path, int(resolution[1] * (5 / 7.))) #load up a ttf font

video_flags = DOUBLEBUF | FULLSCREEN
surface = pygame.display.set_mode(resolution, video_flags) #create our main window SDL surface
surface.fill((255, 255, 255)) #fill with white


def main():
    on = False #wheter the stopwatch should be running or not
    time = [0, 0, 0, 0] # an array to keep the current time measurement which is being rendered
    start_state = [0, 0, 0, 0] #the time measurement from which to start counting
    start_tick = 0 # the number of ticks when we began counting

    last_tick = pygame.time.get_ticks()	# initialize the tick count
 
    while True: #do forever
        event = pygame.event.poll()

        if event.type == KEYUP:
            if event.key == K_ESCAPE:
                break

            if event.key == K_SPACE: # if the space bar was pushed
                if on: # if currently running
                    #prepare start_state for future use, save current time
                    start_state[3] = time[3]
                    start_state[2] = time[2]
                    start_state[1] = time[1]
                    start_state[0] = time[0]
                else:
                    #starting the timer, so set the tick count reference to the current tick count
                    start_tick = pygame.time.get_ticks()

                on = not on #toggle on

            elif event.key == K_r:
                last_tick = pygame.time.get_ticks()	# initialize the tick count                
                time = [0, 0, 0, 0] # an array to keep the current time measurement which is being rendered
                start_state = [0, 0, 0, 0] #the time measurement from which to start counting
                on = False

        if on:
            a = (pygame.time.get_ticks() - start_tick) # get the amount of ticks(miliseconds) that passed from when the stopwatch was last run

            time[3] = start_state[3] + int(str(a)[-3:]) / 10 # centesima?
            time[2] = start_state[2] + (a / 1000) % 60 #seconds
            time[1] = start_state[1] + ((a / 1000) / 60 % 60) #minutes
            time[0] = start_state[0] + (a / 1000) / 3600 #hours
 
        # render the time, by converting each array member to a string, and concating with ':' in between time components. render in black on a white background.
        tempsurface=font.render("%02d:%02d:%02d,%02d" % (time[0], time[1], time[2], time[3]), 1, (0, 0, 0), (255, 255, 255))
 
        surface.fill((255, 255, 255)) #fill the screen with white, to erase the previous time
        surface.blit(tempsurface, (resolution[0]/32, resolution[1]/4)) # blit the temporary surface to the screen

        pygame.display.flip()
 
 
if __name__ == '__main__':
    main()
