"""
  MAVProxy heads up display module


"""

import mavutil, re, os, sys, time, threading
import math
#import pdb

#from subprocess import Popen, PIPE, STDOUT
from multiprocessing import Process, Queue
#from threading import Thread

#sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'))
#import mp_hud

sys.path.insert(0, os.path.join('/','home','matt','pi', 'demos'))
import HUD

mpstate = None

class hud_manager(object):
    def __init__(self, mpstate):
        self.mpstate = mpstate
        self.mpstate.hud_initialised = False
        
        self.unload = threading.Event()
        self.unload.clear()

        self.update_queue = Queue(100)

#        self.hud_thread = threading.Thread(target=self.hud_app)
#        self.hud_thread.daemon = True
#        self.hud_thread.start()

        self.hud_process = Process(target=self.hud_app)
        self.hud_process.daemon = False
        self.hud_process.start()

        
    def set_variable(self, var_name, value):
        try:
            self.update_queue.put_nowait((var_name, value))
        except:
            print("Queue full")
            
    def hud_quit(self):
        mpstate.hud_manager.set_variable("quit", True)
        
        
    def hud_app(self):
        print("hud initialised")

        self.mpstate.hud_initialised = True
                    
        self.hud = HUD.HUD(master=False, update_queue=self.update_queue)
        self.hud.run_hud()

#        while ( (not mpstate.status.exit) and (not self.unload.is_set()) ):
#            time.sleep(1)
        
 
        self.mpstate.hud_initialised = False
        self.hud = None
        print("hud closed")  
    

def name():
    '''return module name'''
    return "hud"

def description():
    '''return module description'''
    return "heads up display"

def cmd_hud(args):
    '''hud command'''
    state = mpstate.hud_state

    if len(args) == 0:
        return

    elif args[0] == "help":
        print("hud <width|height>")
    elif args[0] == "width":
        if len(args) == 1:
            print("width: %.1f" % state.width)
            return
        state.width = int(args[1])
    elif args[0] == "height":
        if len(args) == 1:
            print("height: %.1f" % state.height)
            return
        state.height = int(args[1])


def init(_mpstate):
    '''initialise module'''
    global mpstate
    mpstate = _mpstate
    mpstate.hud_manager = hud_manager(mpstate)
    

def unload():
    '''unload module'''
    mpstate.hud_manager.hud_quit()
        
def mavlink_packet(msg):
    '''handle an incoming mavlink packet'''
    
    if(not msg):
        return
    if msg.get_type() == "GLOBAL_POSITION_INT":
        vz = msg.vz   # vertical velocity in cm/s
        vz = float(vz) * 0.6  #vz in meters/min
        mpstate.hud_manager.set_variable("vertical_speed", vz)

        #convert groundspeed to km/hr
#        groundspeed = math.sqrt((msg.vx*msg.vx) + (msg.vy*msg.vy) + (msg.vz*msg.vz)) * 0.0036
#        mpstate.hud_manager.set_variable("groundspeed", groundspeed)
        
        mpstate.hud_manager.set_variable("agl", msg.relative_alt)
        
        
    elif msg.get_type() == "VFR_HUD":
        mpstate.hud_manager.set_variable("heading", msg.heading)
        
        mpstate.hud_manager.set_variable("groundspeed", msg.groundspeed)
        mpstate.hud_manager.set_variable("tas", msg.airspeed)

    elif msg.get_type() == "ATTITUDE":
        mpstate.hud_manager.set_variable("roll", math.degrees(msg.roll))
        mpstate.hud_manager.set_variable("pitch", math.degrees(msg.pitch))
        
            