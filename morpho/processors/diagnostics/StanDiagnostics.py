'''
Creates Stan diagnostic plots.
'''

from __future__ import absolute_import

from morpho.utilities import morphologging, reader
from morpho.processors import BaseProcessor
logger=morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)

class StanDiagnostics(BaseProcessor):
    '''                                                                                                                                
    Describe.

    '''
    def __init__(self, *args, **kwargs):
        return

    def InternalConfigure(self, params):
        """Configures by reading in list of names of divergence plots to be created and dictionary containing fit object"""
        self.which_diag_plots = reader.read_param(params,"which_diag_plots")
        self.data = reader.read_param(params,"data",{})

    def InternalRun(self):
        import subprocess
        command = 'Rscript'
        path2script = 'bayesplot_diag.R'
        args = [self.data, self.which_diag_plots]
        cmd = [command, path2script] + args
        subprocess.check_output(cmd)
