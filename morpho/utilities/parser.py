'''
Definitions for parsing the CLI and updating the Toolbox configuration dictionary
Authors: J. Johnston, M. Guigue, T. Weiss
Date: 06/26/18
'''

from argparse import ArgumentParser
import ast

from morpho.utilities import morphologging
logger = morphologging.getLogger(__name__)


def parse_args():
    '''Parse the command line arguments provided to morpho
    Args:
        None
    Returns:
        namespace: Namespace containing the arguments
    '''
    p = ArgumentParser(description='''
        An analysis tool for Project 8 data.
    ''')
    p.add_argument('-c', '--config',
                   metavar='<configuration file>',
                   help='Full path to the configuration file used by morpho',
                   required=True)
    # p.add_argument('--job_id',
    #                metavar='<job_id>',
    #                help='Job id number or string for batching',
    #                required=False)
    # p.add_argument('-s','--seed',
    #                metavar='<seed>',
    #                help='Add random seed number to file',
    #                required=False)
    # p.add_argument('-nas','--noautoseed',
    #                action='store_false',
    #                default=True,
    #                help='Generate the seed based on the current time in ms',
    #                required=False)
    p.add_argument('param', nargs='*',
                   default=False,
                   help='Manualy change of a parameter and its value')
    p.add_argument('-v', '--verbosity', default='DEBUG',
                   metavar='<verbosity>',
                   help="Specify verbosity of the logger, with options DEBUG, INFO, WARNING, ERROR, or CRITICAL (Default: DEBUG)",
                   choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                   required=False)
    p.add_argument('-sev', '--stderr-verbosity', default='WARNING',
                   metavar='<stderr_verbosity>',
                   help="Messages with level greater than or equal to the given verbosity will be redirected to stderr (Default: WARNING)",
                   choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                   required=False)
    return p.parse_args()


def update_from_arguments(the_dict, args):
    '''Update a dictionary
    Args:
        the_dict: Dictionary to update
        args: Dictionary to merge into the_dict
    Returns:
        dict: Dictionary with args merged into the_dict
    '''
    logger.debug('Update dict parameters')
    new_dict = the_dict
    for a_arg in args:
        result = a_arg.split('=')
        xpath = result[0].split('.')
        try:
            interpreted_val = ast.literal_eval(result[1])
        except:
            interpreted_val = str(result[1])
        to_update_dict = {xpath[-1]: interpreted_val}
        for path in reversed(xpath[:-1]):
            to_update_dict = {path: to_update_dict}
        new_dict = merge(new_dict, to_update_dict)
    return new_dict


def change_and_format(b):
    """Try to convert a string into a boolean or float
    Args:
        b: String containing a boolean or float
    Returns:
        bool, float, or str: If b == 'True' or 'False', then the
        corresponding boolean is returns. Otherwise, if b can be
        converted into a float, the float is returned. Otherwise
        b is returned.
    """
    if b == 'True':
        return True
    elif b == 'False':
        return False
    else:
        try:
            a = float(b)
            return a
        except:
            return b


def merge(a, b, path=None):
    '''Merge two dictionaries
    Args:
        a: Base dictionary
        b: Dictionary to merge into a
        path: Location to merge b at
    Returns:
        dict: Merged dictionary
    '''
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            else:
                a[key] = change_and_format(b[key])
        else:
            a[key] = change_and_format(b[key])
    return a
