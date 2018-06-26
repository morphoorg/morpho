'''
This scripts aims at testing miscellaneous processors.
Author: M. Guigue
Date: Mar 30 2018
'''

import unittest

from morpho.utilities import morphologging
logger = morphologging.getLogger(__name__)

class MiscTests(unittest.TestCase):

    def test_ProcAssistant(self):
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
    unittest.main()