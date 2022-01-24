'''
Interface between config files and processors config dictionaries
Authors: J. Johnston, M. Guigue, T. Weiss
Date: 06/26/18
'''

from morpho.utilities import morphologging
logger = morphologging.getLogger(__name__)


def read_param(yaml_data, node, default):
    """
    Recursively parse a path (separated by .) and retrive the value from the yaml_data dictionary.
    If the value is required but not present, raises an exception.
    If not required and not present, it returns the default value.
    """
    data = yaml_data
    xpath = node.split('.')
    try:
        for path in xpath:
            data = data[path]
    except KeyError as exc:
        if default == 'required':
            logger.error(f"Configuration parameter {node} required but not provided in config file!")
            raise exc
        data = default
    return data


def add_dict_param(dictionary, key, value):
    '''
    This method checks if a key already exists in a dictionary,
    and if not, it adds the key and its corresponding value to
    the dictionary.

    Could be changed to take as input a list of tuples (key, value),
    so multiple parameters may be added at once.
    '''
    if key in dictionary:
        logger.error(f"Cannot add key {key} to dictionary. That key is taken.")
        raise ValueError
    dictionary.update({key: value})
    return dictionary
