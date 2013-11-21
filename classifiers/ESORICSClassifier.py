# This is a Python framework to compliment "Peek-a-Boo, I Still See You: Why Efficient Traffic Analysis Countermeasures Fail".
# Copyright (C) 2012  Kevin P. Dyer (kpdyer.com)
# See LICENSE for more details.

import config
from Packet import Packet
import Levenshtein

class ESORICSClassifier:
    @staticmethod
    def traceToInstance( trace ):
        return trace
    
    @staticmethod
    def classify( runID, trainingSet, testingSet ):
        candidateSequences = {}
        for trace in trainingSet:
            for d in [Packet.UP,  Packet.DOWN]:
                if not candidateSequences.get('Webpage'+str(trace.getId())):
                    candidateSequences['Webpage'+str(trace.getId())] = {}
                    candidateSequences['Webpage'+str(trace.getId())][Packet.UP] = []
                    candidateSequences['Webpage'+str(trace.getId())][Packet.DOWN] = []
                    
                candidateSequences['Webpage'+str(trace.getId())][d].append([])
                for p in trace.getPackets():
                    if p.getDirection()==d:
                        if d == Packet.UP and p.getLength() > 300:
                            candidateSequences['Webpage'+str(trace.getId())][d][-1].append(p.getLength())
                        elif d == Packet.DOWN and p.getLength() > 300 and p.getLength() < 1450:
                            candidateSequences['Webpage'+str(trace.getId())][d][-1].append(p.getLength())
        
        correctlyClassified = 0
        debugInfo           = []
        for instance in testingSet:
            actual = 'Webpage'+str(instance.getId())
            guess = ESORICSClassifier.doClassify(candidateSequences, instance)
            if guess == actual:
                correctlyClassified += 1
            debugInfo.append([actual, guess])
        
        accuracy = 100.0 * correctlyClassified / len(testingSet)
        
        return [accuracy, debugInfo]
    
    @staticmethod
    def doClassify(candidateSequences,  instance):
        guess = None
        
        targetSequenceUp   = []
        targetSequenceDown = []
        for p in instance.getPackets():
            if p.getDirection()==Packet.UP and p.getLength() > 300:
                targetSequenceUp.append(p.getLength())
            elif p.getDirection()==Packet.DOWN and p.getLength() > 300 and p.getLength() < 1450:
                targetSequenceDown.append(p.getLength())
        
        similarity = {}        
        for className in candidateSequences:
            if not similarity.get(className):
                similarity[className] = 0
            for direction in [Packet.UP,  Packet.DOWN]:
                for i in range(len(candidateSequences[className][direction])):
                    if direction == Packet.UP:
                        distance = ESORICSClassifier.levenshtein(targetSequenceUp, candidateSequences[className][direction][i])
                        maxLen = max(len(targetSequenceUp), len(candidateSequences[className][direction][i]))
                        if len(targetSequenceUp) == 0 or len(candidateSequences[className][direction][i]) == 0:
                            distance = 1.0
                        else:
                            distance /= 1.0 * maxLen
                            
                        similarity[className] +=  0.6 * distance
                    elif direction == Packet.DOWN:
                        distance = ESORICSClassifier.levenshtein(targetSequenceDown, candidateSequences[className][direction][i])
                        maxLen = max(len(targetSequenceDown), len(candidateSequences[className][direction][i]))
                        if len(targetSequenceDown) == 0 or len(candidateSequences[className][direction][i]) == 0:
                            distance = 1.0
                        else:
                            distance /= 1.0 * maxLen
                        similarity[className] +=  0.4 * distance
                
        bestSimilarity = config.NUM_TRAINING_TRACES
        for className in similarity:
            if guess == None or similarity[className] <= bestSimilarity:
                bestSimilarity = similarity[className]
                guess = className
        
        return guess

    @staticmethod
    # from http://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance
    def levenshtein(s1, s2):
        s1 = ESORICSClassifier.encode(s1)
        s2 = ESORICSClassifier.encode(s2)
        return Levenshtein.distance(unicode(s1), unicode(s2))
        
    @staticmethod
    def encode(list):
        strList = []
        for val in list:
            #appVal = config.PACKET_RANGE2.index(val)
            appVal = unichr(val)
            strList.append(appVal)
            
        return ''.join(strList)
