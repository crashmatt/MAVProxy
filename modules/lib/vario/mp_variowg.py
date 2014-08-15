"""
  variowg module.  Decides what sounds to make for a given climb rate.
  Sends the sound demand to a wave generator connected through a named pipe
"""

import math
import fluidsynth
import time

import threading, Queue
import sys,os

import socket
import json

#from scipy import interpolate
#from operator import itemgetter
 
#chunk = numpy.concatenate(chunks) * 0.25


class wavegen(threading.Thread):
    def __init__(self):     #, mpstate, addr="localhost", port="14560"
        threading.Thread.__init__(self)
        
#        self.port = port
#        self.addr = addr
        
#        self.mpstate = mpstate
        self._stop = threading.Event()
        
        self.txq = Queue.Queue(20)
    
    def stop(self):
        print("sound generator thread request stop\n")
        self._stop.set()

    def stopped(self):
        return not self.isAlive()

    def setVariable(self, module, varName, value):
        """ Set a variable value in the wave generator.
        Formats the text to send and adds it to a queue.
        The queue add is done from any thread.
        The actual send is performed in a the wavegen thread
        
        send string is
        module:variable name:value\n
        """
        sendstr = '{0}:{1}:{2}\n'.format(module, varName, value )
        try:
            self.txq.put(sendstr, True, 0.01)
        except:
            pass
        
    def run(self):
        print("wavegen communication thread starting\n")
        self._stop.clear()

        with open('/home/matt/workspace/wavegen/wavegen.fifo', 'a') as fifo:
            while( not self._stop.isSet() ):    # and (self.mpstate.status.exit == False)
                try:
                    txmsg = self.txq.get(True, 0.5)
                    fifo.write(txmsg)
                    fifo.flush()
                except:
                    pass
                        
        print("sound generator communication thread end\n")



def enum(*sequential, **named):
    """ not sure what this is for, legacy and hanging around"""
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


class vario():
    def __init__(self, mpstate):
        self.serialise_attribs = ["rising_deadband", "falling_deadband", "minRisingPulseFreq", "maxRisingPulseFreq", "risingPulseBand", "maxRate",
                   "minRate", "maxRisingFreq", "minRisingFreq", "maxFallingFreq", "minFallingFreq", "volume"]        

        self.wgen = wavegen()
        self.wgen.start()
        
        self.rising_deadband   = 0.0
        self.falling_deadband   = 0.5
        self.minRisingPulseFreq = 1.0
        self.maxRisingPulseFreq = 10.0
        self.risingPulseBand = 2.5
        self.maxRate    = 6.0
        self.minRate    = -4.0
        self.maxRisingFreq  = 2500.0
        self.minRisingFreq  = 800.0
        self.maxFallingFreq = 400.0
        self.minFallingFreq = 650.0
        
        self.volume = 0.5;
        
        self.filtered = 0;
        
        self.load()
        self.save()

    def __del__(self):
        self.soundGen.stop()
        
        self.minRisingPulsePeriod = 1.0
        self.maxRisingPulsePeriod = 0.1
        
    def filter(self, input):
        self.filtered += input
        self.filtered *= 0.5
        return self.filtered

    def setRate(self, rate):
        rate = self.filter(rate)
        
        if(rate > self.rising_deadband):
            if(rate < ( self.rising_deadband + self.risingPulseBand)):
                fdiff = self.maxRisingPulseFreq - self.minRisingPulseFreq
                pulsefreq = fdiff * (rate - self.rising_deadband) / self.risingPulseBand
                pulsefreq += self.minRisingPulseFreq
                pulseperiod = 1/pulsefreq
                self.wgen.setVariable("modulator","period", pulseperiod)
                val = "%5.2f" % self.minRisingFreq
                self.wgen.setVariable("wavegen","frequency",val)               
                self.wgen.setVariable("modulator","pulsing","true")
            elif(rate < self.maxRate):
                bandstart = self.rising_deadband + self.risingPulseBand
                freq = ( (rate-bandstart) * (self.maxRisingFreq - self.minRisingFreq) / (self.maxRate - bandstart)) + self.minRisingFreq
                val = "%5.2f" % freq
                self.wgen.setVariable("wavegen","frequency",val)
                self.wgen.setVariable("modulator","pulsing","true")
            else:
                val = "%5.2f" % self.maxRisingFreq
                self.wgen.setVariable("wavegen","frequency",val)
                self.wgen.setVariable("modulator","constant","true")
            
        elif(rate < -self.falling_deadband):
            if(rate < self.minRate):
                val = "%5.2f" % self.maxFallingFreq
                self.wgen.setVariable("wavegen","frequency", val)
                self.wgen.setVariable("modulator","period", "0.3")
                self.wgen.setVariable("modulator","pulsing","true")
            else:
                self.wgen.setVariable("modulator","constant","true")
                freq = rate+self.falling_deadband
                freq = freq / (self.minRate + self.falling_deadband)
                freq = freq * (self.minFallingFreq - self.maxFallingFreq)
                freq = self.minFallingFreq - freq
                val = "%5.2f" % freq
                self.wgen.setVariable("wavegen","frequency",val)
        else:
            self.wgen.setVariable("modulator", "mute", "0.0")
    
    def to_dict(self):
        d = dict({})
        for a in self.serialise_attribs:
            try:
                d[a] = getattr(self, a)
            except:
                pass
        return d

    def from_dict(self, attr_dict):
        for key in attr_dict:
            try:
                setattr(self, key, float(attr_dict[key]))
            except:
                pass

    def to_json(self):
        return json.dumps(self.to_dict())
    
    def save(self):
        print("saving vario to configuration")
        conf = file("varioconf.cfg","w")
        conf.write(self.to_json())
        conf.close()

    def from_json(self, filestr):
        self.from_dict(json.loads(filestr)) 

    def load(self):
        print("loading vario from configuration")
        try:
            conf = file("varioconf.cfg","r")
        except:
            return
        
        self.from_json(conf.read())
        conf.close()

           
