#!/usr/bin/env python

#
# postprocessing.py
#
# Author: M. G. Guigue <mathieu.guigue@pnnl.gov>
#

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import re
import fileinput

from h5py import File as HDF5
from yaml import load as yload
from argparse import ArgumentParser
from inspect import getargspec

from hashlib import md5
