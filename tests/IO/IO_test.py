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
        reader_config = {
            "action": "write",
            "tree_name": "test",
            "filename": "myTest.root",
            "variables": ["x","y","list"]
        }
        input_data = {
                        "x": [1,2,3,4,5,6], 
                        "y": [1.2,2.3,3.4,4.5,5.6,6.7],
                        "list": [[1,2],[2,3],[3,4],[4,5],[5,6],[6,7]] }
        b = IOROOTProcessor("write")
        b.Configure(reader_config)
        b.data = input_data
        data = b.Run()
        # logger.info("Data extracted = {}".format(data.keys()))
        # for key in data.keys():
            # logger.info("{} -> size = {}".format(key,len(data[key])))
            # self.assertEqual(len(data[key]),22)

if __name__ == '__main__':
    unittest.main()