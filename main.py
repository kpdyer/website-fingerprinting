# This is a Python framework to compliment "Peek-a-Boo, I Still See You: Why Efficient Traffic Analysis Countermeasures Fail".
# Copyright (C) 2012  Kevin P. Dyer (kpdyer.com)
# See LICENSE for more details.

import sys
import config
import time
import os
import random
import getopt
import string
import itertools

# custom
from Datastore import Datastore
from Webpage import Webpage

# countermeasures
from PadToMTU import PadToMTU
from PadRFCFixed import PadRFCFixed
from PadRFCRand import PadRFCRand
from PadRand import PadRand
from PadRoundExponential import PadRoundExponential
from PadRoundLinear import PadRoundLinear
from MiceElephants import MiceElephants
from DirectTargetSampling import DirectTargetSampling
from Folklore import Folklore
from WrightStyleMorphing import WrightStyleMorphing

# classifiers
from LiberatoreClassifier import LiberatoreClassifier
from WrightClassifier import WrightClassifier
from BandwidthClassifier import BandwidthClassifier
from HerrmannClassifier import HerrmannClassifier
from TimeClassifier import TimeClassifier
from PanchenkoClassifier import PanchenkoClassifier
from VNGPlusPlusClassifier import VNGPlusPlusClassifier
from VNGClassifier import VNGClassifier
from JaccardClassifier import JaccardClassifier
from ESORICSClassifier import ESORICSClassifier

def intToCountermeasure(n):
    countermeasure = None
    if n == config.PAD_TO_MTU:
        countermeasure = PadToMTU
    elif n == config.RFC_COMPLIANT_FIXED_PAD:
        countermeasure = PadRFCFixed
    elif n == config.RFC_COMPLIANT_RANDOM_PAD:
        countermeasure = PadRFCRand
    elif n == config.RANDOM_PAD:
        countermeasure = PadRand
    elif n == config.PAD_ROUND_EXPONENTIAL:
        countermeasure = PadRoundExponential
    elif n == config.PAD_ROUND_LINEAR:
        countermeasure = PadRoundLinear
    elif n == config.MICE_ELEPHANTS:
        countermeasure = MiceElephants
    elif n == config.DIRECT_TARGET_SAMPLING:
        countermeasure = DirectTargetSampling
    elif n == config.WRIGHT_STYLE_MORPHING:
        countermeasure = WrightStyleMorphing
    elif n > 10:
        countermeasure = Folklore

        # FIXED_PACKET_LEN: 1000,1250,1500
        if n in [11,12,13,14]:
            Folklore.FIXED_PACKET_LEN    = 1000
        elif n in [15,16,17,18]:
            Folklore.FIXED_PACKET_LEN    = 1250
        elif n in [19,20,21,22]:
            Folklore.FIXED_PACKET_LEN    = 1500

        if n in [11,12,13,17,18,19]:
            Folklore.TIMER_CLOCK_SPEED   = 20
        elif n in [14,15,16,20,21,22]:
            Folklore.TIMER_CLOCK_SPEED   = 40

        if n in [11,14,17,20]:
            Folklore.MILLISECONDS_TO_RUN = 0
        elif n in [12,15,18,21]:
            Folklore.MILLISECONDS_TO_RUN = 5000
        elif n in [13,16,19,22]:
            Folklore.MILLISECONDS_TO_RUN = 10000

        if n==23:
            Folklore.MILLISECONDS_TO_RUN = 0
            Folklore.FIXED_PACKET_LEN    = 1250
            Folklore.TIMER_CLOCK_SPEED   = 40
        elif n==24:
            Folklore.MILLISECONDS_TO_RUN = 0
            Folklore.FIXED_PACKET_LEN    = 1500
            Folklore.TIMER_CLOCK_SPEED   = 20
        elif n==25:
            Folklore.MILLISECONDS_TO_RUN = 5000
            Folklore.FIXED_PACKET_LEN    = 1000
            Folklore.TIMER_CLOCK_SPEED   = 40
        elif n==26:
            Folklore.MILLISECONDS_TO_RUN = 5000
            Folklore.FIXED_PACKET_LEN    = 1500
            Folklore.TIMER_CLOCK_SPEED   = 20
        elif n==27:
            Folklore.MILLISECONDS_TO_RUN = 10000
            Folklore.FIXED_PACKET_LEN    = 1000
            Folklore.TIMER_CLOCK_SPEED   = 40
        elif n==28:
            Folklore.MILLISECONDS_TO_RUN = 10000
            Folklore.FIXED_PACKET_LEN    = 1250
            Folklore.TIMER_CLOCK_SPEED   = 20


    return countermeasure

