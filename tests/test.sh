#!/bin/bash

# missing scipy (required only for testing)
pip3 install scipy

cd IO && python IO_test.py && cd ..
cd misc && python misc_test.py && cd ..
cd sampling && python sampling_test.py && cd ..