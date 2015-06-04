#!/usr/bin/env python
'''rfkill module

Using fork of python-rfkill library by Evgeni Golov in modules/lib:
original work here: https://github.com/evgeni/python-rfkill
  
'''

import sys, threading, os, dbus

#sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib', 'python-rfkill'))
#import RFKillSwitch from rfkill

mpstate = None


def idle_task():
    if(getattr(mpstate, "rfkill_gokill", None ) is not None):
        if(mpstate.rfkill_gokill.is_set()):
            for dev in mpstate.rfkill_list:
                killcmd = "rfkill block " + dev
                os.system(killcmd)
            mpstate.rfkill_gokill.clear()
            
def unload():
    if(getattr(mpstate, "rfkill_list", None ) is not None):
        for dev in mpstate.rfkill_list:
            killcmd = "rfkill unblock " + dev
            os.system(killcmd)
        mpstate.rfkill_list = []
    

            
def name():
    '''return module name'''
    return "rfkill"

def description():
    '''return module description'''
    return "rfkill"

def mavlink_packet(pkt):
    if(getattr(mpstate, "rfkill_active", None ) is not None):
        if(not mpstate.rfkill_active.is_set()):
            mpstate.rfkill_active.set()
            mpstate.rfkill_gokill.set()
                        

def init(_mpstate):
    global mpstate
    mpstate = _mpstate
    mpstate.command_map['rfkill'] = (cmd_rfkill, "rfkill commands")
    mpstate.rfkill_list = ['1']
    mpstate.rfkill = None
    mpstate.rfkill_active = threading.Event()
    mpstate.rfkill_gokill = threading.Event()
    mpstate.rfkill_active.clear()
    mpstate.rfkill_gokill.clear()

def cmd_rfkill(args):
    '''rfkill command'''
    usage = "rfkill add [number]"
    if(len(args) != 2):
        return
    if(args[0] == "add"):
        if(not args[1] in mpstate.rfkill_list):
            mpstate.rfkill_list.Add(args[1])
        
#    if(args[0] == "wifi"):
#    if(args[0] == "bluetooth"):
    
        