def intToClassifier(n):
    classifier = None
    if n == config.LIBERATORE_CLASSIFIER:
        classifier = LiberatoreClassifier
    elif n == config.WRIGHT_CLASSIFIER:
        classifier = WrightClassifier
    elif n == config.BANDWIDTH_CLASSIFIER:
        classifier = BandwidthClassifier
    elif n == config.HERRMANN_CLASSIFIER:
        classifier = HerrmannClassifier
    elif n == config.TIME_CLASSIFIER:
        classifier = TimeClassifier
    elif n == config.PANCHENKO_CLASSIFIER:
        classifier = PanchenkoClassifier
    elif n == config.VNG_PLUS_PLUS_CLASSIFIER:
        classifier = VNGPlusPlusClassifier
    elif n == config.VNG_CLASSIFIER:
        classifier = VNGClassifier
    elif n == config.JACCARD_CLASSIFIER:
        classifier = JaccardClassifier
    elif n == config.ESORICS_CLASSIFIER:
        classifier = ESORICSClassifier

    return classifier

def usage():
    print """
    -N [int] : use [int] websites from the dataset
               from which we will use to sample a privacy
               set k in each experiment (default 775)

    -k [int] : the size of the privacy set (default 2)

    -d [int]: dataset to use
        0: Liberatore and Levine Dataset (OpenSSH)
        1: Herrmann et al. Dataset (OpenSSH)
        2: Herrmann et al. Dataset (Tor)
        (default 1)

    -C [int] : classifier to run
        0: Liberatore Classifer
        1: Wright et al. Classifier
        2: Jaccard Classifier
        3: Panchenko et al. Classifier
        5: Lu et al. Edit Distance Classifier
        6: Herrmann et al. Classifier
        4: Dyer et al. Bandwidth (BW) Classifier
        10: Dyer et al. Time Classifier
        14: Dyer et al. Variable n-gram (VNG) Classifier
        15: Dyer et al. VNG++ Classifier
        (default 0)

    -c [int]: countermeasure to use
        0: None
        1: Pad to MTU
        2: Session Random 255
        3: Packet Random 255
        4: Pad Random MTU
        5: Exponential Pad
        6: Linear Pad
        7: Mice-Elephants Pad
        8: Direct Target Sampling
        9: Traffic Morphing
        (default 0)

    -t [int]: number of trials to run per experiment (default 1)

    -t [int]: number of training traces to use per experiment (default 16)

    -T [int]: number of testing traces to use per experiment (default 4)
    """

