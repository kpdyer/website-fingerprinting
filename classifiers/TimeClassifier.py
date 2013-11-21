# This is a Python framework to compliment "Peek-a-Boo, I Still See You: Why Efficient Traffic Analysis Countermeasures Fail".
# Copyright (C) 2012  Kevin P. Dyer (kpdyer.com)
# See LICENSE for more details.

import wekaAPI
from Packet import Packet
import arffWriter

class TimeClassifier:
    @staticmethod
    def traceToInstance( trace ):
        maxTime = 0
        for packet in trace.getPackets():
             if packet.getTime() > maxTime:
                 maxTime = packet.getTime()

        instance = {}
        instance['time'] = maxTime
        instance['class'] = 'webpage'+str(trace.getId())
        return instance
    
    @staticmethod
    def classify( runID, trainingSet, testingSet ):
        [trainingFile,testingFile] = arffWriter.writeArffFiles( runID, trainingSet, testingSet )
        return wekaAPI.execute( trainingFile, testingFile, "weka.classifiers.bayes.NaiveBayes", ['-K'] )
