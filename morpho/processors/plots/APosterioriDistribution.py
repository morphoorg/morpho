'''                                                                                                                                     
Plot a posteriori distribution of the variables of interest
'''

from __future__ import absolute_import

import json
import os

from morpho.utilities import morphologging, reader, plots
from morpho.processors import BaseProcessor
logger=morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)

class APosterioriDistribution(BaseProcessor):
    '''                                                                                                                                
    Describe.
    '''

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self,value):
        self._data = value

    def Configure(self, param_dict):
        '''
        Configure
        '''
        self.nbins_x = int(reader.read_param(param_dict,'n_bins_x',100))
        self.nbins_y = int(reader.read_param(param_dict,'n_bins_y',100))
        self.namedata = reader.read_param(param_dict,'data',"required")
        self.draw_opt_2d = reader.read_param(param_dict,'root_plot_option',"contz")
        

    def Run(self):

    # Populate a grid of histograms with the parameters
        # if 'n_bins_x' in param_dict:
        #     nbins_x = param_dict['n_bins_x']
        # else:
        #     nbins_x = 100
        # if 'n_bins_y' in param_dict:
        #     nbins_y = param_dict['n_bins_y']
        # else:
        #     nbins_y = 100

        # if 'data' in param_dict:
        #     namedata = param_dict['data']
            

        # if 'root_plot_option' in param_dict:
        #     draw_opt_2d = param_dict['root_plot_option']
        # else:
        #     draw_opt_2d = 'contz'

        name_grid, draw_opts_grid, colors_grid =plots._fill_variable_grid(self.namedata,
                                                                    self.draw_opt_2d)
        # print(name_grid)
        # print(draw_opts_grid)
        # print(colors_grid)
        # myfile = ROOT.TFile(param_dict['input_file_name'],"READ")
        # input_tree_name = param_dict['input_tree']
        hist_grid = plots._fill_hist_grid(self.data, name_grid,
                                    self.nbins_x, self.nbins_y)
        
        # Preparing the canvas
        logger.debug("Preparing Canvas")
        # title, width, height = plots._preparingCanvas(param_dict)
        import ROOT
        can = ROOT.TCanvas("test","test",600,400)
        can.Draw()
        # if 'options' in param_dict:
        #     if "logy" in param_dict['options']:
        #         can.SetLogy()

        # Setting the titles
        logger.debug("Preparing Titles")
        # xtitle, ytitle = self._preparingTitles(param_dict)
        xtitle = "x"
        ytitle = 'y'

        gSave = []
    
        # Plot all histograms
        ROOT.gStyle.SetOptStat(0)
        rows = len(hist_grid)
        cols = len(hist_grid[0])
        can.Divide(cols,rows)
        # Histograms must still be in memory when the pdf is saved
        additional_hists = list()
        for r in range(rows):
            for c in range(cols):
                if(not hist_grid[r][c] is None):
                    ican = 1+r*cols+c
                    can.cd(ican)
                    if(not colors_grid[r][c] is None):
                        color = colors_grid[r][c]
                    else:
                        color = ROOT.kRed
                    hist_grid[r][c].SetFillColor(color+2)
                    hist_grid[r][c].Draw(draw_opts_grid[r][c])
                    if(draw_opts_grid[r][c]=="bar" or
                    draw_opts_grid[r][c]=="hbar"):
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
                        for i in range(1,bins):
                            bin_val = hist_grid[r][c].GetBinCenter(i)
                            if(bin_val<mean-2*sigma or bin_val>mean+2*sigma):
                                hist_2_sig.SetBinContent(i, hist_grid[r][c].GetBinContent(i))
                            elif(bin_val<mean-sigma or bin_val>mean+sigma):
                                hist_1_sig.SetBinContent(i, hist_grid[r][c].GetBinContent(i))
                        hist_1_sig.Draw("%s%s" % (draw_opts_grid[r][c], "same"))
                        hist_2_sig.Draw("%s%s" % (draw_opts_grid[r][c], "same"))
                        additional_hists.append(hist_1_sig)
                        additional_hists.append(hist_2_sig)
                    
        # Save the plot
        # if 'output_path' in param_dict:
        #     path = param_dict['output_path']
        # else:
        #     path = "./"
        # if path.endswith('/')==False:
        #     path = path + '/'
        # if title!=' ':
        #     figurefullpath = path+title+'_'
        # else:
        #     figurefullpath = path
        # for namedata in param_dict['data']:
        #     figurefullpath += namedata + '_'
        # if figurefullpath.endswith('_'):
        #     figurefullpath = figurefullpath[:-1]
        # if 'output_format' in param_dict:
        #     figurefullpath += '.' + param_dict['output_format']
        # else:
        #     figurefullpath += '.pdf'
        # can.Update()

        can.SaveAs("plots/aposteriori.pdf")
        return can