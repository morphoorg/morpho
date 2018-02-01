'''                                                                                                                                     
Creates Stan diagnostic plots.

'''

from __future__ import absolute_import

import json
import os

from morpho.utilities import morphologging, reader
from morpho.processors import SamplingBaseProcessor
logger=morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)

class StanDiagnostics(SamplingBaseProcessor):
    '''                                                                                                                                
    Describe.

    '''
    def __init__(self, *args, **kwargs):
        return

    def Configure(self, params):
        """Configures by reading in list of names of divergence plots to be created and dictionary containing fit object"""
        self.which_diag_plots = params["which_diag_plots"]
        self.data = params["data"]

    def Run(self):
        import subprocess
        command = 'Rscript'
        path2script = 'bayesplot_diag.R'
        args = [self.data, self.which_diag_plots]
        cmd = [command, path2script] + args
        subprocess.check_output(cmd)
        






