# Source root
. /usr/local/bin/thisroot.sh
# Let's go with tests!
cd tests/IO && python3 IO_test.py
cd ../IO && python3 CVS_IO_test.py
cd ../IO && python3 R_IO_test.py
cd ../misc && python3 misc_test.py
cd ../sampling && python3 sampling_test.py