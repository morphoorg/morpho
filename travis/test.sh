#!/bin/bash
# Test script
# Author: M. Guigue
# Date: 06/09/2018

# Source root
. /usr/local/bin/thisroot.sh
# Let's go with the tests!
cd tests/IO && python3 IO_test.py
cd ../IO && python3 CVS_IO_test.py
cd ../IO && python3 R_IO_test.py
cd ../misc && python3 misc_test.py
cd ../sampling && python3 sampling_test.py