import logging
from morpho.utilities import morphologging, parser

def main():
    print("Testing logging features")
    args = parser.parse_args(False)
    logger = morphologging.getLogger('morpho',
                                     level=args.verbosity,
                                     stderr_lb=args.stderr_verbosity,
                                     propagate=False)
    print("Verbosity level: {}".format(args.verbosity))
    logger.critical("Critical")
    logger.error("Error")
    logger.warning("Warning")
    logger.info("Info")
    logger.debug("Debug")

    from morpho.processors.misc import ProcessorAssistant
    proc = ProcessorAssistant("name") # -> should print DEBUG: Creating processor <name> if verbosity=2 (-vv or more)

if __name__ == '__main__':
    main()