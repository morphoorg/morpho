'''
This scripts aims at testing miscellaneous processors.
Author: M. Guigue
Date: Mar 30 2018
'''

import unittest

from morpho.utilities import morphologging, parser
logger = morphologging.getLogger(__name__)

class MiscTests(unittest.TestCase):

    def test_ProcAssistant(self):
        logger.info("Processor Assistant test")
        from morpho.processors.misc import ProcessorAssistant
        proc_config = {
            "function_name": "myFunction",
            "module_name": "myModule",
            "value": 10
        }
        assistantProcessor = ProcessorAssistant("assistantProcessor")
        assistantProcessor.Configure(proc_config)
        assistantProcessor.Run()
        logger.debug("Assistant processor returned: {}".format(assistantProcessor.results))
        self.assertEqual(assistantProcessor.results,"value=10")

if __name__ == '__main__':

    args = parser.parse_args(False)
    logger = morphologging.getLogger('morpho',
                                     level=args.verbosity,
                                     stderr_lb=args.stderr_verbosity,
                                     propagate=False)
    logger = morphologging.getLogger(__name__,
                                     level=args.verbosity,
                                     stderr_lb=args.stderr_verbosity,
                                     propagate=False)
    unittest.main()