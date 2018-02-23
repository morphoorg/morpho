'''
Morpho logging utilities
Authors: J. Johnston, M. Guigue
Date: 02/22/18
'''

from __future__ import absolute_import

import os,sys
try:
    reload  # Python 2.7
except NameError:
    try:
        from importlib import reload  # Python 3.4+
    except ImportError:
        from imp import reload  # Python 3.0 - 3.3
    reload(sys)
# sys.setdefaultencoding("utf-8")

import logging
import colorlog

def getLogger(name, stderr_lb=logging.ERROR,
                      level=logging.DEBUG, propagate=False):
    """Return a logger object with the given settings that prints
    messages greater than or equal to a given level to stderr instead of stdout
    name: Name of the logger. Loggers are conceptually arranged
          in a namespace hierarchy using periods as separators.
          For example, a logger named morpho is the parent of a
          logger named morpho.plot, and by default the child logger
          will display messages with the same settings as the parent
    stderr_lb: Messages with level equal to or greaterthan stderr_lb
               will be printed to stderr instead of stdout
    level: Initial level for the logger
    propagate: Whether messages to this logger should be passed to
               the handlers of its ancestor"""

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = propagate

    class LessThanFilter(logging.Filter):
        """Filter to get messages less than a given level
        """
        def __init__(self, exclusive_maximum, name=""):
            super(LessThanFilter, self).__init__(name)
            self.max_level = exclusive_maximum

        def filter(self, record):
            #non-zero return means we log this message
            return 1 if record.levelno < self.max_level else 0

    base_format = '%(asctime)s{}[%(levelname)-8s] %(name)s(%(lineno)d) -> {}%(message)s'
    morpho_formatter = colorlog.ColoredFormatter(
        base_format.format('%(log_color)s', '%(purple)s'),
        datefmt = '%Y-%m-%dT%H:%M:%SZ'[:-1],
        reset=True,
        )

    logger.handlers = []
    handler_stdout = logging.StreamHandler(sys.stdout)
    handler_stdout.setFormatter(morpho_formatter)
    handler_stdout.setLevel(logging.DEBUG)
    handler_stdout.addFilter(LessThanFilter(stderr_lb))
    logger.addHandler(handler_stdout)
    handler_stderr = logging.StreamHandler(sys.stderr)
    handler_stderr.setFormatter(morpho_formatter)
    handler_stderr.setLevel(stderr_lb)
    logger.addHandler(handler_stderr)
    # Create morpho and pystan loggers
    # Will be reinstantiated after parsing command line args if __main__ is run

    return logger

