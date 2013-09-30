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
cyan = 0, 255, 255
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

x, y, mod, arg = 0, 0, 0, 0

prevctr = -1

done = False
show_coords = 0

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
            elif ev.key == pygame.K_c:
                show_coords = (show_coords + 1) % 4
                
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
                    x, y = float(splitted[1]), float(splitted[2])
                    mod = math.sqrt(x*x + y*y)
                    arg = math.atan2(y,x)
            except:
                print "network data parsing error, original data follows"
                print repr(data)
                raise

    # update stuff
    screen.fill(black)
    
    # draw stuff
    center = (width/2, height/2)
    point = (int(500*x + width/2),int(-500*y + height/2))
    
    draw.line(screen, white, center, point, 3)
    draw.circle(screen, cyan, point, 6, 3)
    
    titlestr, labelstr = None, None
    if show_coords == 1:
        titlestr = "Cartesian coordinates"
        labelstr = "(%0.2f,%0.2f)" % (x,y)
    if show_coords == 2:
        titlestr = "Screen coordinates"
        labelstr = "(%d,%d)" % point
    if show_coords == 3:
        titlestr = "Polar coordinates"
        labelstr = "(%0.2f,%0.2f)" % (mod,arg)
    if labelstr:
        title = labelfont.render(titlestr, False, white)
        label = labelfont.render(labelstr, False, white)
        titlerect = title.get_rect()
        titlerect.center = (width/2, 30)
        labelrect = label.get_rect()
        labelrect.centerx = point[0]
        if y > 0:
            labelrect.bottom = point[1] - 5
        else:
            labelrect.top = point[1] + 5
        screen.blit(title, titlerect)
        screen.blit(label, labelrect)
    
    display.flip()

pygame.quit()