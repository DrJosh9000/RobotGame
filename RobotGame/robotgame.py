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
from pygame import display, transform, image, event, time, sprite, mixer
import sys
from random import randint, uniform
import socket
import math


# PYGAME SETUP
# ------------------------------------------------------------------	

pygame.init()
clock = time.Clock()

size = width, height = 1024, 768
black = 0, 0, 0
screen = display.set_mode(size)
bgimg = transform.scale(image.load("bg.png"), (1024, 768)).convert()

explosion_sound = mixer.Sound("explosion.aiff")
shoot_sound = mixer.Sound("shoot.aiff")


# GAME CLASSES
# ------------------------------------------------------------------	

class BouncySprite(sprite.Sprite):
    def __init__(self, imagefilename, initialpos):
        sprite.Sprite.__init__(self)
        self.baseimage = self.image = transform.scale2x(image.load(imagefilename))
        self.rect = self.image.get_rect();
        self.realpos = initialpos
        self.rect.center = self.realpos
        self.acceleration_magnitude = 0.0
        self.rotation = math.pi / 2.0
        self.velocity = [0,0]
        self.acceleration = [0,0]
    
    def update(self):
        self.acceleration = [self.acceleration_magnitude * math.cos(self.rotation), -self.acceleration_magnitude * math.sin(self.rotation)]
        self.velocity = [a+b for a,b in zip(self.velocity, self.acceleration)]
        self.image = transform.rotate(self.baseimage, self.rotation * 180.0 / math.pi - 90)
        self.realpos = [a+b for a,b in zip(self.realpos, self.velocity)]
        self.rect.center = self.realpos
        if self.rect.left < 0:
            self.velocity[0] = abs(self.velocity[0])
        if self.rect.right > width:
            self.velocity[0] = -abs(self.velocity[0])
        if self.rect.top < 0:
            self.velocity[1] = abs(self.velocity[1])
        if self.rect.bottom > height:
            self.velocity[1] = -abs(self.velocity[1])

class Explosion(sprite.Sprite):
    def __init__(self, position):
        sprite.Sprite.__init__(self)
        self.frames = [transform.scale2x(image.load("explosion%d.png" % i)) for i in xrange(0,3)]
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.index = 0
        explosion_sound.play()

    def update(self):
        sprite.Sprite.update(self)
        self.index += 1
        if self.index == 12:
            self.kill()
        else:
            self.image = self.frames[self.index / 4]

class Robot(BouncySprite):
    def __init__(self, game):
        BouncySprite.__init__(self, "robot.png", (width / 2, height / 2))
        self.game = game
        
    def shoot(self):    
        if self.alive():
            shot = Shot(self.game, self.realpos, 20)
            shot.velocity = [20 * math.cos(self.rotation), -20 * math.sin(self.rotation)]
            self.game.allsprites.add(shot)
    
    def update(self):
        BouncySprite.update(self)
        if sprite.spritecollide(self, self.game.monsters, False):
            self.kill()
            
    def kill(self):
        # Create explosion
        self.game.allsprites.add(Explosion(self.realpos))
        sprite.Sprite.kill(self)
        
    
class Monster(BouncySprite):
    def __init__(self, game):
        BouncySprite.__init__(self, "monster.png", [randint(0,width), randint(0,height)])
        if randint(0,1):
            if randint(0,1):
                self.realpos[0] = -16
            else:
                self.realpos[0] = width+16
        else:
            if randint(0,1):
                self.realpos[1] = -16
            else:
                self.realpos[1] = height+16
        self.game = game
        self.velocity = [uniform(-2,2), uniform(-2,2)]
        
    def kill(self):
        # Create explosion
        self.game.allsprites.add(Explosion(self.realpos))
        sprite.Sprite.kill(self)
        
class Shot(BouncySprite):
    def __init__(self, game, initialpos, life):
        BouncySprite.__init__(self, "shot.png", initialpos)
        self.life = life
        self.game = game
        shoot_sound.play()
        
    def update(self):
        BouncySprite.update(self)
        if sprite.spritecollide(self, self.game.monsters, True):
            self.kill()
        self.life -= 1
        if self.life <= 0:
            self.kill()
        

# GAME SETUP
# ------------------------------------------------------------------

class RobotGame(object):
    def __init__(self):
        self.robot = Robot(self)
        self.monsters = sprite.RenderPlain(Monster(self) for x in xrange(10))
        self.allsprites = self.monsters.copy()
        self.allsprites.add(self.robot)


# GAME LOOP
# ------------------------------------------------------------------

def game():
    
    # NETWORK SETUP
    # ------------------------------------------------------------------	
    
    host, port = socket.gethostname(), 9991
    print "host: %s" % host
    print "port: %d" % port
    
    remotesock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    remotesock.bind((host,port))
    remotesock.setblocking(0)
    prevctr = -1
    done = False
    game = RobotGame()
    index = 0
    while not done:
        clock.tick(60)
        for ev in event.get():
            if ev.type == pygame.QUIT:
                done = True
            elif ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_ESCAPE, pygame.K_q):
                    done = True
                elif ev.key == pygame.K_r:
                    game = RobotGame()
                                        
        netdata = True
        while netdata:
            try:
                data, addr = remotesock.recvfrom(512)
                # handle packet
                try:
                    splitted = data.rstrip('\0').split(',')
                    ctr = int(splitted[0])
                    if prevctr < ctr:
                        prevctr = ctr
                        if splitted[1] in ('left', 'right'):
                            if game.robot.alive():
                                #fire cannon
                                game.robot.shoot()
                            else:
                                game = RobotGame()
                        else:
                            x, y = float(splitted[1]), float(splitted[2])
                            mod = math.sqrt(x*x + y*y)
                            arg = math.atan2(y,x)
                            game.robot.acceleration_magnitude = mod / 10
                            game.robot.rotation = arg 
                except:
                    print "network data parsing error, original data follows"
                    print repr(data)
                    raise
            except socket.error:
                netdata = False
    
        # Spawn a new monster each second
        if index % 60 == 0:
            monster = Monster(game)
            game.monsters.add(monster)
            game.allsprites.add(monster)
            
        game.allsprites.update()
        screen.blit(bgimg, bgimg.get_rect())
        game.allsprites.draw(screen)
        display.flip()
        index += 1
    pygame.quit()
    
if __name__ == "__main__":
    game()