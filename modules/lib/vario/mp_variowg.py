import math
import fluidsynth
import time

import threading, Queue
import sys,os

import socket

#from scipy import interpolate
#from operator import itemgetter
 
#chunk = numpy.concatenate(chunks) * 0.25


class wavegen(threading.Thread):
    def __init__(self, mpstate, addr="localhost", port="14560"):
        threading.Thread.__init__(self)
        
        self.port = port
        self.addr = addr
        
        self.mpstate = mpstate
        self._stop = threading.Event()
        
        self.txq = Queue.Queue(20)
    
    def stop(self):
        print("sound generator thread request stop\n")
        self._stop.set()

    def stopped(self):
        return not self.isAlive()

    def setVariable(self, module, varName, value):
        sendstr = '["{0}":"{1}":"{2}"]\n'.format(module, varName, value )
        try:
            self.txq.put(sendstr, True, 0.01)
        except:
            pass
        
    def run(self):
        print("wavegen communication thread starting\n")
        self._stop.clear()

        #=======================================================================
        # try:
        #     sock = socket.socket(socket.AF_INET, # Internet
        #                          socket.SOCK_DGRAM) # UDP
        # except:
        #     printf("wavegen failed to open socket")
        #     return            
        # fd
        # while( (not self._stop.isSet()) and (self.mpstate.status.exit == False) ):
        #     try:
        #         txmsg = self.txq.get(True, 0.01)
        #         sock.sendto( txmsg, (self.addr, self.port) )
        #     except:
        #         pass
        #=======================================================================

        with open('/home/matt/workspace/wavegen/wavegen.fifo', 'a') as fifo:
            while( (not self._stop.isSet()) and (self.mpstate.status.exit == False) ):
                try:
                    txmsg = self.txq.get(True, 0.5)
                    fifo.write(txmsg)
                    fifo.flush()
                except:
                    pass
        
        print("sound generator thread end\n")



def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


class vario():
    def __init__(self, mpstate):
        self.wgen = wavegen(mpstate)
        self.wgen.start()
        
        self.rising_deadband   = 0.0
        self.falling_deadband   = 0.5
        self.maxRate    = 4.0
        self.minRate    = -4.0
        self.maxRisingFreq  = 2500.0
        self.minRisingFreq  = 1000.0
        self.maxFallingFreq = 400.0
        self.minFallingFreq = 650.0
        
        self.volume = 0.5;

    def __del__(self):
        self.soundGen.stop()
        
    def setRate(self, rate):
        if(rate > self.rising_deadband):
            if(rate < self.maxRate):
                self.soundGen.setKey( ( (rate-self.rising_deadband) * (self.maxRisingFreq - self.minRisingFreq) / (self.maxRate - self.rising_deadband)) + self.minRisingKey)
                self.soundGen.setPulsing(True)
            else:
                self.soundGen.setKey(self.maxRisingKey)
                self.soundGen.setPulsing(False)
            self.soundGen.setAmplitude(self.volume)
            
        elif(rate < -self.falling_deadband):
            if(rate < self.minRate):
                self.soundGen.setKey(self.maxFallingKey)
                self.soundGen.setPulsing(True)
                self.soundGen.setAmplitude(self.volume)
            else:
                self.soundGen.setPulsing(False)
                freq = rate+self.deadband
                freq = freq / (self.minRate + self.falling_deadband)
                freq = freq * (self.maxFallingFreq - self.minFallingFreq)
                freq = self.minFallingFreq - freq
                self.soundGen.setKey( freq )
                self.soundGen.setAmplitude(self.volume)
        else:
            self.wgen.setVariable("wavegen", "amplitude", "0.0")
    


           
