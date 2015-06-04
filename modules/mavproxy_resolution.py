#!/usr/bin/env python
'''rfkill module
  
'''

import sys, threading, os, dbus


mpstate = None

def set_resolution(res):
    rescmd = "xrandr -s "  + res
    os.system(rescmd)
    

def idle_task():
    if(getattr(mpstate, "resolution_gores", None ) is not None):
        if(mpstate.resolution_gores.is_set()):
            mpstate.resolution_gores.clear()
            set_resolution(mpstate.auto_resolution)
            
def unload():
    pass

            
def name():
    '''return module name'''
    return "resolution"

def description():
    '''return module description'''
    return "resolution"

def mavlink_packet(pkt):
    if(getattr(mpstate, "resolution_auto_done", None ) is not None):
        if(not mpstate.resolution_auto_done.is_set()):
            mpstate.resolution_gores.set()
            mpstate.resolution_auto_done.set()                        

def init(_mpstate):
    global mpstate
    mpstate = _mpstate
    mpstate.command_map['resolution'] = (cmd_resolution, "resolution commands")
    mpstate.auto_resolution = "800x600"
    mpstate.resolution_gores = threading.Event()
    mpstate.resolution_auto_done = threading.Event()
    mpstate.resolution_gores.clear()
    mpstate.resolution_auto_done.clear()

def cmd_resolution(args):
    '''resolution command'''
#    usage = "rfkill add [number]"
    if(len(args) != 2):
        return
    if(args[0] == "auto"):
        mpstate.auto_resolution = args[1]
    if(args[0] == "set"):
        set_resolution(args[1])
        
#    if(args[0] == "wifi"):
#    if(args[0] == "bluetooth"):
    
        