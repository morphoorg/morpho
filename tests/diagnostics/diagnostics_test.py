'''
This scripts aims at testing diagnostics processors.
Author: M. Guigue
Date: June 3 2020
'''

import unittest
from ROOT import TRandom

from morpho.utilities import morphologging, parser
logger = morphologging.getLogger(__name__)

class DiagnosticsTests(unittest.TestCase):

    def test_CalibrationProc(self):
        logger.info("Processor Calibration test")
        from morpho.processors.diagnostics import CalibrationProcessor
        from morpho.processors.IO import IOROOTProcessor
        root_config = {
            "action": "write",
            "tree_name": "input",
            "filename": "calib.root",
            "variables": [
                {
                    "variable": "x",
                    "root_alias": "x",
                    "type": "float"
                }
            ]
        }
        
        proc_config = {
            "files": ["calib.root"],
            "in_param_names": "x",
            "root_in_tree": "input"
        }
        
        rootProc = IOROOTProcessor("ioRootProcessor")
        calibProc = CalibrationProcessor("calibProcessor")

        rootProc.Configure(root_config)
        calibProc.Configure(proc_config)

        rand = TRandom()
        rootProc.data = {"x": [ rand.Gaus(0, 1) for i in range(0, 1000)]}
        rootProc.filename = "calib.root"
        rootProc.Run()
        rootProc.tree_name = "analysis"
        rootProc.file_option = "UPDATE"
        rootProc.Run()

        calibProc.Run()

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
