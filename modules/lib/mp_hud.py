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
        self.pitch_ladder_zero_bar_width =  0.3;
        self.pitch_ladder_zero_bar_thickness = 2;
        self.pitch_ladder_bar_width = 0.25;
        self.pitch_ladder_bar_thickness = 1;
        self.pitch_ladder_bar_gap = 0.08;
        self.pitch_ladder_step = 10;    # degrees
        self.pitch_ladder_step_height = 0.2
        self.pitch_ladder_text_xoffset = 0.025
        self.pitch_ladder_font_size = 15;
        self.pitch_ladder_font = "FreeMono"
        self.pitch_ladder_font_bold = True
        self.pitch_ladder_upper_colour = blue
        self.pitch_ladder_lower_colour = brown
        self.pitch_ladder_zero_colour = white
        self.pitch_ladder_fade_pos = 0.3
         
        
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
        
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.NOFRAME | pygame.DOUBLEBUF)
        # Beware - there be dragons -  | pygame.FULLSCREEN
         
        while( (not self._stop.isSet()) and (self.mpstate.status.exit == False) ):
            time.sleep(0.05);
            self.update_instruments()
            self.update_screen()
            
        pygame.display.quit()

        print("HUD thread end")
            
        
    def update_instruments(self):
        self.roll = self.roll + (2 * math.pi / 360)
        self.pitch = self.pitch + (0.5 * math.pi / 360)
        if(self.roll > math.pi):
            self.roll -= math.pi * 2
        if(self.pitch > math.pi):
            self.pitch -= math.pi * 2

    # redraw the pitch ladder using rotated surface method
    def redraw_pitch_ladder_rot(self):
        surface = pygame.Surface(self.screen.get_size())
        #screen center
        
        degpitch = math.degrees(self.pitch)

        # Find the next angle step in the ladder down from the screen center
        steps_down = math.floor(degpitch / self.pitch_ladder_step)
        next_step_down =  steps_down * self.pitch_ladder_step                                               #degrees
        next_step_down_delta = degpitch - next_step_down                                                     #degrees        
        next_step_down_pos = next_step_down_delta * self.pitch_ladder_step_height / self.pitch_ladder_step   #relative
        
        # relative units
        step_down_distance_to_center = degpitch * self.pitch_ladder_step_height / self.pitch_ladder_step
        top_steps = int(self.pitch_ladder_height / (self.pitch_ladder_step_height * 2))
        
        # Load the font
        ladderfont = pygame.font.SysFont(self.pitch_ladder_font, self.pitch_ladder_font_size, self.pitch_ladder_font_bold)
        
        for step in xrange(-top_steps, top_steps+1):
            step_pos = (step * self.pitch_ladder_step_height) + next_step_down_pos      #relative

            # bar lengths in relative units
            if ((steps_down - step) == 0):
                bar_delta_x = ( (self.pitch_ladder_zero_bar_width - self.pitch_ladder_bar_gap) * 0.5)
                bar_thickness = self.pitch_ladder_zero_bar_thickness
                step_str = "0" 
                bar_color = self.pitch_ladder_zero_colour
            else:
                bar_delta_x = ( (self.pitch_ladder_bar_width - self.pitch_ladder_bar_gap) * 0.5)
                bar_thickness = self.pitch_ladder_bar_thickness
                stepangle = (steps_down - step) * self.pitch_ladder_step
                step_str = "%02d" % stepangle
                
                if((steps_down - step) < 0):
                    bar_color = self.pitch_ladder_lower_colour
                elif((steps_down - step) > 0):
                    bar_color = self.pitch_ladder_upper_colour
                 
            if(step_pos > self.pitch_ladder_fade_pos):
                max = self.pitch_ladder_height * 0.5
                min = self.pitch_ladder_fade_pos
                bar_fade = (max - step_pos) / (max - min)
                if(bar_fade < 0):
                    bar_fade = 0
            elif(step_pos < -self.pitch_ladder_fade_pos):
                max = -self.pitch_ladder_height * 0.5
                min = -self.pitch_ladder_fade_pos
                bar_fade = (max - step_pos) / (max - min)
                if(bar_fade < 0):
                    bar_fade = 0
            else:
                bar_fade = 1
                
            bc = ( int(bar_color[0] * bar_fade), int(bar_color[1] * bar_fade), int(bar_color[2] * bar_fade))
            bar_color = bc
                
            step_text = ladderfont.render(step_str, 1, red)
            text_rect = step_text.get_rect()
            text_center = text_rect.center
            
            # Draw right side line and text
            x1 = (self.pitch_ladder_bar_gap * self.width * 0.5) + self.x0
            y1 = (step_pos * self.height) + self.y0
            x2 = x1 + (bar_delta_x * self.width)
            y2 = y1
            
            pygame.draw.line(surface, bar_color, (x1, y1), (x2, y2), bar_thickness)

            x2 = x2 + (self.pitch_ladder_text_xoffset * self.width)
            surface.blit(step_text, (x2 , y1-text_center[1]) )

            # Draw left side line and text
            x1 = (-self.pitch_ladder_bar_gap * self.width * 0.5) + self.x0
            x2 = x1 - (bar_delta_x * self.width)
            
            pygame.draw.line(surface, bar_color, (x1, y1), (x2, y2), bar_thickness)
            x2 = x2 - (text_center[0]*2) - (self.pitch_ladder_text_xoffset * self.width)
            surface.blit(step_text, (x2 , y1-text_center[1]) )
            
            
