# This is a Python framework to compliment "Peek-a-Boo, I Still See You: Why Efficient Traffic Analysis Countermeasures Fail".
# Copyright (C) 2012  Kevin P. Dyer (kpdyer.com)
# See LICENSE for more details.

import unittest
import pcapparser
from Trace import Trace
from Packet import Packet

class  PcapParserTestCase(unittest.TestCase):
    def test_readfile(self):
        actualTrace = pcapparser.readfile( month=3, day=14, hour=22, webpageId=8 )

        expectedTrace = Trace(8)
        expectedTrace.addPacket( Packet( Packet.UP  , 0  , 148 ) )
        expectedTrace.addPacket( Packet( Packet.DOWN, 0  , 100 ) )
        expectedTrace.addPacket( Packet( Packet.UP  , 0  , 52  ) )
        expectedTrace.addPacket( Packet( Packet.UP  , 3  , 500 ) )
        expectedTrace.addPacket( Packet( Packet.DOWN, 18 , 244 ) )
        expectedTrace.addPacket( Packet( Packet.UP  , 35 , 436 ) )
        expectedTrace.addPacket( Packet( Packet.DOWN, 75 , 52  ) )
        expectedTrace.addPacket( Packet( Packet.DOWN, 118, 292 ) )
        expectedTrace.addPacket( Packet( Packet.UP  , 158, 52  ) )

if __name__ == '__main__':
    unittest.main()
