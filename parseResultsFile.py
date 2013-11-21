# This is a Python framework to compliment "Peek-a-Boo, I Still See You: Why Efficient Traffic Analysis Countermeasures Fail".
# Copyright (C) 2012  Kevin P. Dyer (kpdyer.com)
# See LICENSE for more details.

import os.path
import sys
import config
import glob
import math

if config.PYTHONPATH: sys.path.append(config.PYTHONPATH)

from statlib import stats

def parseResultsFile(filename):
    resultsFile = open(filename, 'r')

    contents    = resultsFile.read()

    columns = contents.split("\n")[0].split(',')
    data    = {}
    for value in columns:
        data[value] = []

    lines = contents.split("\n")
    if len(lines) <= 1:
        return None

    for i in range(1,len(lines)):
        items = lines[i].split(', ')
        for i in range(len(items)):
            data[columns[i]].append(items[i])

    trials = str(len(data[data.keys()[0]]))
    for key in data:
        if key=='accuracy':
            meanAccuracy = 0
            for i in range(len(data[key])):
                data[key][i] = float(data[key][i])
                meanAccuracy += data[key][i]
            meanAccuracy /= len(data[key])
            meanAccuracy = '%.1f' % round(meanAccuracy, 1)

        elif key=='overhead':
            numeratorSum   = 0
            denominatorSum = 0
            for i in range(len(data[key])):
                value = data[key][i].split('/')
                numeratorSum   += int(value[0])
                denominatorSum += int(value[1])

            overhead = str( round(( numeratorSum * 100.0 / denominatorSum ) - 100,1) )
        elif key=='timeElapsedTotal':
            for i in range(len(data[key])):
                data[key][i] = float( data[key][i] )

            timeElapsed = str(round(stats.mean(data[key]),1))

    return [meanAccuracy,overhead,timeElapsed,trials]

print 'filename [avgAccuracy, avgOverhead, avgTimeElapsed, numTrials]'
if len(sys.argv)>1 and os.path.exists(sys.argv[1]):
    print sys.argv[1], parseResultsFile(sys.argv[1])
else:
    filelist = glob.glob('output/*.output')
    filelist.sort()
    for filename in filelist:
        if parseResultsFile(filename):
            print filename, parseResultsFile(filename)
