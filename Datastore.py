# This is a Python framework to compliment "Peek-a-Boo, I Still See You: Why Efficient Traffic Analysis Countermeasures Fail".
# Copyright (C) 2012  Kevin P. Dyer (kpdyer.com)
# See LICENSE for more details.

import MySQLdb
import math
import config
import pcapparser

from Webpage import Webpage
from Trace import Trace
from Packet import Packet

import memcache
mc = memcache.Client(['127.0.0.1:11211'], debug=0)
ENABLE_CACHE = False

import cPickle

class Datastore:
    @staticmethod
    def getWebpagesLL( webpageIds, traceIndexStart, traceIndexEnd ):
        webpages = []
        for webpageId in webpageIds:
            webpage = Webpage(webpageId)
            for traceIndex in range(traceIndexStart, traceIndexEnd):
                trace = Datastore.getTraceLL( webpageId, traceIndex )
                webpage.addTrace(trace)
            webpages.append(webpage)

        return webpages

    @staticmethod
    def getTraceLL( webpageId, traceIndex ):
        key = '.'.join(['Webpage',
                        'LL',
                        str(webpageId),
                        str(traceIndex)])

        trace = mc.get(key)
        if ENABLE_CACHE and trace:
            trace = cPickle.loads(trace)
        else:
            dateTime = config.DATA_SET[traceIndex]
            trace = pcapparser.readfile(dateTime['month'],
                                        dateTime['day'],
                                        dateTime['hour'],
                                        webpageId)

            mc.set(key,cPickle.dumps(trace,protocol=cPickle.HIGHEST_PROTOCOL))

        return trace

    @staticmethod
    def getWebpagesHerrmann( webpageIds, traceIndexStart, traceIndexEnd ):
        webpages = []
        for webpageId in webpageIds:
            webpage = Webpage(webpageId)
            for traceIndex in range(traceIndexStart, traceIndexEnd):
                trace = Datastore.getTraceHerrmann( webpageId, traceIndex )
                webpage.addTrace(trace)
            webpages.append(webpage)

        return webpages

    @staticmethod
    def getTraceHerrmann( webpageId, traceIndex ):
        if config.DATA_SOURCE == 1:
            datasourceId = 4
        elif config.DATA_SOURCE == 2:
            datasourceId = 5

        key = '.'.join(['Webpage',
                        'H',
                        str(datasourceId),
                        str(webpageId),
                        str(traceIndex)])

        trace = mc.get(key)
        if ENABLE_CACHE and trace:
            trace = cPickle.loads(trace)
        else:
            connection = MySQLdb.connect(host=config.MYSQL_HOST,
                                         user=config.MYSQL_USER,
                                         passwd=config.MYSQL_PASSWD,
                                         db=config.MYSQL_DB )

            cursor = connection.cursor()
            command = """SELECT packets.trace_id,
                                      packets.size,
                                      ROUND(packets.abstime*1000)
                                 FROM (SELECT id
                                         FROM traces
                                        WHERE site_id = (SELECT id
                                                           FROM sites
                                                          WHERE dataset_id = """+str(datasourceId)+"""
                                                          ORDER BY id
                                                          LIMIT """+str(webpageId)+""",1)
                                        ORDER BY id
                                        LIMIT """+str(traceIndex)+""",1) traces,
                                      packets
                                WHERE traces.id = packets.trace_id
                                ORDER BY packets.trace_id, packets.abstime"""
            cursor.execute( command )

            data = cursor.fetchall()
            trace = Trace(webpageId)
            for item in data:
                direction = Packet.UP
                if int(item[1])>0:
                    direction = Packet.DOWN
                time   = item[2]
                length = int(math.fabs(item[1]))

                trace.addPacket( Packet( direction, time, length ) )
            connection.close()

            mc.set(key,cPickle.dumps(trace,protocol=cPickle.HIGHEST_PROTOCOL))

        return trace
