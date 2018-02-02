    
def read_param(yaml_data, node, default):
    data = yaml_data
    xpath = node.split('.')
    try:
        for path in xpath:
            data = data[path]
    except Exception as exc:
        if default == 'required':
            err = """FATAL: Configuration parameter {0} required but not\
            provided in config file!
            """.format(node)
            logger.debug(err)
            raise exc
        else:
            data = default
    return data