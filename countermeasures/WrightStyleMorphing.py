# This is a Python framework to compliment "Peek-a-Boo, I Still See You: Why Efficient Traffic Analysis Countermeasures Fail".
# Copyright (C) 2012  Kevin P. Dyer (kpdyer.com)
# See LICENSE for more details.

import random
import math
import config

from Webpage import Webpage
from Trace import Trace
from Packet import Packet

from cvxopt.base import matrix, sparse, spdiag

from cvxopt import solvers

solvers.options['show_progress'] = False
solvers.options['LPX_K_MSGLEV']  = 0

solvers.options['abstol'] = 1e-4
solvers.options['reltol'] = 1e-4

solvers.options['maxiters'] = 200

# cost_matrix is the vector of cost coeffs
n = len(config.PACKET_RANGE)
N = n**2
cost_matrix = matrix(0.0, (n,n), 'd')
for i in range(n):
    for j in range(n):
        cost_matrix[i,j] = math.fabs(config.PACKET_RANGE[i] - config.PACKET_RANGE[j])

cost_matrix = matrix(cost_matrix, (N,1), 'd')

class WrightStyleMorphing:
    L1_THRESHHOLD = 0.3

    @staticmethod
    def buildMetadata( srcWebpage, targetWebpage ):
        targetDistributionBi     = targetWebpage.getHistogram( None, True )
        targetDistributionUp     = targetWebpage.getHistogram( Packet.UP, True )
        targetDistributionDown   = targetWebpage.getHistogram( Packet.DOWN, True )
        srcDistributionUp        = srcWebpage.getHistogram( Packet.UP, True )
        srcDistributionDown      = srcWebpage.getHistogram( Packet.DOWN, True )
        morphingMatrixUp         = WrightStyleMorphing.buildMorphingMatrix(srcWebpage.getId(), targetWebpage.getId(), Packet.UP, srcDistributionUp, targetDistributionUp)
        morphingMatrixDown       = WrightStyleMorphing.buildMorphingMatrix(srcWebpage.getId(), targetWebpage.getId(), Packet.DOWN, srcDistributionDown, targetDistributionDown)
        
        return [targetDistributionBi, targetDistributionUp, targetDistributionDown, srcDistributionUp, srcDistributionDown, morphingMatrixUp, morphingMatrixDown]

    @staticmethod
    def applyCountermeasure( trace,  metadata ):
        [targetDistributionBi,
         targetDistributionUp,
         targetDistributionDown,
         srcDistributionUp,
         srcDistributionDown,
         morphingMatrixUp,
         morphingMatrixDown] = metadata
         
        newTrace = Trace(trace.getId())

        # primary sampling
        timeCursor = 0
        for packet in trace.getPackets():
            timeCursor = packet.getLength()
            index = (packet.getLength()-Packet.HEADER_LENGTH)/8

            targetDistribution = None
            morphingColumn     = None
            if packet.getDirection()==Packet.UP:
                if morphingMatrixUp:
                    morphingColumn = morphingMatrixUp[:,index]
                else:
                    targetDistribution = targetDistributionUp
                targetDistributionSecondary = targetDistributionUp
            else:
                if morphingMatrixDown:
                    morphingColumn = morphingMatrixDown[:,index]
                else:
                    targetDistribution = targetDistributionDown
                targetDistributionSecondary = targetDistributionDown

            if morphingColumn:
                targetDistribution = {}
                for i in range(len(morphingColumn)):
                    key = str(packet.getDirection())+'-'+str( i*8 + Packet.HEADER_LENGTH )
                    targetDistribution[key] = morphingColumn[i]

            packets = WrightStyleMorphing.morphPacket( packet, targetDistribution, targetDistributionSecondary )
            for newPacket in packets:
                newTrace.addPacket( newPacket )

        # secondary sampling
        while True:
            l1Distance = newTrace.calcL1Distance( targetDistributionBi )
            if l1Distance <= WrightStyleMorphing.L1_THRESHHOLD:
                break

            timeCursor += 10
            newDirection, newLen = newTrace.getMostSkewedDimension( targetDistributionBi )
            packet = Packet( newDirection, timeCursor, newLen )
            newTrace.addPacket( packet )

        return newTrace

    @staticmethod
    def morphPacket( packet, targetDistributionPrimary, targetDistributionSecondary ):
        packetPenalty = config.PACKET_PENALTY

        packetList = []
        newPacket = WrightStyleMorphing.generatePacket( targetDistributionPrimary, packet )
        packetList.append( newPacket )

        dataSent  = newPacket.getLength() - packetPenalty
        dataSent  = max( dataSent, 0 ) # Can have 'negative' dataSent if newPacket is ACK
                                       # and packet is not ACK
        residual  = (packet.getLength() - packetPenalty) - dataSent

        # Now sample from secondary
        while residual > 0:
            newPacket = WrightStyleMorphing.generatePacket( targetDistributionSecondary, packet )
            packetList.append( newPacket )

            dataSent  = (newPacket.getLength() - packetPenalty)
            dataSent  = max( dataSent, 0 )
            residual -= dataSent

        return packetList

    @staticmethod
    def generatePacket( targetDistribution, packet ):
        sample       = WrightStyleMorphing.sampleFromDistribution( targetDistribution )
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

    @staticmethod
    def buildMorphingMatrix(srcID, targetID, direction, srcDist, targetDist):
        srcVec    = matrix(0, ( len(config.PACKET_RANGE) , 1), 'd' )
        targetVec = matrix(0, ( len(config.PACKET_RANGE) , 1), 'd' )

        for i in range(len(config.PACKET_RANGE)):
            key = str(direction)+'-'+str(config.PACKET_RANGE[i])

            if not srcDist.get( key ):
                srcVec[i] = 0
            else:
                srcVec[i] = srcDist[key]

            if not targetDist.get( key ):
                targetVec[i] = 0
            else:
                targetVec[i] = targetDist[key]

        A = WrightStyleMorphing.what_is_the_matrix( srcVec, targetVec )

        return A

    @staticmethod
    def what_is_the_matrix(X, Z):
        """find the optimal morphing matrix A such that A * src_dist = target_dist"""

        #print "============ What is the Matrix? ==============="

        n = len(Z)
        N = n**2

        #print "X =", X.T
        #print "Z =", Z.T

        # Equality Constraints
        A_list = []
        b_list = []
        #  -- the columns of the matrix must be valid PDF's
        A_pdf = matrix(0.0, (n,N), 'd')
        for i in range(n):
            A_pdf[i,n*i:n*i+n] = 1.0
        b_pdf = matrix(1.0, (n,1), 'd')
        #print "A_pdf ="
        #print A_pdf
        #print "b_pdf ="
        #print b_pdf
        A_list.append(A_pdf)
        b_list.append(b_pdf)

        #  -- the matrix must morph X to Z
        A_morph = matrix(0.0, (n,N), 'd')
        for i in range(n):
            matrix_vers = matrix(0.0, (n,n), 'd')
            matrix_vers[i,:] = X.T
            row = matrix(matrix_vers, (1,N), 'd')
            A_morph[i,:] = row
        b_morph = matrix(Z, (n,1), 'd')
        A_list.append(A_morph)
        b_list.append(b_morph)

        #print "A_morph ="
        #print A_morph
        #print "b_morph ="
        #print b_morph

        # concatenate all our equality constraints into one coeff matrix and one b vector
        #A_list = [A_morph, A_pdf]
        #b_list = [b_morph, b_pdf]
        #A_list = [A_pdf]
        #b_list = [b_pdf]
        #A = matrix(A_list)
        A = sparse(A_list)
        b = matrix(b_list)

        #print "A ="
        #print A
        #print "b ="
        #print b

        # Inequality Constraints -- in order to be a valid PDF, each cell a_ij must be 0 <= a_ij <= 1
        G_list = []
        h_list = []
        G_lt = spdiag(matrix(1.0, (N,1), 'd'))
        h_lt = matrix(1.0, (N,1), 'd')
        # cvw: as mentioned in the comment above in find_the_one(), the "less than" constraints are
        #      in fact redundant given that we already require the columns to sum to 1.0 and require
        #      (below) that each prob is >= 0.  yay for smaller KKT matrices.
        #G_list.append(G_lt)
        #h_list.append(h_lt)

        G_gt = spdiag(matrix(-1.0, (N,1), 'd'))
        h_gt = matrix(0.0, (N,1), 'd')
        G_list.append(G_gt)
        h_list.append(h_gt)

        # cvw: I guess we could add some more constraints if we really wanted to..
        #      i.e. only downgrade the bit rate 10% of the time or less
        #      but for now these'll do

        G = sparse(G_list)
        h = matrix(h_list)
        #print "G ="
        #print G
        #print "h ="
        #print h

        #print "vectorized cost matrix ="
        #print c.T

        # now run the cvxopt solver to get our answer
        #print "running cvxopt lp() solver..."
        ans = solvers.lp(cost_matrix, G=G, h=h, A=A, b=b, solver='glpk')
        ##print ans['x']
        #print "answer = ", ans
        A = None
        if ans['x']:
            cost = cost_matrix.T * ans['x']

            # A is the morphing matrix
            A = matrix(ans['x'], (n,n), 'd')

        return A
