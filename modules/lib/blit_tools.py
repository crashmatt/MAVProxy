'''
Created on 24 Jun 2014

@author: matt
'''

import pygame


def blit_alpha(target, source, location, opacity):
        x = location[0]
        y = location[1]
        temp = pygame.Surface((source.get_width(), source.get_height())).convert()
        temp.blit(target, (-x, -y))
        temp.blit(source, (0, 0))
        temp.set_alpha(opacity)        
        target.blit(temp, location)

#buffer is a surface that has had surface.convert() applied to it
def blit_alpha_buffer(blit_buffer, target, source, location, opacity):
        x = location[0]
        y = location[1]
        blit_buffer.blit(target, (-x, -y))
        blit_buffer.blit(source, (0, 0))
        blit_buffer.set_alpha(opacity)        
        target.blit(blit_buffer, location)
