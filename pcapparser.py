# This is a Python framework to compliment "Peek-a-Boo, I Still See You: Why Efficient Traffic Analysis Countermeasures Fail".
# Copyright (C) 2012  Kevin P. Dyer (kpdyer.com)
# See LICENSE for more details.

import Packet
import trace
import os.path
import glob
import config
import os
from Packet import Packet
from Trace import Trace
import dpkt

def readfile( month, day, hour, webpageId ):
    strId = '.'.join([str(month), str(day), str(hour), str(webpageId)])

    trace = Trace(webpageId)
    start = 0

    absPath    = __constructAbsolutePath( month, day, hour, webpageId )

    if absPath:
        pcapReader = dpkt.pcap.Reader( file( absPath, "rb") )

        for ts, buf in pcapReader:
            eth = dpkt.ethernet.Ethernet(buf)
            ip  = eth.data
            tcp = ip.data
            
            if start==0: start = ts
            direction = Packet.UP
            if (tcp.sport==22):
                direction = Packet.DOWN
            delta     = int(round(((ts - start) * 1000),0))
            length    = ip.len + Packet.HEADER_ETHERNET

            trace.addPacket( Packet(direction, delta, length ) )
            
    return trace

def __constructAbsolutePath( month, day, hour, webpageId ):
    if not os.path.exists(config.PCAP_ROOT):
        raise Exception('Directory ('+config.PCAP_ROOT+') does not exist')
    
    monthStr = '%02d' % month
    dayStr   = '%02d' % day
    hourStr  = '%02d' % hour
    path     = os.path.join(config.PCAP_ROOT, '2006-'+monthStr
                                                 +'-'+dayStr
                                                 +'T'+hourStr
                                                 +'*/*'
                                                 +'-'+str(webpageId))

    pathList    =  glob.glob(path)

    absFilePath = None
    if len(pathList)>0:
        absFilePath = pathList[0]

    return absFilePath