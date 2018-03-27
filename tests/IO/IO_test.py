'''
This scripts aims at testing IO processors by reading/writing files.
Author: M. Guigue
Date: Feb 27 2018
'''

import unittest

from morpho.utilities import morphologging
logger = morphologging.getLogger(__name__)

class IOTests(unittest.TestCase):
    
    def test_ROOTIO(self):
        from morpho.processors.IO import IOROOTProcessor
        writer_config = {
            "action": "write",
            "tree_name": "test",
            "filename": "myTest.root",
            "variables": [
                {
                "variable":"x",
                "root_alias":"x",
                "type":"int"
                },
                {
                "variable":"y"
                },
                {
                "variable":"list",
                "root_alias":"myList",
                "type":"float"
                }
            ]
        }
        reader_config = {
            "action": "read",
            "tree_name": "test",
            "filename": "myTest.root",
            "variables": ["x","y","myList"]
        }
        input_data = {
                        "x": [1,2,3,4,5,6], 
                        "y": [1.2,2.3,3.4,4.5,5.6,6.7],
                        "list": [[1.1,2.],[2.,3.],[3.,4.],[4.,5.],[5.,6.],[6.,7.]] }
        a = IOROOTProcessor("Writer")
        b = IOROOTProcessor("Reader")
        a.Configure(writer_config)
        b.Configure(reader_config)
        a.data = input_data
        b.data = a.Run()
        data = b.Run()
        logger.info("Data extracted = {}".format(data.keys()))
        for key in data.keys():
            logger.info("{} -> size = {}".format(key,len(data[key])))
            self.assertEqual(len(data[key]),6)

if __name__ == '__main__':
    unittest.main()