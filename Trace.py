# This is a Python framework to compliment "Peek-a-Boo, I Still See You: Why Efficient Traffic Analysis Countermeasures Fail".
# Copyright (C) 2012  Kevin P. Dyer (kpdyer.com)
# See LICENSE for more details.

import math
import config
from Packet import Packet

class Trace:
    def __init__(self,id):
        self.__packetArray   = []
        self.__id            = id
        self.__histogramUp   = {}
        self.__histogramDown = {}
        self.__packetsUp     = 0
        self.__packetsDown   = 0
        self.__filePath      = None
        self.__year          = 0
        self.__month         = 0
        self.__day           = 0
        self.__hour          = 0

    def getId(self): return self.__id

    def getPacketCount( self, direction = None ):
        return len(self.getPackets(direction))

    def getPackets( self, direction = None ):
        retArray = []
        for packet in self.__packetArray:
            if direction == None or packet.getDirection() == direction:
                retArray.append( packet )
        return retArray

    def addPacket( self, packet ):
        # Completely ignore ACK packets
        if config.IGNORE_ACK and packet.getLength() == Packet.HEADER_LENGTH:
            return self.__packetArray

        key = str(packet.getDirection())+'-'+str(packet.getLength())

        if packet.getDirection()==Packet.UP:
            self.__packetsUp += 1
            if not self.__histogramUp.get( key ):
                self.__histogramUp[key] = 0
            self.__histogramUp[key] += 1
        elif packet.getDirection()==Packet.DOWN:
            self.__packetsDown += 1
            if not self.__histogramDown.get( key ):
                self.__histogramDown[key] = 0
            self.__histogramDown[key] += 1

        return self.__packetArray.append( packet )

    def getBandwidth( self, direction = None ):
        totalBandwidth = 0
        for packet in self.getPackets():
            if (direction == None or direction == packet.getDirection()) and packet.getLength() != Packet.HEADER_LENGTH:
                totalBandwidth += packet.getLength()

        return totalBandwidth

    def getTime( self, direction = None ):
        timeCursor = 0
        for packet in self.getPackets():
            if direction == None or direction == packet.getDirection():
                timeCursor = packet.getTime()

        return timeCursor

    def getHistogram( self, direction = None, normalize = False ):
        if direction == Packet.UP:
            histogram = dict(self.__histogramUp)
            totalPackets = self.__packetsUp
        elif direction == Packet.DOWN:
            histogram = dict(self.__histogramDown)
            totalPackets = self.__packetsDown
        else:
            histogram = dict(self.__histogramUp)
            for key in self.__histogramDown:
                histogram[key] = self.__histogramDown[key]
            totalPackets = self.__packetsDown + self.__packetsUp

        if normalize==True:
            for key in histogram:
                histogram[key] = (histogram[key] * 1.0) / totalPackets

        return histogram

    def calcL1Distance( self, targetDistribution, filterDirection=None ):
        localDistribution  = self.getHistogram( filterDirection, True )

        keys = localDistribution.keys()
        for key in targetDistribution:
            if key not in keys:
                keys.append( key )

        distance = 0
        for key in keys:
            l = localDistribution.get(key)
            r = targetDistribution.get(key)

            if l == None and r == None: continue
            if l == None: l = 0
            if r == None: r = 0

            distance += math.fabs( l - r )

        return distance

    def getMostSkewedDimension( self, targetDistribution ):
        localDistribution  = self.getHistogram( None, True )

        keys = targetDistribution.keys()

        worstKey = None
        worstKeyDistance = 0

        for key in keys:
            l = localDistribution.get(key)
            r = targetDistribution.get(key)

            if l == None: l = 0
            if r == None: r = 0

            if worstKey==None or (r - l) > worstKeyDistance:
                worstKeyDistance = r - l
                worstKey = key

        bits = worstKey.split('-')

        return [int(bits[0]),int(bits[1])]
