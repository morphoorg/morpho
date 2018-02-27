from morpho.processors.IO import IOCVSProcessor

config = {
    "action": "write",
    "filename": "myFile.txt",
    "variables": ["x","y"],
    "format": "cvs"
}

reader_config = {
    "action": "read",
    "filename": "myFile.txt",
    "variables": ['x'],
    "format": "csv"
}

data = {
    "x": [1,2,3],
    "y": [4,5,6,7]
}

a = IOCVSProcessor("writer")
b = IOCVSProcessor("reader")
a.Configure(config)
b.Configure(reader_config)
a.data = data
a.Run()
print(b.Run())