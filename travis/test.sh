#!/bin/bash
# Test script
# Author: M. Guigue
# Date: 06/09/2018

# Let's go with the tests!
cd tests/IO && python3 IO_test.py || exit 1
cd ../misc && python3 misc_test.py || exit 1
cd ../sampling && python3 sampling_test.py || exit 1

cd ../../examples
morpho -c linear_fit/scripts/morpho_linear.yaml || exit 1
cd ../..