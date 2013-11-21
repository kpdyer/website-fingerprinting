# This is a Python framework to compliment "Peek-a-Boo, I Still See You: Why Efficient Traffic Analysis Countermeasures Fail".
# Copyright (C) 2012  Kevin P. Dyer (kpdyer.com)
# See LICENSE for more details.

from Trace import Trace
from Packet import Packet

class PadToMTU:
    @staticmethod
    def applyCountermeasure(trace):
        newTrace = Trace(trace.getId())
        # pad all packets to the MTU
        for packet in trace.getPackets():
            newPacket = Packet( packet.getDirection(),
                                packet.getTime(),
                                Packet.MTU )
            newTrace.addPacket( newPacket )

        return newTrace