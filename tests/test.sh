#!/bin/bash

cd IO && python IO_test.py -vv && cd ..
cd misc && python misc_test.py -vv && cd ..
cd sampling && python sampling_test.py -vv && cd ..