def run():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "t:T:N:k:c:C:d:n:r:h")
    except getopt.GetoptError, err:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    char_set = string.ascii_lowercase + string.digits
    runID = ''.join(random.sample(char_set,8))

    for o, a in opts:
        if o in ("-k"):
            config.BUCKET_SIZE = int(a)
        elif o in ("-C"):
            config.CLASSIFIER = int(a)
        elif o in ("-d"):
            config.DATA_SOURCE = int(a)
        elif o in ("-c"):
            config.COUNTERMEASURE = int(a)
        elif o in ("-N"):
            config.TOP_N = int(a)
        elif o in ("-t"):
            config.NUM_TRAINING_TRACES = int(a)
        elif o in ("-T"):
            config.NUM_TESTING_TRACES = int(a)
        elif o in ("-n"):
            config.NUM_TRIALS = int(a)
        elif o in ("-r"):
            runID = str(a)
        else:
            usage()
            sys.exit(2)

    outputFilenameArray = ['results',
                           'k'+str(config.BUCKET_SIZE),
                           'c'+str(config.COUNTERMEASURE),
                           'd'+str(config.DATA_SOURCE),
                           'C'+str(config.CLASSIFIER),
                           'N'+str(config.TOP_N),
                           't'+str(config.NUM_TRAINING_TRACES),
                           'T'+str(config.NUM_TESTING_TRACES),
                          ]
    outputFilename = os.path.join(config.OUTPUT_DIR,'.'.join(outputFilenameArray))

    if not os.path.exists(config.CACHE_DIR):
        os.mkdir(config.CACHE_DIR)

    if not os.path.exists(outputFilename+'.output'):
        banner = ['accuracy','overhead','timeElapsedTotal','timeElapsedClassifier']
        f = open( outputFilename+'.output', 'w' )
        f.write(','.join(banner))
        f.close()
    if not os.path.exists(outputFilename+'.debug'):
        f = open( outputFilename+'.debug', 'w' )
        f.close()

    if config.DATA_SOURCE == 0:
        startIndex = config.NUM_TRAINING_TRACES
        endIndex   = len(config.DATA_SET)-config.NUM_TESTING_TRACES
    elif config.DATA_SOURCE == 1:
        maxTracesPerWebsiteH = 160
        startIndex = config.NUM_TRAINING_TRACES
        endIndex   = maxTracesPerWebsiteH-config.NUM_TESTING_TRACES
    elif config.DATA_SOURCE == 2:
        maxTracesPerWebsiteH = 18
        startIndex = config.NUM_TRAINING_TRACES
        endIndex   = maxTracesPerWebsiteH-config.NUM_TESTING_TRACES

    for i in range(config.NUM_TRIALS):
        startStart = time.time()

        webpageIds = range(0, config.TOP_N - 1)
        random.shuffle( webpageIds )
        webpageIds = webpageIds[0:config.BUCKET_SIZE]

        seed = random.randint( startIndex, endIndex )

        preCountermeasureOverhead = 0
        postCountermeasureOverhead = 0

        classifier     = intToClassifier(config.CLASSIFIER)
        countermeasure = intToCountermeasure(config.COUNTERMEASURE)

        trainingSet = []
        testingSet  = []

        targetWebpage = None

        for webpageId in webpageIds:
            if config.DATA_SOURCE == 0:
                webpageTrain = Datastore.getWebpagesLL( [webpageId], seed-config.NUM_TRAINING_TRACES, seed )
                webpageTest  = Datastore.getWebpagesLL( [webpageId], seed, seed+config.NUM_TESTING_TRACES )
            elif config.DATA_SOURCE == 1 or config.DATA_SOURCE == 2:
                webpageTrain = Datastore.getWebpagesHerrmann( [webpageId], seed-config.NUM_TRAINING_TRACES, seed )
                webpageTest  = Datastore.getWebpagesHerrmann( [webpageId], seed, seed+config.NUM_TESTING_TRACES )

            webpageTrain = webpageTrain[0]
            webpageTest = webpageTest[0]

            if targetWebpage == None:
                targetWebpage = webpageTrain

            preCountermeasureOverhead  += webpageTrain.getBandwidth()
            preCountermeasureOverhead  += webpageTest.getBandwidth()

            metadata = None
            if config.COUNTERMEASURE in [config.DIRECT_TARGET_SAMPLING, config.WRIGHT_STYLE_MORPHING]:
                metadata = countermeasure.buildMetadata( webpageTrain,  targetWebpage )

            i = 0
            for w in [webpageTrain, webpageTest]:
                for trace in w.getTraces():
                    if countermeasure:
                        if config.COUNTERMEASURE in [config.DIRECT_TARGET_SAMPLING, config.WRIGHT_STYLE_MORPHING]:
                            if w.getId()!=targetWebpage.getId():
                                traceWithCountermeasure = countermeasure.applyCountermeasure( trace,  metadata )
                            else:
                                traceWithCountermeasure = trace
                        else:
                            traceWithCountermeasure = countermeasure.applyCountermeasure( trace )
                    else:
                        traceWithCountermeasure = trace

                    postCountermeasureOverhead += traceWithCountermeasure.getBandwidth()
                    instance = classifier.traceToInstance( traceWithCountermeasure )

                    if instance:
                        if i==0:
                            trainingSet.append( instance )
                        elif i==1:
                            testingSet.append( instance )
                i+=1

        ###################

        startClass = time.time()

        [accuracy,debugInfo] = classifier.classify( runID, trainingSet, testingSet )

        end = time.time()

        overhead = str(postCountermeasureOverhead)+'/'+str(preCountermeasureOverhead)

        output = [accuracy,overhead]

        output.append( '%.2f' % (end-startStart) )
        output.append( '%.2f' % (end-startClass) )

        summary = ', '.join(itertools.imap(str, output))

        f = open( outputFilename+'.output', 'a' )
        f.write( "\n"+summary )
        f.close()

        f = open( outputFilename+'.debug', 'a' )
        for entry in debugInfo:
            f.write( entry[0]+','+entry[1]+"\n" )
        f.close()

if __name__ == '__main__':
    run()
