#!/usr/bin/env python
'''rfkill module
  
'''

import sys, threading, os, dbus


mpstate = None

def device_list():
    os.remove("/tmp/rfkill_list")
    os.system("rfkill list >> /tmp/rfkill_list")
    listfile = open("/tmp/rfkill_list")
    mpstate.rfkill_devices = []
    for line in listfile.readlines():
        parts = line.split(":")
        if(len(parts) == 3):
            parts[2] = parts[2].strip("\n")
            mpstate.rfkill_devices.append(parts)
            
def rfkill_set_all(block=True):
    for devtype in mpstate.rfkill_list:
        rfkill_set(devtype, block)    

def rfkill_set(devtype, block=True):
    for device in mpstate.rfkill_devices:
        if(devtype in device[1]):
            if(block):
                cmd = "rfkill block " + device[0]
            else:
                cmd = "rfkill unblock " + device[0]
            os.system(cmd)

def idle_task():
    if(getattr(mpstate, "rfkill_gokill", None ) is not None):
        if(mpstate.rfkill_gokill.is_set()):
            mpstate.rfkill_gokill.clear()
            rfkill_set_all(block=True)
            
def unload():
    rfkill_set_all(block=False)

            
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
    mpstate.rfkill_list = ["phy0"]
    mpstate.rfkill = None
    mpstate.rfkill_active = threading.Event()
    mpstate.rfkill_gokill = threading.Event()
    mpstate.rfkill_active.clear()
    mpstate.rfkill_gokill.clear()
    
    device_list();
    print mpstate.rfkill_devices 

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
    
        