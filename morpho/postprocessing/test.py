#!/usr/bin/env python

#
# postprocessing.py
#
# Author: M. G. Guigue <mathieu.guigue@pnnl.gov>
#

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def test(dict):
    print("Hello world!")
    print(dict['name'])
    print(dict['output_name'])

def prout():
    print("prout")
