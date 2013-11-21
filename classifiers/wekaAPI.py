# This is a Python framework to compliment "Peek-a-Boo, I Still See You: Why Efficient Traffic Analysis Countermeasures Fail".
# Copyright (C) 2012  Kevin P. Dyer (kpdyer.com)
# See LICENSE for more details.

import re
import subprocess
import config
import os

def execute( trainingFile, testingFile, classifier, args ):
    myArgs = ["java",
        "-Xmx" + str(config.JVM_MEMORY_SIZE),
        "-classpath", '$CLASSPATH:'+config.WEKA_JAR,
        classifier,
        "-t", trainingFile,
        "-T", testingFile,
        '-v',
        '-classifications','weka.classifiers.evaluation.output.prediction.CSV'
        ]

    for arg in args:
        myArgs.append( arg )

    pp = subprocess.Popen(' '.join(myArgs), shell=True, stdout=subprocess.PIPE)

    totalPredictions = 0
    totalCorrectPredictions = 0
    debugInfo = []
    parsing = False
    for line in pp.stdout:
        line = line.rstrip()

        if parsing == True:
            if line=='': break;
            lineBits = line.split(',')
            actualClass = lineBits[1].split(':')[1]
            predictedClass = lineBits[2].split(':')[1]
            debugInfo.append([actualClass,predictedClass])
            totalPredictions += 1.0
            if actualClass == predictedClass:
                totalCorrectPredictions += 1.0

        if line == 'inst#,actual,predicted,error,prediction':
            parsing = True

    accuracy = totalCorrectPredictions / totalPredictions * 100.0

    return [accuracy,debugInfo]
