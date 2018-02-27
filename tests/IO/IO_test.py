from morpho.processors.IO import IOProcessor

config = {
    "action": "write",
    "filename": "myFile.cvs",
    "variables": ["x"],
    "format": "cvs"
}

data = {
    "x": [1,2,3],
    "y": [4,5,6,7]
}

a = IOProcessor("myIOProcessor")
a.Configure(config)
a.data = data
a.Run()