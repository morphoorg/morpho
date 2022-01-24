'''
A super simple module for unittest
'''

from math import cos
from morpho.utilities import morphologging
logger = morphologging.getLogger(__name__)


def myPdf(x, a, b, c):
    return abs(cos(b*x)+c)
