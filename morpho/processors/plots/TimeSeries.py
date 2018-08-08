'''
Plot a time series of the variables of interest
Authors: M. Guigue
Date: 06/26/18
'''

from __future__ import absolute_import

from morpho.utilities import morphologging, reader
from morpho.processors import BaseProcessor
from morpho.processors.plots import RootCanvas
logger = morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)


class TimeSeries(BaseProcessor):
    '''
    Time series plot generator.
    Display the value for each parameter (variables) as a time series.
    The red points are warmup part of the chain.

    Parameters:
        variables (required): name(s) of the variable in the data
        width: window width (default=600)
        height: window height (default=400)
        title: canvas title
        x_title: title of the x axis
        y_title: title of the y axis
        options: other options (logy, logx)
        output_path: where to save the plot
        output_pformat: plot format (default=pdf)

    Input:
        data: dictionary containing model input data

    Results:
        None
    '''

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    def InternalConfigure(self, param_dict):
        # Initialize Canvas: for some reason, the module or the class is
        # imported depending which script imports.
        try:
            self.rootcanvas = RootCanvas(param_dict, optStat=0)
        except:
            self.rootcanvas = RootCanvas.RootCanvas(param_dict, optStat=0)

        # Read other parameters
        self.namedata = reader.read_param(param_dict, 'variables', "required")
        return True

    def InternalRun(self):
        # Drawing and dividing the canvas
        self.rootcanvas.Draw()
        self.rootcanvas.Divide(1, len(self.namedata))

        listGraph = []
        listGraphWarmup = []
        iWarmup = 0
        iSample = 0
        # Plot all histograms
        try:
            import ROOT
        except ImportError:
            pass
        # Histograms must still be in memory when the pdf is saved
        for iName, name in enumerate(self.namedata):
            self.rootcanvas.cd(iName+1)
            listGraph.append(ROOT.TGraph())
            listGraphWarmup.append(ROOT.TGraph())
            subdata = self.data[str(name)]
            is_sample = self.data["is_sample"]
            iWarmup = 0
            iSample = 0
            for iValue, value in enumerate(subdata):
                if is_sample[iValue]:
                    listGraph[iName].SetPoint(iSample, iValue, value)
                    iSample = iSample + 1
                else:
                    listGraphWarmup[iName].SetPoint(iWarmup, iValue, value)
                    iWarmup += 1
            listGraph[iName].Draw("AP")
            listGraph[iName].SetMarkerStyle(7)
            listGraphWarmup[iName].Draw("sameP")
            listGraphWarmup[iName].SetMarkerStyle(7)
            listGraphWarmup[iName].SetMarkerColor(2)
            listGraph[iName].SetTitle(";Iteration;{}".format(name))

        self.rootcanvas.Save()
        return True
