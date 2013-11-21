# This is a Python framework to compliment "Peek-a-Boo, I Still See You: Why Efficient Traffic Analysis Countermeasures Fail".
# Copyright (C) 2012  Kevin P. Dyer (kpdyer.com)
# See LICENSE for more details.

import arffWriter
import wekaAPI

from statlib import stats

from Trace import Trace
from Packet import Packet
import math

class VNGClassifier:
    @staticmethod
    def roundArbitrary(x, base):
        return int(base * round(float(x)/base))

    @staticmethod
    def traceToInstance( trace ):
        instance = {}

        # Size/Number Markers
        directionCursor = None
        dataCursor      = 0
        for packet in trace.getPackets():
            if directionCursor == None:
                directionCursor = packet.getDirection()

            if packet.getDirection()!=directionCursor:
                dataKey = 'S'+str(directionCursor)+'-'+str( VNGClassifier.roundArbitrary(dataCursor, 600) )
                if not instance.get( dataKey ):
                    instance[dataKey] = 0
                instance[dataKey] += 1

                directionCursor = packet.getDirection()
                dataCursor      = 0

            dataCursor += packet.getLength()

        if dataCursor>0:
            key = 'S'+str(directionCursor)+'-'+str( VNGClassifier.roundArbitrary(dataCursor, 600) )
            if not instance.get( key ):
                instance[key] = 0
            instance[key] += 1

        instance['class'] = 'webpage'+str(trace.getId())
        return instance
    
    @staticmethod
    def classify( runID, trainingSet, testingSet ):
        [trainingFile,testingFile] = arffWriter.writeArffFiles( runID, trainingSet, testingSet )
        return wekaAPI.execute( trainingFile, testingFile, "weka.classifiers.bayes.NaiveBayes", ['-K'] )
