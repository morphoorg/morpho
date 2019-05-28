'''
A super simple module for unittest
'''

from math import sin, cos, sqrt, pow
from morpho.utilities import morphologging
logger = morphologging.getLogger(__name__)


def myFunction(x, a, b, c):
    # logger.info("This is my function: {},{},{},{} -> {}".format(x,a,b,c,abs(a*sin(b*x))))
    return abs(cos(b*x)+c)
    # return (x<a)*(a - x) * sqrt(pow(a - x, 2) - pow(b, 2)) + c
