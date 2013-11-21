# This is a Python framework to compliment "Peek-a-Boo, I Still See You: Why Efficient Traffic Analysis Countermeasures Fail".
# Copyright (C) 2012  Kevin P. Dyer (kpdyer.com)
# See LICENSE for more details.

import random

from Trace import Trace
from Packet import Packet

class PadRand:
    @staticmethod
    def applyCountermeasure(trace):
        newTrace = Trace(trace.getId())
        for packet in trace.getPackets():
            length = Packet.MTU
            if Packet.MTU-packet.getLength()>0:
                length = packet.getLength()+random.choice(range(0,Packet.MTU-packet.getLength(),8))
            newPacket = Packet( packet.getDirection(),
                                packet.getTime(),
                                length )
            newTrace.addPacket( newPacket )

        return newTrace