#!/bin/bash

echo "IO testing"
cd IO && python IO_test.py && cd ..

echo "Misc testing"
cd misc && python misc_test.py && cd ..

echo "Sampling testing"
cd sampling && python sampling_test.py && cd ..

echo "Prior sampling testing"
cd sampling && python prior_sampling_test.py && cd ..
