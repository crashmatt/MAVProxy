'''
Created on 24 Jun 2014

@author: matt
'''

import pygame
import sys,os
import time
import threading, Queue
import math
import webcolors
import blit_tools

blue = (0,0,255)
red = (255,0,0)
green = (0,255,0)
purple = (150,0,150)
white = (255,255,255)
brown = webcolors.name_to_rgb("brown")


class hud(threading.Thread):
    def __init__(self,mpstate):
        threading.Thread.__init__(self)
        
        self.mpstate = mpstate
        self._stop = threading.Event()
        
        self.width = 640
        self.height = 480

        self.x0 = self.width / 2
        self.y0 = self.height / 2
        
        #Pitch ladder parameters
        self.pitch_ladder_height = 0.8 # percent of total screen height that it covers
        self.pitch_ladder_zero_bar_width =  0.164;
        self.pitch_ladder_zero_bar_thickness = 2;
        self.pitch_ladder_bar_width = 0.15;
        self.pitch_ladder_bar_thickness = 1;
        self.pitch_ladder_bar_gap = 0.04;
        self.pitch_ladder_step = 10;    # degrees
        self.pitch_ladder_step_height = 0.2
        self.pitch_ladder_text_xoffset = 0.01
        self.pitch_ladder_font_size = 15;
        self.pitch_ladder_font = "FreeMono"
        self.pitch_ladder_font_bold = True
        self.pitch_ladder_font_color = green
        self.pitch_ladder_upper_colour = blue
        self.pitch_ladder_lower_colour = brown
        self.pitch_ladder_zero_colour = white
        self.pitch_ladder_fade_pos = 0.3
         
        # gap between bar center and start of the bar
        self.bar_gap = (self.pitch_ladder_bar_gap * self.width * 0.5) #bar gap in abs units
        
        # attitude in radians
        self.roll = 0
        self.pitch = 0;
        self.yaw = 0;
        self.heading = 0;
        
    def close(self):
        self._stop.set()

        
#    def update_attitude(self,pitch,roll,yaw):

    def run(self):
        print("HUD thread starting")
        self._stop.clear()
        
        pygame.init()
        pygame.font.init()
        
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.NOFRAME | pygame.DOUBLEBUF, 32)
        # Beware - there be dragons -  | pygame.FULLSCREEN
        
        max_sprite_dim = self.ladder_text_sprite_gen()
        
        self.ladder_text_buffer = pygame.Surface((max_sprite_dim, max_sprite_dim)).convert()
         
        while( (not self._stop.isSet()) and (self.mpstate.status.exit == False) ):
            time.sleep(0.05);
            self.update_instruments()
            self.update_screen()
            
        pygame.display.quit()

        print("HUD thread end")
    
    def ladder_text_sprite_gen(self):
        # Load the fonts
        ladderfont = pygame.font.SysFont(self.pitch_ladder_font, self.pitch_ladder_font_size, self.pitch_ladder_font_bold)
        
        steps = 120 / self.pitch_ladder_step
        self.fontmap = []
        
        width = 0
        height = 0
        
        # Render all required angle steps. Get the largest sized text sizes to create rotation buffer.
        for angle in xrange(-steps, steps):
            step_angle = angle * self.pitch_ladder_step
            step_str = "%01d" % step_angle
            text = ladderfont.render(step_str, 1, self.pitch_ladder_font_color)
            text_rect = text.get_rect()
            if(text_rect.width > width):
                width = text_rect.width
            if(text_rect.height > height):
                height = text_rect.height
            self.fontmap.append( (step_angle, text) )
                
        #maximum dimension when sprite rotated to 45deg
        return int( math.sqrt( ((width*width)) + ((height*height))) + 2)


    def ladder_text_lookup(self, angle):
        for txt in self.fontmap:
            if(angle == txt[0] ):
                return txt[1]
        return self.fontmap[0][1]
        
    def update_instruments(self):
        self.roll = self.roll + (2 * math.pi / 360)
        self.pitch = self.pitch + (0.5 * math.pi / 360)
        if(self.roll > math.pi):
            self.roll -= math.pi * 2
        if(self.pitch > math.pi):
            self.pitch -= math.pi * 2


    # redraw the pitch ladder directly on the surface accelerated by pre-rendered text
    def redraw_pitch_ladder_direct(self):

        surface = self.screen
        
        degpitch = math.degrees(self.pitch)

        # Find the next angle step in the ladder down from the screen center
        steps_down = math.floor(degpitch / self.pitch_ladder_step)
        next_step_down =  steps_down * self.pitch_ladder_step                                               #degrees
        next_step_down_delta = degpitch - next_step_down                                                     #degrees        
        next_step_down_pos = next_step_down_delta * self.pitch_ladder_step_height / self.pitch_ladder_step   #relative
        
        # relative units
