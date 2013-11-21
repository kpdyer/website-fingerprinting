# This is a Python framework to compliment "Peek-a-Boo, I Still See You: Why Efficient Traffic Analysis Countermeasures Fail".
# Copyright (C) 2012  Kevin P. Dyer (kpdyer.com)
# See LICENSE for more details.

import config
import random
from Webpage import Webpage
from Trace import Trace
from Packet import Packet
import math

class Folklore:
    FIXED_PACKET_LEN    = 1000
    TIMER_CLOCK_SPEED   = 20
    MILLISECONDS_TO_RUN = 0

    class Buffer:
        def __init__(self):
            self.__array = []

        def queue(self):
            return self.__array

        def add(self,p):
            self.__array.append(p)

        def remove(self):
            if len(self.__array)==0:
                return None
            else:
                p = self.__array[0]
                del self.__array[0]
                return p

        def hasPackets(self):
            return (len(self.__array)>0)

    @staticmethod
    def packFromBuffer(outgoingCellCapacity, buffer):
        while outgoingCellCapacity>0:
            p = buffer.remove()
            if p and (p.getLength()-Packet.HEADER_LENGTH) > outgoingCellCapacity:
                newP = Packet( p.getDirection(), p.getTime(), (p.getLength()-Packet.HEADER_LENGTH)-outgoingCellCapacity )
                buffer.add(newP)
                break
            elif p and p.getLength() <= outgoingCellCapacity:
                outgoingCellCapacity -= (p.getLength()-Packet.HEADER_LENGTH)
            else:
                break

    @staticmethod
    def applyCountermeasure( trace ):
        return Folklore.doCountermeasure(trace)[0]

    @staticmethod
    def maxLatency( trace ):
        latencyList = Folklore.doCountermeasure(trace)[1]
        maxLatency = 0
        if len(latencyList)>0:
            maxLatency = max(latencyList)
        return maxLatency

    @staticmethod
    def doCountermeasure( trace ):
        # Median trace length in the herrmann dataset is 3500ms
        # Median throughput is 62000 bytes/second
        # 40*1500 = 60000 bytes/second

        newTrace = Trace(trace.getId())

        latency      = []
        timer        = 0
        bufferUP     = Folklore.Buffer()
        bufferDOWN   = Folklore.Buffer()
        packetCursor = 0

        # Terminate only if (1) our clock is up, (2) we have no more packets from the source
        # and (3) our buffers are empty
        while timer <= Folklore.MILLISECONDS_TO_RUN \
           or packetCursor < trace.getPacketCount() \
           or bufferUP.hasPackets() \
           or bufferDOWN.hasPackets():

            # calculate max latency
            if bufferUP.hasPackets():
                earliestPacket = bufferUP.queue()[0]
                latency.append( timer - earliestPacket.getTime() )
            if bufferDOWN.hasPackets():
                earliestPacket = bufferDOWN.queue()[0]
                latency.append( timer - earliestPacket.getTime() )

            # add to buffer: all packets that appeared since last clock
            while packetCursor < trace.getPacketCount()\
              and trace.getPackets()[packetCursor].getTime()<=timer:
                packet = trace.getPackets()[packetCursor]

                if packet.getDirection() == Packet.UP:
                    bufferUP.add( packet )
                elif packet.getDirection() == Packet.DOWN:
                    bufferDOWN.add( packet )

                # increment position in source buffer
                packetCursor += 1

            # check buffer UP: purge at most Packet.MTU bytes
            Folklore.packFromBuffer(Folklore.FIXED_PACKET_LEN-Packet.HEADER_LENGTH, bufferUP)

            # check buffer DOWN: purge at most Packet.MTU bytes
            Folklore.packFromBuffer(Folklore.FIXED_PACKET_LEN-Packet.HEADER_LENGTH, bufferDOWN)

            # send a byte in both directions
            newTrace.addPacket( Packet(Packet.DOWN, timer, Folklore.FIXED_PACKET_LEN ) )
            newTrace.addPacket( Packet(Packet.UP  , timer, Folklore.FIXED_PACKET_LEN ) )

            # go to the next clock cycle
            timer += Folklore.TIMER_CLOCK_SPEED
            
        return [newTrace,latency]
