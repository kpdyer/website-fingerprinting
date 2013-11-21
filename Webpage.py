# This is a Python framework to compliment "Peek-a-Boo, I Still See You: Why Efficient Traffic Analysis Countermeasures Fail".
# Copyright (C) 2012  Kevin P. Dyer (kpdyer.com)
# See LICENSE for more details.

import random

class Webpage:
    def __init__( self, id ):
        self.__id = int(id)
        self.__traceSet = []

    def addTrace( self, trace ):
        self.__traceSet.append( trace )

    def getTrace( self, n ):
        return self.__traceSet[n]

    def getTraces( self ):
        return self.__traceSet

    def getId( self ):
        return self.__id

    def getBandwidth(self):
        totalBandwidth = 0
        for trace in self.getTraces():
            totalBandwidth += trace.getBandwidth()
        return totalBandwidth

    def getHistogram( self, direction = None, normalize = False ):
        histogram    = {}
        totalPackets = 0
        for trace in self.getTraces():
            traceHistogram = trace.getHistogram( direction, False )
            for key in traceHistogram.keys():
                if not histogram.get( key ):
                    histogram[key] = 0
                histogram[key] += traceHistogram[key]
                totalPackets   += traceHistogram[key]

        if normalize:
            for key in histogram:
                histogram[key] = (histogram[key] * 1.0) / totalPackets

        return histogram