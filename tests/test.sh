#!/bin/bash

echo "IO testing"
cd IO
python3 IO_test.py -vv || true
cd ..

echo "Misc testing"
cd misc
python3 misc_test.py -vv || true
cd ..

echo "Sampling testing"
cd sampling
python3 sampling_test.py -vv || true
cd ..

echo "Prior sampling testing"
cd sampling
python3 prior_sampling_test.py -vv || true
cd ..

echo "Diagnostics testing"
cd diagnostics
python3 diagnostics_test.py -vv || true
cd ..
