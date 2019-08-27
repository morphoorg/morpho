'''
A super simple module for unittest
'''

from math import sin, cos, sqrt, pow
from morpho.utilities import morphologging
logger = morphologging.getLogger(__name__)


def myFunction(x, a, b, c):
    return abs(cos(b*x)+c)
