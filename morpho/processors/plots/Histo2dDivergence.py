'''
Plot a posteriori distribution with divergent points colored
Authors: J. Jonhston, M. Guigue
Date: 05/20/2019
'''

from __future__ import absolute_import

from morpho.utilities import morphologging, reader, plots
from morpho.processors import BaseProcessor
from morpho.processors.plots import RootCanvas
logger = morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)


class Histo2dDivergence(BaseProcessor):
    '''
    Generates an a posterior distribution for all the parameters of interest
    TODO:
    - Use the RootHistogram class instead of TH1F itself...
    Parameters:
        n_bins_y: number of bins (default=100)
        n_bins_y: number of bins (default=100)
        variables (required): name(s) of the variable in the data
        width: window width (default=600)
        height: window height (default=400)
        title: canvas title
        x_title: title of the x axis
        y_title: title of the y axis
        options: other options (logy, logx)
        output_path: where to save the plot
        output_pformat: plot format (default=pdf)
    '''


    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self._data = dict()
        self.sample_warmup_sequence = list()

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def sample_warmup_sequence(self):
        return self._sample_warmup_sequence

    @sample_warmup_sequence.setter
    def sample_warmup_sequence(self, value):
        self._sample_warmup_sequence = value

    def InternalConfigure(self, param_dict):
        '''
        Configure
        '''
        # Initialize Canvas: for some reason, the module or the class is
        # imported depending which script imports.
        try:
            self.rootcanvas = RootCanvas(param_dict, optStat=0)
        except:
            self.rootcanvas = RootCanvas.RootCanvas(param_dict, optStat=0)

        # Read other parameters
        self.nbins_x = int(reader.read_param(param_dict, 'n_bins_x', 100))
        self.nbins_y = int(reader.read_param(param_dict, 'n_bins_y', 100))
        self.namedata = reader.read_param(param_dict, 'variables', "required")
        return True

    def InternalRun(self):
        name_grid, draw_opts_grid, colors_grid = plots._fill_variable_grid(self.namedata,
                                                                           "")
        hist_grid = plots._fill_hist_grid_divergence(self.data, name_grid,
                                                      self.nbins_x, self.nbins_y)


        rows = len(hist_grid)
        cols = len(hist_grid[0])
        # Drawing and dividing the canvas
        self.rootcanvas.Draw()
        self.rootcanvas.Divide(cols, rows)

        # Plot all histograms
        try:
            import ROOT
        except ImportError:
            pass
        # Histograms must still be in memory when the pdf is saved
        additional_hists = list()
        for r in range(rows):
            for c in range(cols):
                if(not hist_grid[r][c] is None):
                    ican = 1+r*cols+c
                    self.rootcanvas.cd(ican)
                    if(not colors_grid[r][c] is None):
                        color = colors_grid[r][c]
                    else:
                        color = ROOT.kRed
                    if(draw_opts_grid[r][c] == "bar" or
                       draw_opts_grid[r][c] == "hbar"):
                        hist_grid[r][c].SetFillColor(color+2)
                        hist_grid[r][c].Draw(draw_opts_grid[r][c])
                        # Overlay separate histograms for 1 and 2+ sigma
                        mean = hist_grid[r][c].GetMean()
                        sigma = hist_grid[r][c].GetStdDev()
                        name = hist_grid[r][c].GetName()
                        bins = hist_grid[r][c].GetNbinsX()
                        xmin = hist_grid[r][c].GetXaxis().GetXmin()
                        xmax = hist_grid[r][c].GetXaxis().GetXmax()
                        hist_1_sig = ROOT.TH1F("%s%s" % (name, "_1sig"),
                                               name, bins, xmin, xmax)
                        hist_1_sig.SetFillColor(color)
                        hist_2_sig = ROOT.TH1F("%s%s" % (name, "_2sig"),
                                               name, bins, xmin, xmax)
                        hist_2_sig.SetFillColor(color-4)
                        for i in range(1, bins):
                            bin_val = hist_grid[r][c].GetBinCenter(i)
                            if(bin_val < mean-2*sigma or bin_val > mean+2*sigma):
                                hist_2_sig.SetBinContent(
                                    i, hist_grid[r][c].GetBinContent(i))
                            elif(bin_val < mean-sigma or bin_val > mean+sigma):
                                hist_1_sig.SetBinContent(
                                    i, hist_grid[r][c].GetBinContent(i))
                        hist_1_sig.Draw("%s%s" %
                                        (draw_opts_grid[r][c], "same"))
                        hist_2_sig.Draw("%s%s" %
                                        (draw_opts_grid[r][c], "same"))
                        additional_hists.append(hist_1_sig)
                        additional_hists.append(hist_2_sig)
                    else:
                        # Color code by divergence
                        if not hist_grid[r][c][0] is None:
                            hist_grid[r][c][0].SetMarkerColor(ROOT.kBlack)
                            hist_grid[r][c][0].Draw(draw_opts_grid[r][c])
                        if not hist_grid[r][c][1] is None:
                            hist_grid[r][c][1].SetMarkerColor(ROOT.kRed)
                            hist_grid[r][c][1].Draw(draw_opts_grid[r][c]+"same")

        self.rootcanvas.Save()
        return True