#        step_down_distance_to_center = degpitch * self.pitch_ladder_step_height / self.pitch_ladder_step
        top_steps = int(self.pitch_ladder_height / (self.pitch_ladder_step_height * 2))
        
        
        for step in xrange(-top_steps, top_steps):
            step_pos = (step * self.pitch_ladder_step_height) + next_step_down_pos      #relative

            # bar lengths in relative units
            if ((steps_down - step) == 0):
                bar_length = self.pitch_ladder_zero_bar_width - self.pitch_ladder_bar_gap
                bar_thickness = self.pitch_ladder_zero_bar_thickness
                text_offset = self.pitch_ladder_zero_bar_width + self.pitch_ladder_text_xoffset
                stepangle = 0
                bar_color = self.pitch_ladder_zero_colour
            else:
                bar_length = self.pitch_ladder_bar_width - self.pitch_ladder_bar_gap
                bar_thickness = self.pitch_ladder_bar_thickness
                text_offset = self.pitch_ladder_bar_width + self.pitch_ladder_text_xoffset
                stepangle = (steps_down - step) * self.pitch_ladder_step
                
                if((steps_down - step) < 0):
                    bar_color = self.pitch_ladder_lower_colour
                elif((steps_down - step) > 0):
                    bar_color = self.pitch_ladder_upper_colour
                 
            if(step_pos > self.pitch_ladder_fade_pos):
                max_pos = self.pitch_ladder_height * 0.5
                min_pos = self.pitch_ladder_fade_pos
                bar_fade = (max_pos - step_pos) / (max_pos - min_pos)
                if(bar_fade < 0):
                    bar_fade = 0
            elif(step_pos < -self.pitch_ladder_fade_pos):
                max_pos = -self.pitch_ladder_height * 0.5
                min_pos = -self.pitch_ladder_fade_pos
                bar_fade = (max_pos - step_pos) / (max_pos - min_pos)
                if(bar_fade < 0):
                    bar_fade = 0
            else:
                bar_fade = 1
                
            bc = ( int(bar_color[0] * bar_fade), int(bar_color[1] * bar_fade), int(bar_color[2] * bar_fade))
            bar_color = bc

            # bar centers in absolute units
            bar_y_offset = ( step_pos * self.height )
            bar_centre_x = ( bar_y_offset * math.sin(self.roll) ) + self.x0
            bar_centre_y = ( bar_y_offset * math.cos(self.roll) ) + self.y0
            
            text = self.ladder_text_lookup(stepangle)
            rot_text = pygame.transform.rotate(text, math.degrees(self.roll) )
            text_rect = rot_text.get_rect()
            text_center = text_rect.center
            
            # Draw right side line
            abs_bar_length = bar_length * self.width
            x1 = bar_centre_x + ( self.bar_gap * math.cos(self.roll) )
            y1 = bar_centre_y - ( self.bar_gap * math.sin(self.roll) )
            x2 = bar_centre_x + ( abs_bar_length * math.cos(self.roll) )
            y2 = bar_centre_y - ( abs_bar_length * math.sin(self.roll) )
            pygame.draw.line(surface, bar_color, (x1, y1), (x2, y2), bar_thickness)

            # Right side text
            x1 = bar_centre_x + ( (text_offset * self.width) * math.cos(self.roll)) - text_center[0]
            y1 = bar_centre_y - ( (text_offset * self.width) * math.sin(self.roll) ) - text_center[1]
            if(bar_fade < 1):
                blit_tools.blit_alpha_buffer(self.ladder_text_buffer, surface, rot_text, (x1, y1), bar_fade*255)
            else:
                surface.blit(rot_text, (x1,y1))
                
            #test circle at text position
            #pygame.draw.circle(surface, green, ( int(x1),int(y1) ), 10, 2)

#            x2 = x2 + (self.pitch_ladder_text_xoffset * self.width)
#            surface.blit(step_text, (x2 , y1-text_center[1]) )

            # Draw left side line
            x1 = bar_centre_x - ( self.bar_gap * math.cos(self.roll) )
            y1 = bar_centre_y + ( self.bar_gap * math.sin(self.roll) )
            x2 = bar_centre_x - ( abs_bar_length * math.cos(self.roll) )
            y2 = bar_centre_y + ( abs_bar_length * math.sin(self.roll) )            
            pygame.draw.line(surface, bar_color, (x1, y1), (x2, y2), bar_thickness)
            
            # Left side text
            x1 = bar_centre_x - (text_offset * self.width * math.cos(self.roll)) - text_center[0]
            y1 = bar_centre_y + (text_offset * self.width * math.sin(self.roll) ) - text_center[1]
            if(bar_fade < 1):
                blit_tools.blit_alpha_buffer(self.ladder_text_buffer, surface, rot_text, (x1, y1), bar_fade*255)
            else:
                surface.blit(rot_text, (x1,y1))


    def update_screen(self):
        screen = self.screen
        
        screen.fill((0, 0, 0, 255))
        
        self.redraw_pitch_ladder_direct()        
        
        pygame.display.flip()

        event = pygame.event.poll()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._stop.set()
            if event.type == pygame.KEYDOWN:
                self._stop.set()
            

#===============================================================================
# 
# def blit_alpha(target, source, location, opacity):
#        x = location[0]
#        y = location[1]
#        temp = pygame.Surface((source.get_width(), source.get_height())).convert()
#        temp.blit(target, (-x, -y))
#        temp.blit(source, (0, 0))
#        temp.set_alpha(opacity)        
#        target.blit(temp, location)
# 
# #buffer is a surface that has had surface.convert() applied to it
# def blit_alpha_buffer(blit_buffer, target, source, location, opacity):
#        x = location[0]
#        y = location[1]
#        blit_buffer.blit(target, (-x, -y))
#        blit_buffer.blit(source, (0, 0))
#        blit_buffer.set_alpha(opacity)        
#        target.blit(blit_buffer, location)
#===============================================================================
