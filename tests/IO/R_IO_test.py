'''
This scripts aims at testing the IO R processor by writing and reading the same file.
Author: M. Guigue
Date: Feb 27 2018
'''

from morpho.processors.IO import IORProcessor

writer_config = {
    "action": "write",
    "filename": "myFile.r",
    "variables": ["x","y"]
}

reader_config = {
    "action": "read",
    "filename": "myFile.r",
    "variables": ['x','y'],
}

data = {
    "x": [1,2,3],
    "y": [4,5,6,7]
}

a = IORProcessor("writer")
b = IORProcessor("reader")
a.Configure(writer_config)
b.Configure(reader_config)
a.data = data
a.Run()