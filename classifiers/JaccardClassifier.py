# This is a Python framework to compliment "Peek-a-Boo, I Still See You: Why Efficient Traffic Analysis Countermeasures Fail".
# Copyright (C) 2012  Kevin P. Dyer (kpdyer.com)
# See LICENSE for more details.

import config

class JaccardClassifier:
    @staticmethod
    def traceToInstance( trace ):
        instance = {}
        for p in trace.getPackets():
            instance[p.getLength()] = 1
        
        instance['class'] = 'webpage'+str(trace.getId())
        return instance
    
    @staticmethod
    def classify( runID, trainingSet, testingSet ):
        bagOfLengths = {}
        for instance in trainingSet:
            if not bagOfLengths.get(instance['class']):
                bagOfLengths[instance['class']] = {}
            for attribute in instance:
                if attribute!='class':
                    if not bagOfLengths[instance['class']].get(attribute):
                        bagOfLengths[instance['class']][attribute] = 0
                    bagOfLengths[instance['class']][attribute] += 1
        
        for className in bagOfLengths:
            for length in bagOfLengths[className].keys():
                if bagOfLengths[className][length] < (config.NUM_TRAINING_TRACES/2.0):
                    del bagOfLengths[className][length]
        
        correctlyClassified = 0
        debugInfo           = []
        for instance in testingSet:
            guess = JaccardClassifier.doClassify(bagOfLengths, instance)
            if guess == instance['class']:
                correctlyClassified += 1
            debugInfo.append([instance['class'], guess])
        
        accuracy = 100.0 * correctlyClassified / len(testingSet)
        
        return [accuracy, debugInfo]
    
    @staticmethod
    def doClassify(bagOfLengths,  instance):
        guess = None
        bestSimilarity = 0
        for className in bagOfLengths:
            intersection = 0
            for attribute in instance:
                if attribute!='class' and attribute in bagOfLengths[className]:
                    intersection += 1
            union = (len(instance) - 1) + len(bagOfLengths[className])
            if union == 0:
                similarity = 0
            else:
                similarity = 1.0 * intersection / union
            if guess == None or similarity > bestSimilarity:
                bestSimilarity = similarity
                guess = className
        
        return guess
