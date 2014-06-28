"""
  MAVProxy heads up display module


"""

import mavutil, re, os, sys, threading, time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'))
import mp_hud

mpstate = None

class hud_manager(object):
    def __init__(self, mpstate):
        self.mpstate = mpstate
        self.mpstate.hud_initialised = False
        
        self.unload = threading.Event()
        self.unload.clear()

        self.monitor_thread = threading.Thread(target=self.hud_app)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    
    def hud_app(self):
        self.hud = mp_hud.hud(mpstate)
        print("hud initialised")
        self.hud.start()

        self.mpstate.hud_initialised = True
                    
        while ( (not mpstate.status.exit) and (not self.unload.is_set()) ):
            time.sleep(1)
        
        self.hud.stop()
        self.hud.join()
        self.hud = None
        self.mpstate.hud_initialised = False
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
    mpstate.hud_manager.unload.set()
        
def mavlink_packet(msg):
    '''handle an incoming mavlink packet'''
    
 
            