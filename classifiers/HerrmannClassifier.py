# This is a Python framework to compliment "Peek-a-Boo, I Still See You: Why Efficient Traffic Analysis Countermeasures Fail".
# Copyright (C) 2012  Kevin P. Dyer (kpdyer.com)
# See LICENSE for more details.

import wekaAPI
import math
import arffWriter

# TF-N implementation of Multinomial Naive Bayes Classifier
class HerrmannClassifier:
    @staticmethod
    def traceToInstance( trace ):
        instance = trace.getHistogram()

        for attribute in instance:
            # Apply TF Transformation
            instance[attribute] = math.log( 1 + instance[attribute], 2 )

        # Store Euclidean Length for Cosine Normalisation (Section 4.5.2)
        euclideanLength = 0
        for attribute in instance:
            euclideanLength += instance[attribute] * instance[attribute]
        euclideanLength = math.sqrt( euclideanLength )

        for attribute in instance:
            # Apply Cosine Normalisation
            instance[attribute] /= euclideanLength
        
        instance['class'] = 'webpage'+str(trace.getId())
        return instance
    
    @staticmethod
    def classify( runID, trainingSet, testingSet ):
        [trainingFile,testingFile] = arffWriter.writeArffFiles( runID, trainingSet, testingSet )
        return wekaAPI.execute( trainingFile, testingFile, "weka.classifiers.bayes.NaiveBayesMultinomial", [] )
