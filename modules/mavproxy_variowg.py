"""
  MAVProxy vario module
  Connects mavproxy to a vario, generating sound according to climb rate
  Starts a thread which uses the mp_variowg module to connect to an audio waveform generator.
"""

import mavutil, re, os, sys, threading, time

mpstate = None

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib', 'vario'))
import mp_variowg


class vario_manager(object):
    def __init__(self, mpstate):
        self.mpstate = mpstate
        
        self.unload = threading.Event()
        self.unload.clear()

        self.app_thread = threading.Thread(target=self.vario_app)
        self.app_thread.daemon = True
        self.app_thread.start()
        
        self.timeout_time = 0;
        self.vz_update_frame = 0;
        self.vz_update_period = time.time()
        self.vz_update_time = 0
        
        self.filtered = 0;
        
    def update_timeout(self):
        self.timeout_time = time.time() + 1.0;
        self.vz_update_frame += 1
        if(self.vz_update_frame >= 10):
            self.vz_update_period = (time.time() - self.vz_update_time) * 0.1
            self.vz_update_time = time.time()
            self.vz_update_frame = 0;
            
    def vario_app(self):
        
        # Find aircraft name argument from mavproxy options
        args = sys.argv[1:]
        self.aircraft = filter(lambda x: '--aircraft' in x,args)
        if(len(self.aircraft) < 1):
            aircraft = ""
        else:
            self.aircraft = self.aircraft[0]
            splt = self.aircraft.split("=")
            if(len(splt) == 2):
                aircraft = splt[1]
            else:
                aircraft = ""

        self.vario = mp_variowg.vario(name=aircraft)
                
        mpstate.vario_initialised = True
        print("vario initialised")        
        
        while ( (not mpstate.status.exit) and (not self.unload.is_set()) ):        
            time.sleep(0.1)
            if(time.time() > self.timeout_time):
                self.vario.setRate(0)
            
        mpstate.vario_initialised = False
        self.vario.stop()
        self.vario.join()
        self.vario = None
        print("vario closed")        

        
def name():
    '''return module name'''
    return "vario"

def description():
    '''return module description'''
    return "variometer"

def cmd_vario(args):
    '''vario command'''
    if(mpstate.vario_initialised == False):
        return
    usage = "vario param value"
    if(len(args) < 1):
         return
    if(args(0) == "volume"):
        mpstate.vario_manager.vario.setAmplitude(float(args(1)))

    

#===============================================================================
#    state = mpstate.graph_state
# 
#    if len(args) == 0:
#        # list current graphs
#        for i in range(len(state.graphs)):
#            print("Graph %u: %s" % (i, state.graphs[i].fields))
#        return
# 
#    # start a new graph
#    state.graphs.append(Graph(args[:]))
#===============================================================================


def init(_mpstate):
    '''initialise module'''
    global mpstate
    mpstate = _mpstate

    mpstate.vario_initialised = False
    mpstate.vario_manager = vario_manager(mpstate)
    
    mpstate.command_map['vario'] = (cmd_vario, "vario settings adjust")

def unload():
    '''unload module'''
    mpstate.vario_manager.unload.set()
        
def mavlink_packet(msg):
    '''handle an incoming mavlink packet'''
                #===============================================================
                # if msg and msg.get_type() == "HEARTBEAT":
                #    print(msg)        
                #    system = msg.get_srcSystem()
                #    component = msg.get_srcComponent()
                #    print("Heartbeat from UDB (system %u component %u)" % (system, component))
                #    if((system == mpstate.system) and (component == mpstate.component)):
                #        mpstate.heartbeat_ok = True
                #        mpstate.heartbeat_timer = time.time()
                #===============================================================

    if msg and msg.get_type() == "GLOBAL_POSITION_INT":
        try:
            vz = msg.vz             # inverted vertical velocity in cm/s
            vz = int(-vz) * 0.01    # vertical velocity in m/s 
        except:
            print("decode global vz message fail")
        try:
            if(mpstate.vario_initialised == True):
                mpstate.vario_manager.vario.setRate(vz)
                mpstate.vario_manager.update_timeout()
        except:
            print("vario callback fail")
    return
            
#===============================================================================
# 
# class healthcheck(threading.Thread):
#    def __init__(self, _mpstate):
#        threading.Thread.__init__(self)
#        self._stop = threading.Event()
#        global mpstate
#        mpstate = _mpstate
# 
#        
#    def run(mpstate):
#        while ( (not mpstate.status.exit) and (not self._stop.isSet()) ):
#            time.sleep(0.5)
#===============================================================================
        

