'''
This scripts aims at testing the IO CVS processor by writing and reading the same file.
Author: M. Guigue
Date: Feb 27 2018
'''

from morpho.processors.IO import IOROOTProcessor

writer_config = {
    "action": "write",
    "filename": "myFile.root",
    "variables": ["x","y"],
    "format": "root",
    "tree_name": "tree"
}

reader_config = {
    "action": "read",
    "filename": "myFile.txt",
    "variables": ['x','y'],
    "format": "csv"
}

data = {
    "x": [1.,2.,3.],
    "y": [4,5,6,7]
}

a = IOROOTProcessor("writer")
# b = IOCVSProcessor("reader")
a.Configure(writer_config)
# b.Configure(reader_config)
a.data = data
a.Run()