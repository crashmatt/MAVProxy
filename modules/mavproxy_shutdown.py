#!/usr/bin/env python
'''joypad interface module

Adapted from work by AndrewF:
  http://diydrones.com/profile/AndrewF

'''

import sys

mpstate = None


def idle_task():
    pass

def name():
    '''return module name'''
    return "shutdown command"

def description():
    '''return module description'''
    return "implement mavproxy shutdown command"

def mavlink_packet(pkt):
    pass

def init(_mpstate):
    global mpstate
    mpstate = _mpstate
    mpstate.command_map['shutdown'] = (cmd_shutdown, "shutdown commands")

def cmd_shutdown(args):
    '''variowg command'''
    usage = "shutdown param value"
    if(len(args) != 1):
         return
    if(args[0] == "now"):
        mpstate.status.exit = True
#        sys.exit(1)
        