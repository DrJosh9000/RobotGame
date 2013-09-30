#!/usr/bin/python2.7

#
#  RobotGame is licensed under the MIT license.
#
#  Copyright (c) 2013 Josh Deprez.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is furnished
#  to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import pygame
from pygame import display, transform, image, event, time, sprite, draw, font
import sys
import socket
import math


# PYGAME SETUP
# ------------------------------------------------------------------	

pygame.init()
clock = time.Clock()

size = width, height = 1024, 768
black = 0, 0, 0
white = 255,255,255
cyan = 0,255,255
red = 255,0,0
green = 0,192,0
blue = 0,0,255
screen = display.set_mode(size)

labelfont = font.Font(None, 36)

# NETWORK SETUP
# ------------------------------------------------------------------	

host, port = socket.gethostname(), 9991
print "host: %s" % host
print "port: %d" % port

remotesock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
remotesock.bind((host,port))
remotesock.setblocking(0)


# SETUP
# ------------------------------------------------------------------

x, y, z = 0, 0, 0

prevctr = -1

done = False

# GAME LOOP
# ------------------------------------------------------------------

while not done:
    clock.tick(60)
    for ev in event.get():
        if ev.type == pygame.QUIT:
            done = True
        elif ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_ESCAPE, pygame.K_q):
                done = True
                
    netdata = True
    while netdata:
        try:
            data, addr = remotesock.recvfrom(512)
        except socket.error:
            netdata = False
        else:
            # handle packet 
            try:
                splitted = data.rstrip('\0').split(',')
                ctr = int(splitted[0])
                if prevctr < ctr:
                    prevctr = ctr
                    x, y, z = float(splitted[1]), float(splitted[2]), float(splitted[3])
            except:
                print "network data parsing error, original data follows"
                print repr(data)
                raise

    # update stuff
    screen.fill(black)
    
    # draw a line from the center
    center = (width/2, height/2)
    
    draw.circle(screen, cyan, (center[0] + int(500*x), center[1] + int(-500*y)), 5 + abs(int(25.0/5.0*z)))  
    
    display.flip()

pygame.quit()