'''
This scripts aims at testing IO processors by reading/writing files.
Author: M. Guigue
Date: Feb 27 2018
'''

import unittest

from morpho.utilities import morphologging
logger = morphologging.getLogger(__name__)


input_data = {
    "x": [1, 2, 3, 4, 5, 6],
    "y": [1.2, 2.3, 3.4, 4.5, 5.6, 6.7],
    "list": [[1.1, 2.], [2., 3.], [3., 4.], [4., 5.], [5., 6.], [6., 7.]]
}


class IOTests(unittest.TestCase):

    def test_JSONIO(self):
        logger.info("JSONIO test")
        from morpho.processors.IO import IOJSONProcessor, IOYAMLProcessor
        writer_config = {
            "action": "write",
            "filename": "myTest.json",
            "variables": [
                "x",
                {
                    "variable": "y"
                },
                {
                    "variable": "list",
                    "json_alias": "myList"
                }
            ]
        }
        reader_config = {
            "action": "read",
            "filename": "myTest.json",
            "variables": ["x", "y", "myList"]
        }
        a = IOJSONProcessor("WriterJSON")
        b = IOJSONProcessor("ReaderJSON")
        c = IOYAMLProcessor("WriterYAML")
        d = IOYAMLProcessor("ReaderYAML")

        a.Configure(writer_config)
        b.Configure(reader_config)
        writer_config.update({"filename": "myTest.yaml"})
        reader_config.update({"filename": "myTest.yaml"})
        c.Configure(writer_config)
        d.Configure(reader_config)

        a.data = input_data
        a.Run()
        b.Run()
        data = b.data
        logger.info("Data extracted = {}".format(data.keys()))
        for key in data.keys():
            logger.info("{} -> size = {}".format(key, len(data[key])))
            self.assertEqual(len(data[key]), 6)
        c.data = input_data
        c.Run()
        d.Run()
        data2 = d.data
        for key in data2.keys():
            logger.info("{} -> size = {}".format(key, len(data2[key])))
            self.assertEqual(len(data2[key]), 6)

    def test_ROOTIO(self):
        logger.info("IOROOT test")
        from morpho.processors.IO import IOROOTProcessor
        writer_config = {
            "action": "write",
            "tree_name": "test",
            "filename": "myTest.root",
            "variables": [
                {
                    "variable": "x",
                    "root_alias": "x",
                    "type": "int"
                },
                {
                    "variable": "y"
                },
                {
                    "variable": "list",
                    "root_alias": "myList",
                    "type": "float"
                }
            ]
        }
        reader_config = {
            "action": "read",
            "tree_name": "test",
            "filename": "myTest.root",
            "variables": ["x", "y", "myList"]
        }
        a = IOROOTProcessor("WriterROOT")
        b = IOROOTProcessor("ReaderROOT")
        a.Configure(writer_config)
        b.Configure(reader_config)
        a.data = input_data
        a.Run()
        b.Run()
        data = b.data
        logger.info("Data extracted = {}".format(data.keys()))
        for key in data.keys():
            logger.info("{} -> size = {}".format(key, len(data[key])))
            self.assertEqual(len(data[key]), 6)

    def test_RIO(self):
        logger.info("IOR test")
        from morpho.processors.IO import IORProcessor
        writer_config = {
            "action": "write",
            "filename": "myFile.r",
            "variables": ["x", "y"]
        }

        reader_config = {
            "action": "read",
            "filename": "myFile.r",
            "variables": ['x', 'y'],
        }

        a = IORProcessor("writer")
        b = IORProcessor("reader")
        a.Configure(writer_config)
        b.Configure(reader_config)
        a.data = input_data
        a.Run()
        b.Run()
        data = b.data
        logger.info("Data extracted = {}".format(data.keys()))
        for key in data.keys():
            logger.info("{} -> size = {}".format(key, len(data[key])))
            self.assertEqual(len(data[key]), 6)

    def test_CVSIO(self):
        logger.info("IOCVS test")
        from morpho.processors.IO import IOCVSProcessor
        writer_config = {
            "action": "write",
            "filename": "myFile.txt",
            "variables": ["x", "y"],
            "format": "cvs"
        }

        reader_config = {
            "action": "read",
            "filename": "myFile.txt",
            "variables": ['x', 'y'],
            "format": "csv"
        }

        a = IORProcessor("writer")
        b = IORProcessor("reader")
        a.Configure(writer_config)
        b.Configure(reader_config)
        a.data = input_data
        a.Run()
        b.Run()
        data = b.data
        logger.info("Data extracted = {}".format(data.keys()))
        for key in data.keys():
            logger.info("{} -> size = {}".format(key, len(data[key])))
            self.assertEqual(len(data[key]), 6)

if __name__ == '__main__':
    unittest.main()
