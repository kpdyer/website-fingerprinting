# This is a Python framework to compliment "Peek-a-Boo, I Still See You: Why Efficient Traffic Analysis Countermeasures Fail".
# Copyright (C) 2012  Kevin P. Dyer (kpdyer.com)
# See LICENSE for more details.

import config
import random
from Webpage import Webpage
from Trace import Trace
from Packet import Packet

class DirectTargetSampling:
    L1_THRESHHOLD = 0.3
    @staticmethod
    def buildMetadata( srcWebpage, targetWebpage ):
        targetDistributionBi     = targetWebpage.getHistogram( None, True )
        targetDistributionUp     = targetWebpage.getHistogram( Packet.UP, True )
        targetDistributionDown   = targetWebpage.getHistogram( Packet.DOWN, True )
        
        return [targetDistributionBi, targetDistributionUp, targetDistributionDown]

    @staticmethod
    def applyCountermeasure( trace,  metadata ):
        [targetDistributionBi,
         targetDistributionUp,
         targetDistributionDown] = metadata

        newTrace = Trace(trace.getId())

        # primary sampling
        timeCursor = 0
        for packet in trace.getPackets():
            timeCursor = packet.getTime()
            targetDistribution = targetDistributionDown
            if packet.getDirection()==Packet.UP:
                targetDistribution = targetDistributionUp

            packets = DirectTargetSampling.morphPacket( packet, targetDistribution )
            for newPacket in packets:
                newTrace.addPacket( newPacket )

        # secondary sampling
        while True:
            l1Distance = newTrace.calcL1Distance( targetDistributionBi )
            if l1Distance <= DirectTargetSampling.L1_THRESHHOLD:
                break

            timeCursor += 10
            newDirection, newLen = newTrace.getMostSkewedDimension( targetDistributionBi )
            packet = Packet( newDirection, timeCursor, newLen )
            newTrace.addPacket( packet )

        return newTrace

    @staticmethod
    def morphPacket( packet, targetDistribution ):
        packetPenalty = config.PACKET_PENALTY

        packetList = []
        newPacket = DirectTargetSampling.generatePacket( targetDistribution, packet )
        packetList.append( newPacket )

        dataSent  = newPacket.getLength() - packetPenalty
        dataSent  = max( dataSent, 0 ) # Can have 'negative' dataSent if newPacket is ACK
                                       # and packet is not ACK
        residual  = (packet.getLength() - packetPenalty) - dataSent

        # Now sample from secondary
        while residual > 0:
            newPacket = DirectTargetSampling.generatePacket( targetDistribution, packet )
            packetList.append( newPacket )

            dataSent  = (newPacket.getLength() - packetPenalty)
            dataSent  = max( dataSent, 0 )
            residual -= dataSent

        return packetList

    @staticmethod
    def generatePacket( targetDistribution, packet ):
        sample       = DirectTargetSampling.sampleFromDistribution( targetDistribution )
        if sample == None:
            newLen       = 1500
        else:
            bits         = sample.split('-')
            newLen       = int(bits[1])
        packet       = Packet( packet.getDirection(), packet.getTime(), newLen )

        return packet

    @staticmethod
    def sampleFromDistribution( distribution ):
        total = 0
        for key in distribution:
            total += distribution[key]
        n = random.uniform(0,total)

        key = None
        for key in distribution:
            if n < distribution[key]:
                return key
            n -= distribution[key]

        return key