#            surface.blit(step_text, (self.x0 - text_center[0], y1-text_center[1]) )
            
        
#        surface = pygame.transform.rotate(surface, math.degrees(self.roll))
        rot_surface = pygame.transform.rotate(surface, math.degrees(self.roll))
        rot_rect = rot_surface.get_rect()
        rot_rect.center = self.screen.get_rect().center
        
        self.screen.blit(rot_surface, rot_rect)
            
        
    def redraw_pitch_ladder(self):
        screen = self.screen
        #screen center
        
        degpitch = math.degrees(self.pitch)

        # Find the next angle step in the ladder down from the screen center
        steps_down = math.floor(degpitch / self.pitch_ladder_step)
        next_step_down =  steps_down * self.pitch_ladder_step               #degrees
        next_step_down_delta = degpitch - next_step_down                                                     #degrees        
        next_step_down_pos = next_step_down_delta * self.pitch_ladder_step_height / self.pitch_ladder_step   #relative
        
        # relative units
        step_down_distance_to_center = degpitch * self.pitch_ladder_step_height / self.pitch_ladder_step
        top_steps = int(self.pitch_ladder_height / (self.pitch_ladder_step_height * 2))
            
        
        for step in xrange(-top_steps, top_steps+1):
            step_pos = (step * self.pitch_ladder_step_height) + next_step_down_pos      #relative

            # bar lengths in relative units
            if ((steps_down - step) == 0):
                bar_delta_x = (self.pitch_ladder_zero_bar_width * math.cos(self.roll) * 0.5)
                bar_delta_y = (self.pitch_ladder_zero_bar_width * -math.sin(self.roll) * 0.5)
            else:
                bar_delta_x = (self.pitch_ladder_bar_width * math.cos(self.roll) * 0.5)
                bar_delta_y = (self.pitch_ladder_bar_width * -math.sin(self.roll) * 0.5)


            bar_centre_x = (step_pos * math.sin(self.roll) )
            bar_centre_y = (step_pos * math.cos(self.roll) )
            
            x1 = (bar_centre_x * self.height) + self.x0
            y1 = (bar_centre_y * self.height) + self.y0

            x2 = x1 + (bar_delta_x * self.width)
            y2 = y1 + (bar_delta_y * self.width)

            x3 = x1 - (bar_delta_x * self.width)
            y3 = y1 - (bar_delta_y * self.width)

            pygame.draw.line(screen, white, (x1, y1), (x2, y2), 1)
            pygame.draw.line(screen, white, (x1, y1), (x3, y3), 1)
            

    def update_screen(self):
        screen = self.screen
        
        screen.fill((0, 0, 0))
        
        self.redraw_pitch_ladder_rot()
        
        pygame.display.flip()

        event = pygame.event.poll()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._stop.set()
            if event.type == pygame.KEYDOWN:
                self._stop.set()
            