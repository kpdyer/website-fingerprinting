# This is a Python framework to compliment "Peek-a-Boo, I Still See You: Why Efficient Traffic Analysis Countermeasures Fail".
# Copyright (C) 2012  Kevin P. Dyer (kpdyer.com)
# See LICENSE for more details.

import config
import os
import itertools

def writeArffFiles( runID, trainingSet, testingSet ):
    trainingFilename           = 'datafile-'+runID+'-train'
    testingFilename            = 'datafile-'+runID+'-test'

    classes = []
    for instance in trainingSet:
        if instance['class'] not in classes:
            classes.append(instance['class'])
    for instance in testingSet:
        if instance['class'] not in classes:
            classes.append(instance['class'])

    attributes = []
    for instance in trainingSet:
        for key in instance:
            if key not in attributes:
                attributes.append( key )
    for instance in testingSet:
        for key in instance:
            if key not in attributes:
                attributes.append( key )

    trainingFile = __writeArffFile( trainingSet, trainingFilename, classes, attributes )
    testingFile = __writeArffFile( testingSet, testingFilename, classes, attributes )

    return [trainingFile, testingFile]


def __writeArffFile( inputArray, outputFile, classes, attributes ):
    arffFile = []
    arffFile.append('@RELATION sites')
    for attribute in attributes:
        if attribute!='class':
            arffFile.append('@ATTRIBUTE '+str(attribute)+' real')
    arffFile.append('@ATTRIBUTE class {'+','.join(classes)+'}')
    arffFile.append('@DATA')

    for instance in inputArray:
        tmpBuf = []
        for attribute in attributes:
            if attribute!='class':
                val = '0'
                if instance.get(attribute) not in [None,0]:
                    val = str(instance[attribute])
                tmpBuf.append(val)
        tmpBuf.append(instance['class'])

        arffFile.append( ','.join(itertools.imap(str, tmpBuf)) )
    
    outputFile = os.path.join(config.CACHE_DIR, outputFile+'.arff')
    f = open( outputFile, 'w' )
    f.write( "\n".join( arffFile ) )
    f.close()

    return outputFile
