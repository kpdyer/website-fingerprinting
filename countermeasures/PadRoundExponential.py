# This is a Python framework to compliment "Peek-a-Boo, I Still See You: Why Efficient Traffic Analysis Countermeasures Fail".
# Copyright (C) 2012  Kevin P. Dyer (kpdyer.com)
# See LICENSE for more details.

import random

from Trace import Trace
from Packet import Packet

class PadRoundExponential:
    @staticmethod
    def applyCountermeasure(trace):
        newTrace = Trace(trace.getId())
        for packet in trace.getPackets():
            newPacket = Packet( packet.getDirection(),
                                packet.getTime(),
                                PadRoundExponential.calcLength(packet.getLength()) )
            newTrace.addPacket( newPacket )

        return newTrace

    @staticmethod
    def calcLength(packetLength):
        VALID_PACKETS = [128,256,512,1024,1500]
        retVal = 0
        for val in VALID_PACKETS:
            if packetLength<=val:
                retVal = val
                break

        return retVal