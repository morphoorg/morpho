#!/bin/bash

echo "IO testing"
cd IO && python IO_test.py -vv && cd ..

echo "Misc testing"
cd misc && python misc_test.py -vv && cd ..

echo "Sampling testing"
cd sampling && python sampling_test.py -vv && cd ..

echo "Prior sampling testing"
cd sampling && python prior_sampling_test.py -vv && cd ..
