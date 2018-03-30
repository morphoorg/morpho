'''
Interface between config files and processors config dictionaries
'''

from morpho.utilities import morphologging
logger = morphologging.getLogger(__name__)

def read_param(yaml_data, node, default):
    data = yaml_data
    xpath = node.split('.')
    try:
        for path in xpath:
            data = data[path]
    except KeyError as exc:
        if default == 'required':
            err = "Configuration parameter {0} required but not provided in config file!".format(node)
            logger.error(err)
            raise exc
        else:
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
        key_err = "Cannot add key {} to dictionary. That key is taken.".format(key) 
        logger.error(key_err)
        raise
    else:
        dictionary.update({key:value})
    return dictionary   