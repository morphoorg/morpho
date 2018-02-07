#======================================================
# histo.py
#
# Author: M. Guigue, T. E. Weiss
# Date: Aug. 4, 2016
#
# Description:
#
# Generic methods to display histograms with ROOT
#=======================================================

"""
Contains generic methods to plot ROOT histograms (1D and 2D)
List of methods:
- histo: plot a 1D histogram using a list of data (x)
- spectra: plot a 1D histogram using two lists of data (x,bin_content)
- histo2D: plot a 2D histogram using two lists of data (x,y)
- histo2D_divergence: plot a 2D histogram using two lists of data (x,y), and color points
                      with divergence==1 differently from divergence==0
- aposteriori_distribution: plot a serie of 2D histograms using a list of data names (>=3).
It will form pairs of variables (x,y) and arrange the 2D histograms to get a view
of the aposteriori distributio for these parameters
- correlation_factors: Plot a grid where a color represents the
correlation factor between each pair of variables.
"""

import logging
logger = logging.getLogger(__name__)
try:
    import ROOT as ROOT
    import numpy as np
except ImportError:
    pass
import cmath as math
from array import array
import re
import uuid


def histo(param_dict):
    '''
    Create a histogram using a list of X
    '''

    # Preparing the canvas
    logger.debug("Preparing Canvas")
    title, width, height = _preparingCanvas(param_dict)
    can = ROOT.TCanvas(title,title,width,height)
    if 'options' in param_dict.keys():
        if any("logy" in s for s in param_dict['options']):
            logger.debug("Setting Log Y")
            can.SetLogy()
    # Setting the titles
    logger.debug("Preparing Titles")
    xtitle, ytitle = _preparingTitles(param_dict)

    gSave = []
    j = 0

    if isinstance(param_dict['data'],list):

        if 'n_bins' in param_dict:
            nbins = param_dict['n_bins']
        else:
            nbins = 100
        list_histo = []

        myfile = ROOT.TFile(param_dict['input_file_name'],"READ")
        for namedata in param_dict['data']:
            list_data = []
            # myfile.Close()
            tree = myfile.Get(param_dict['input_tree'])
            n = tree.GetEntries()
            for i in range(0,n):
                tree.GetEntry(i)
                list_data.append(getattr(tree,namedata))
                # list_data.append(20*j+18510)

            # list_histo.append()
            if 'x_range' in param_dict:
                if isinstance(param_dict['x_range'],list):

                    if (isinstance(param_dict['x_range'][0],float) or isinstance(param_dict['x_range'][0],int)) and (isinstance(param_dict['x_range'][1],float) or isinstance(param_dict['x_range'][1],int)):
                        if  param_dict['x_range'][0] < param_dict['x_range'][1]:
                            xmin = param_dict['x_range'][0]
                            xmax = param_dict['x_range'][1]
                        else:
                            xmin,xmax = _autoRangeList(list_data)
                    elif isinstance(param_dict['x_range'][0],float):
                        xtemp,xmax = _autoRangeList(list_data)
                        xmin = param_dict['x_range'][0]
                    elif isinstance(param_dict['x_range'][1],float):
                        xmin,xtemp = _autoRangeList(list_data)
                        xmax = param_dict['x_range'][1]
                    else:
                        xmin,xmax = _autoRangeList(list_data)
                else:
                    xmin,xmax = _autoRangeList(list_data)
            else:
                xmin,xmax = _autoRangeList(list_data)
            list_histo.append(ROOT.TH1F(namedata,namedata,nbins,xmin,xmax))
            for i in range(0,n):
                list_histo[j].Fill(list_data[i])
            can.cd()
            if (j==0):
                list_histo[j].Draw('hist')
                list_histo[j].GetXaxis().SetTitle(xtitle);
                list_histo[j].SetTitle(title)
                if 'y_range' in param_dict and isinstance(param_dict['y_range'],list):
                    if (isinstance(param_dict['y_range'][0],float) or isinstance(param_dict['y_range'][0],int)) and (isinstance(param_dict['y_range'][1],float) or isinstance(param_dict['y_range'][1],int)):
                        if  param_dict['y_range'][0] < param_dict['y_range'][1]:
                            list_histo[j].GetYaxis().SetRangeUser(param_dict['y_range'][0],param_dict['y_range'][1])
                    elif isinstance(param_dict['y_range'][0],float):
                        ytemp,ymax = _autoRangeContent(list_histo[j])
                        ymin = param_dict['y_range'][0]
                        list_histo[j].GetYaxis().SetRangeUser(ymin,ymax)
                    elif isinstance(param_dict['y_range'][1],float):
                        ymin,ytemp = _autoRangeContent(list_histo[j])
                        ymax = param_dict['y_range'][1]
                        list_histo[j].GetYaxis().SetRangeUser(ymin,ymax)
            else:
                list_histo[j].Draw("SAME")
            # gSave.append(list_histo[j])
            can.Update()


            j=j+1
    gSave.append(can)

    # Setting the picture file name
    if 'output_path' in param_dict:
        path = param_dict['output_path']
    else:
        path = "./"
    if path.endswith('/')==False:
        path = path + '/'
    if title!=' ':
        figurefullpath = path+title+'_'
    else:
        figurefullpath = path
    for namedata in param_dict['data']:
        figurefullpath += namedata + '_'
    if figurefullpath.endswith('_'):
        figurefullpath = figurefullpath[:-1]
    if 'output_format' in param_dict:
        figurefullpath += '.' + param_dict['output_format']
    else:
        figurefullpath += '.pdf'
    can.SaveAs(figurefullpath)

    return can


def spectra(param_dict):
    '''
    Create a spectrum using a (X,Y) list
    '''
    # Preparing the canvas
    logger.debug("Preparing Canvas")
    title, width, height = _preparingCanvas(param_dict)
    can = ROOT.TCanvas(title,title,width,height)
    if "logy" in param_dict.options:
        can.SetLogy()

    # Setting the titles
    logger.debug("Preparing Titles")
    xtitle, ytitle = _preparingTitles(param_dict)

    gSave = []
    j = 0

    if isinstance(param_dict['data'],list):

        if 'n_bins' in param_dict:
            nbins = param_dict['n_bins']
        else:
            nbins = 100
        list_histo = []

        myfile = ROOT.TFile(param_dict['input_file_name'],"READ")
        for namedata in param_dict['data']:
            if not isinstance(namedata, list):
                logger.critical(' {} is not a list of list; required for spectra ploting; skipping'.format(namedata))
                continue
            list_dataX = []
            list_dataY = []
            # myfile.Close()
            tree = myfile.Get(param_dict['input_tree'])
            n = tree.GetEntries()
            for i in range(0,n):
                tree.GetEntry(i)
                list_dataX.append(getattr(tree,namedata[0]))
                list_dataY.append(getattr(tree,namedata[1]))

            # list_histo.append()
            # logger.debug('Setting x axis')
            if 'x_range' in param_dict:
                if isinstance(param_dict['x_range'],list):

                    if (isinstance(param_dict['x_range'][0],float) or isinstance(param_dict['x_range'][0],int)) and (isinstance(param_dict['x_range'][1],float) or isinstance(param_dict['x_range'][1],int)):
                        if  param_dict['x_range'][0] < param_dict['x_range'][1]:
                            xmin = param_dict['x_range'][0]
                            xmax = param_dict['x_range'][1]
                        else:
                            xmin,xmax = _autoRangeList(list_dataX)
                    elif isinstance(param_dict['x_range'][0],float):
                        xtemp,xmax = _autoRangeList(list_dataX)
                        xmin = param_dict['x_range'][0]
                    elif isinstance(param_dict['x_range'][1],float):
                        xmin,xtemp = _autoRangeList(list_dataX)
                        xmax = param_dict['x_range'][1]
                    else:
                        xmin,xmax = _autoRangeList(list_dataX)
                else:
                    xmin,xmax = _autoRangeList(list_dataX)
            else:
                xmin,xmax = _autoRangeList(list_dataX)
            histo_title = '{}_vs_{}'.format(namedata[1],namedata[0])
            list_histo.append(ROOT.TH1F(histo_title,histo_title,nbins,xmin,xmax))
            for i in range(0,n):
                list_histo[j].Fill(list_dataX[i],list_dataY[i])
            can.cd()
            if (j==0):
                list_histo[j].Draw('hist')
                list_histo[j].GetXaxis().SetTitle(xtitle);
                list_histo[j].SetTitle(title)
                if 'y_range' in param_dict and isinstance(param_dict['y_range'],list):
                    if (isinstance(param_dict['y_range'][0],float) or isinstance(param_dict['y_range'][0],int)) and (isinstance(param_dict['y_range'][1],float) or isinstance(param_dict['y_range'][1],int)):
                        if  param_dict['y_range'][0] < param_dict['y_range'][1]:
                            list_histo[j].GetYaxis().SetRangeUser(param_dict['y_range'][0],param_dict['y_range'][1])
                    elif isinstance(param_dict['y_range'][0],float):
                        ytemp,ymax = _autoRangeContent(list_histo[j])
                        ymin = param_dict['y_range'][0]
                        list_histo[j].GetYaxis().SetRangeUser(ymin,ymax)
                    elif isinstance(param_dict['y_range'][1],float):
                        ymin,ytemp = _autoRangeContent(list_histo[j])
                        ymax = param_dict['y_range'][1]
                        list_histo[j].GetYaxis().SetRangeUser(ymin,ymax)
            else:
                list_histo[j].Draw("SAME")
            # gSave.append(list_histo[j])
            can.Update()


            j=j+1
    gSave.append(can)

    # Setting the picture file name
    if 'output_path' in param_dict:
        path = param_dict['output_path']
    else:
        path = "./"
    if path.endswith('/')==False:
        path = path + '/'
    if title!=' ':
        figurefullpath = path+title+'_'
    else:
        figurefullpath = path
    for namedata in param_dict['data']:
        figurefullpath += namedata[1] + '_vs_'
        figurefullpath += namedata[0] + '_'
    if figurefullpath.endswith('_'):
        figurefullpath = figurefullpath[:-1]
    if 'output_format' in param_dict:
        figurefullpath += '.' + param_dict['output_format']
    else:
        figurefullpath += '.pdf'
    can.SaveAs(figurefullpath)

    return can

def _prepare_canvas_2d(param_dict):
    '''Prepare a canvas for a 2D histogram'''
    # Preparing the canvas
    logger.debug("Preparing Canvas")
    title, width, height = _preparingCanvas(param_dict)
    can = ROOT.TCanvas(title,title,width,height)

    if 'options' in param_dict:
        if "logy" in param_dict['options']:
            can.SetLogy()
        if "logx" in param_dict['options']:
            can.SetLogx()

    # Setting the titles
    logger.debug("Preparing Titles")
    xtitle, ytitle = _preparingTitles(param_dict)

    gSave = []

    if 'n_bins_x' in param_dict:
        nbins_x = param_dict['n_bins_x']
    else:
        nbins_x = 100
    if 'n_bins_y' in param_dict:
        nbins_y = param_dict['n_bins_y']
    else:
        nbins_y = 100

    return can, title, nbins_x, nbins_y

def _get_root_data_2d(param_dict, myfile):
    '''Get data for a 2D histogram
    The corresponding root file must already be open'''
    if 'data' in param_dict:
        namedata = param_dict['data']
    if not isinstance(namedata, list):
        logger.critical(' {} is not a list of list; required for spectra ploting; skipping'.format(namedata))
        return None, None, namedata
    list_dataX = []
    list_dataY = []
    # myfile.Close()
    tree = myfile.Get(param_dict['input_tree'])
    n = tree.GetEntries()
    for i in range(0,n):
        tree.GetEntry(i)
        list_dataX.append(getattr(tree,namedata[0]))
        list_dataY.append(getattr(tree,namedata[1]))
    return list_dataX, list_dataY, namedata

def _get_root_data_2d_divergence(param_dict, myfile):
    '''Get data for a 2D histogram
    The corresponding root file must already be open'''
    if 'data' in param_dict:
        namedata = param_dict['data']
    if not isinstance(namedata, list):
        logger.critical(' {} is not a list of list; required for spectra ploting; skipping'.format(namedata))
        return None, None, None, None, namedata

    tree = myfile.Get(param_dict['input_tree'])

    # Check that the tree has divergence
    tree.GetEntry(0)
    if not hasattr(tree, "divergence"):
        logger.critical('Tree %s does not contain divergence; skipping' % param_dict['input_tree'])
        return None, None, None, None, namedata

    n = tree.GetEntries()
    list_dataX_div0 = []
    list_dataX_div1 = []
    list_dataY_div0 = []
    list_dataY_div1 = []

    for i in range(0,n):
        tree.GetEntry(i)
        if(getattr(tree, "divergence")==0):
            list_dataX_div0.append(getattr(tree,namedata[0]))
            list_dataY_div0.append(getattr(tree,namedata[1]))
        else:
            list_dataX_div1.append(getattr(tree,namedata[0]))
            list_dataY_div1.append(getattr(tree,namedata[1]))
    arr_x0 = np.array(list_dataX_div0)
    arr_y0 = np.array(list_dataY_div0)
    arr_x1 = np.array(list_dataX_div1)
    arr_y1 = np.array(list_dataY_div1)
    return arr_x0, arr_y0, arr_x1, arr_y1, namedata

def _save_histo(param_dict, title, file_prefix, can):
    # Setting the picture file name
    if 'output_path' in param_dict:
        path = param_dict['output_path']
    else:
        path = "./"
    if path.endswith('/')==False:
        path = path + '/'
    if title!=' ':
        figurefullpath = path+title+'_'
    else:
        figurefullpath = path
    figurefullpath += file_prefix
    for namedata in param_dict['data']:
        figurefullpath += namedata + '_'
    if figurefullpath.endswith('_'):
        figurefullpath = figurefullpath[:-1]
    if 'output_format' in param_dict:
        figurefullpath += '.' + param_dict['output_format']
    else:
        figurefullpath += '.pdf'
    can.SaveAs(figurefullpath)
    return

def histo2D(param_dict):
    '''
    Plot 2D histogram
    '''
    can, title, nbins_x, nbins_y = _prepare_canvas_2d(param_dict)
    myfile = ROOT.TFile(param_dict['input_file_name'],"READ")
    list_dataX, list_dataY, namedata = _get_root_data_2d(param_dict, myfile)
    if(list_dataX is None):
        return

    histo = _get2Dhisto(list_dataX, list_dataY, [nbins_x,nbins_y], [0,0], title)
    histo.GetXaxis().SetTitle(namedata[0])
    histo.GetYaxis().SetTitle(namedata[1])

    if 'root_plot_option' in param_dict:
        histo.Draw(param_dict['root_plot_option'])
    else:
        histo.Draw('contz')
    _save_histo(param_dict, title, "", can)
    return can

def histo2D_divergence(param_dict):
    '''
    Plot 2D histogram
    '''
    can, title, nbins_x, nbins_y = _prepare_canvas_2d(param_dict)
    myfile = ROOT.TFile(param_dict['input_file_name'],"READ")
    arr_X_div0, arr_Y_div0, \
        arr_X_div1, arr_Y_div1, \
        namedata = _get_root_data_2d_divergence(param_dict, myfile)

    if(arr_X_div0 is None):
        return
    xmin = np.amin(np.concatenate((arr_X_div0,
                                   arr_X_div1),axis=0))
    xmax = np.amax(np.concatenate((arr_X_div0,
                                   arr_X_div1),axis=0))
    dx = xmax-xmin
    xmin = xmin-dx*0.05
    xmax = xmax+dx*0.05
    ymin = np.amin(np.concatenate((arr_Y_div0,
                                   arr_Y_div1),axis=0))
    ymax = np.amax(np.concatenate((arr_Y_div0,
                                   arr_Y_div1),axis=0))
    dy = ymax-ymin
    ymin = ymin-dx*0.05
    ymax = ymax+dx*0.05
    ranges = [[xmin,xmax],[ymin,ymax]]

    gSave = []

    histo_div0 = _get2Dhisto(arr_X_div0, arr_Y_div0, [nbins_x,nbins_y], ranges, title)
    histo_div0.SetMarkerStyle(2)
    histo_div0.GetXaxis().SetTitle(namedata[0])
    histo_div0.GetYaxis().SetTitle(namedata[1])

    histo_div1 = _get2Dhisto(arr_X_div1, arr_Y_div1, [nbins_x,nbins_y], ranges, title)
    histo_div1.SetMarkerStyle(2)
    #histo_div1.GetXaxis().SetTitle(namedata[0])
    #histo_div1.GetYaxis().SetTitle(namedata[1])

    if 'color0' in param_dict:
        histo_div0.SetMarkerColor(getattr(ROOT, param_dict['color0']))
    else:
        histo_div0.SetMarkerColor(ROOT.kBlack)
    if 'color1' in param_dict:
        histo_div1.SetMarkerColor(getattr(ROOT, param_dict['color1']))
    else:
        histo_div1.SetMarkerColor(ROOT.kRed)
    if 'markersize' in param_dict:
        histo_div0.SetMarkerSize(getattr(ROOT, param_dict['markersize']))
        histo_div1.SetMarkerSize(getattr(ROOT, param_dict['markersize']))

    if 'root_plot_option' in param_dict:
        histo_div0.Draw(param_dict['root_plot_option'])
        histo_div1.Draw("%s%s" % (param_dict['root_plot_option'], "same"))
    else:
        histo_div0.Draw()
        histo_div1.Draw("same")
        #histo_div1.Draw()
    _save_histo(param_dict, title, "divergence_", can)
    return can

def aposteriori_distribution(param_dict):
    '''
    Plot a disposition of 2D histogram
    '''
   # Populate a grid of histograms with the parameters
    if 'n_bins_x' in param_dict:
        nbins_x = param_dict['n_bins_x']
    else:
        nbins_x = 100
    if 'n_bins_y' in param_dict:
        nbins_y = param_dict['n_bins_y']
    else:
        nbins_y = 100

    if 'data' in param_dict:
        namedata = param_dict['data']
        

    if 'root_plot_option' in param_dict:
        draw_opt_2d = param_dict['root_plot_option']
    else:
        draw_opt_2d = 'contz'

    name_grid, draw_opts_grid, colors_grid =_fill_variable_grid(namedata,
                                                                draw_opt_2d)

    myfile = ROOT.TFile(param_dict['input_file_name'],"READ")
    input_tree_name = param_dict['input_tree']
    hist_grid = _fill_hist_grid(input_tree_name, name_grid, myfile,
                                nbins_x, nbins_y)
    
    # Preparing the canvas
    logger.debug("Preparing Canvas")
    title, width, height = _preparingCanvas(param_dict)
    can = ROOT.TCanvas(title,title,width,height)
    can.Draw()
    if 'options' in param_dict:
        if "logy" in param_dict['options']:
            can.SetLogy()

    # Setting the titles
    logger.debug("Preparing Titles")
    xtitle, ytitle = _preparingTitles(param_dict)

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
    if 'output_path' in param_dict:
        path = param_dict['output_path']
    else:
        path = "./"
    if path.endswith('/')==False:
        path = path + '/'
    if title!=' ':
        figurefullpath = path+title+'_'
    else:
        figurefullpath = path
    for namedata in param_dict['data']:
        figurefullpath += namedata + '_'
    if figurefullpath.endswith('_'):
        figurefullpath = figurefullpath[:-1]
    if 'output_format' in param_dict:
        figurefullpath += '.' + param_dict['output_format']
    else:
        figurefullpath += '.pdf'
    can.Update()

    can.SaveAs(figurefullpath)
    return can

def correlation_factors(param_dict):
    """
    Create a plot with all variables along each axis,
    where the correlation factor between each pair
    of variables is represented by color.
    """
   # Populate a grid of histograms with the parameters
    if 'n_bins_x' in param_dict:
        nbins_x = param_dict['n_bins_x']
    else:
        nbins_x = 100
    if 'n_bins_y' in param_dict:
        nbins_y = param_dict['n_bins_y']
    else:
        nbins_y = 100

    if 'data' in param_dict:
        namedata = param_dict['data']
        

    if 'root_plot_option' in param_dict:
        draw_opt_2d = param_dict['root_plot_option']
    else:
        draw_opt_2d = 'contz'

    name_grid = _fill_variable_grid_corr_plot(namedata)

    myfile = ROOT.TFile(param_dict['input_file_name'],"READ")
    input_tree_name = param_dict['input_tree']
    hist_grid = _fill_hist_grid(input_tree_name, name_grid, myfile,
                                nbins_x, nbins_y)

    # Get correlation factors
    corr_grid = np.zeros((len(hist_grid), len(hist_grid[0])))
    for (idx, elt) in np.ndenumerate(corr_grid):
        corr_grid[idx] = hist_grid[idx[0]][idx[1]].GetCorrelationFactor()
    
    # Preparing the canvas
    logger.debug("Preparing Canvas")
    title, width, height = _preparingCanvas(param_dict)
    can = ROOT.TCanvas(title,title,width,height)
    # Set margins so all variables and the scale appear
    if 'left_margin' in param_dict:
        can.SetLeftMargin(param_dict['left_margin'])
    else:
        can.SetLeftMargin(0.175)
    if 'right_margin' in param_dict:
        can.SetRightMargin(param_dict['right_margin'])
    else:
        can.SetRightMargin(0.13)
    if 'bottom_margin' in param_dict:
        can.SetBottomMargin(param_dict['bottom_margin'])
    else:
        can.SetBottomMargin(0.175)
    if 'top_margin' in param_dict:
        can.SetTopMargin(param_dict['top_margin'])

    can.Draw()
    if 'options' in param_dict:
        if "logy" in param_dict['options']:
            can.SetLogy()


    # Setting the titles
    logger.debug("Preparing Titles")
    xtitle, ytitle = _preparingTitles(param_dict)

    gSave = []
 
    # Plot all histograms
    ROOT.gStyle.SetOptStat(0)
    rows, cols = corr_grid.shape

    hist = ROOT.TH2F(title, title,
                     cols, 0.5, cols+0.5,
                     rows, 0.5, rows+0.5)
    for (idx, corr_fac) in np.ndenumerate(corr_grid):
        hist.Fill(idx[0]+1, idx[1]+1, corr_fac)
    for (i,name) in enumerate(namedata):
        hist.GetXaxis().SetBinLabel(i+1, name)
        hist.GetYaxis().SetBinLabel(i+1, name)
    hist.GetXaxis().LabelsOption("v")
    hist.Draw("colz")

    # Save the plot
    if 'output_path' in param_dict:
        path = param_dict['output_path']
    else:
        path = "./"
    if path.endswith('/')==False:
        path = path + '/'
    if title!=' ':
        figurefullpath = path+title+'_'
    else:
        figurefullpath = path
    for namedata in param_dict['data']:
        figurefullpath += namedata + '_'
    if figurefullpath.endswith('_'):
        figurefullpath = figurefullpath[:-1]
    if 'output_format' in param_dict:
        figurefullpath += '.' + param_dict['output_format']
    else:
        figurefullpath += '.pdf'
    can.Update()

    can.SaveAs(figurefullpath)
    return can



def _set_style_options( rightMargin,  leftMargin,  topMargin,  botMargin):
    '''
    Change ROOT Style of the canvas
    '''
    style = ROOT.TStyle(ROOT.gStyle)
    style.SetOptStat("emr")
    style.SetLabelOffset(0.01,'xy')
    style.SetLabelSize(0.05,'xy')
    style.SetTitleOffset(0.8,'y')
    style.SetTitleSize(0.05,'x')
    style.SetTitleSize(0.05,'y')
    # style.SetLabelSize(0.05,'y')
    # style.SetLabelOffset(0,'y')
    # style.SetLabelSize(0.05,'x')
    style.SetTitleOffset(1.02,'x')

    style.SetPadRightMargin(rightMargin)
    style.SetPadTopMargin(topMargin)
    style.SetPadBottomMargin(botMargin)
    style.SetPadLeftMargin(leftMargin)
    style.cd()

def _preparingCanvas(param_dict):
    '''
    Extract the title, width and height of the TCanvas
    '''
    if 'output_width' in param_dict:
        width = param_dict['output_width']
    else:
        width = 600
    if 'output_height' in param_dict:
        height = param_dict['output_height']
    else:
        height = 400
    # Preparing the canvas
    if 'title' in param_dict and param_dict['title']!='':
        title = param_dict['title']
        _set_style_options(0.04,0.1,0.07,0.12)

    else:
        title = 'can_{}_{}'.format(height,width) #canvas_'+uuid.uuid4().get_hex()
        _set_style_options(0.04,0.1,0.03,0.12)

    return title, width, height

def _preparingTitles(param_dict):
    '''
    Extract the titles of the X and Y axis
    '''
    # Setting the titles
    if 'x_title' in param_dict:
        xtitle = param_dict['x_title']
    else:
        xtitle = ''
    if 'y_title' in param_dict:
        ytitle = param_dict['y_title']
    else:
        ytitle = ''
    return xtitle, ytitle


def _prepare_couples(list_data):
    '''
    Prepare a list of pairs of variables for the a posteriori distribution
    '''
    N = len(list_data)
    newlist = []
    for i in range(1,N): #y
        for j in range(0,i): #x
            newlist.append([list_data[j],list_data[i]])
    return newlist


def _get2Dhisto(list_dataX, list_dataY, nbins, ranges,histo_title):
    '''
    Internal function: return TH2F
    '''
    # logger.debug('Setting x axis')
    x_range = ranges[0]
    if isinstance(x_range,list):
        if isinstance(x_range[0],(float,int)) and isinstance(x_range[1],(float,int)):
            if  x_range[0] < x_range[1]:
                xmin = x_range[0]
                xmax = x_range[1]
            else:
                xmin,xmax = _autoRangeList(list_dataX)
        elif isinstance(x_range[0],(float,int)):
            xtemp,xmax = _autoRangeList(list_dataX)
            xmin = x_range[0]
        elif isinstance(x_range[1],(float,int)):
            xmin,xtemp = _autoRangeList(list_dataX)
            xmax = x_range[1]
        else:
            xmin,xmax = _autoRangeList(list_dataX)
    else:
        xmin,xmax = _autoRangeList(list_dataX)

    # logger.debug('Setting y axis')
    y_range = ranges[1]
    if isinstance(y_range,list):
        if isinstance(y_range[0],(float,int)) and isinstance(y_range[1],(float,int)):
            if  y_range[0] < y_range[1]:
                ymin = y_range[0]
                ymax = y_range[1]
            else:
                ymin,ymax = _autoRangeList(list_dataY)
        elif isinstance(y_range[0],(float,int)):
            ytemp,ymax = _autoRangeList(list_dataY)
            ymin = y_range[0]
        elif isinstance(y_range[1],(float,int)):
            ymin,ytemp = _autoRangeList(list_dataY)
            ymax = y_range[1]
        else:
            ymin,ymax = _autoRangeList(list_dataY)
    else:
        ymin,ymax = _autoRangeList(list_dataY)
    temphisto = ROOT.TH2F(histo_title,histo_title,nbins[0],xmin,xmax,nbins[1],ymin,ymax)
    if len(list_dataX)!=len(list_dataX):
        logger.critical("list of data does not have the same size. x: {}; y: {}".format(len(list_dataX),len(list_dataY)))
        return 0
    for i in range(0,len(list_dataX)):
        temphisto.Fill(list_dataX[i],list_dataY[i])
    return temphisto

def _autoRangeList(list):
    # logger.debug('Using autoRange')

    xmin = min(list)
    xmax = max(list)
    dx = xmax - xmin
    xmin = xmin - dx*0.05
    xmax = xmax + dx*0.05
    return xmin, xmax

def _autoRangeContent(hist):
    # logger.debug('Using autoRange')
    list = []
    for i in range(0,hist.GetNbinsX()):
        list.append(hist.GetBinContent(i))
    xmin = min(list)*0.9
    xmax = max(list)*1.1  # need to be done
    return xmin, xmax

def _fill_variable_grid(variable_names, draw_opt_2d):
    """ 
    pre: variable_name: variables to plot
         draw_opt_2D: Draw option to be used for 2D plots
    post: Returns a 2-tuple, where the first element is a grid of
          lists of variable names and the sedon is a grid of
          options that should be used to plot each list. 
          The grid of variable names will contain list length 1
          with a single variable when a 1D histogram should be
          plotted, and a list length 2 for 2D histograms.
          Positions that should not have a plot contain None
    """
    rows, cols = len(variable_names), len(variable_names)
    name_grid = [[None]*cols for i in range(rows)]
    draw_opts_grid = [[None]*cols for i in range(rows)]
    colors_grid = [[None]*cols for i in range(rows)]

    colors_arr = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen,
                  ROOT.kYellow, ROOT.kMagenta, ROOT.kCyan,
                  ROOT.kOrange, ROOT.kViolet, ROOT.kTeal,
                  ROOT.kSpring, ROOT.kPink, ROOT.kAzure]
    for i in range(0,len(variable_names)):
        for j in range(0,len(variable_names)):
            if(i==0 and j<cols-1):
                # First Row
                name_grid[i][j] = [variable_names[j]]
                draw_opts_grid[i][j] = "bar"
                colors_grid[i][j] = colors_arr[j%len(colors_arr)]
            elif(j==cols-1 and i>0):
                # Last Column
                name_grid[i][j] = [variable_names[(i-2)%cols]]
                draw_opts_grid[i][j] = "hbar"
                colors_grid[i][j] = colors_arr[((i-2)%cols)%len(colors_arr)]
            elif(i>0 and i+(cols-j)<=cols+1):
                name_grid[i][j] = [variable_names[(i-2)%cols], variable_names[j]]
                draw_opts_grid[i][j] = draw_opt_2d
    return (name_grid, draw_opts_grid, colors_grid)

def _fill_variable_grid_corr_plot(variable_names):
    """ 
    pre: variable_name: variables to plot
    post: returns a grid of length 2 lists. The list in
          position [i,j] contains the ith variable name
          then the jth variable name
    """
    rows, cols = len(variable_names), len(variable_names)
    name_grid = [[None]*cols for i in range(rows)]
    for i in range(rows):
        for j in range(cols):
            name_grid[i][j] = [variable_names[i],
                               variable_names[j]]
    return name_grid

def _fill_hist_grid(input_tree, name_grid, myfile,
                    nbins_x, nbins_y):
    rows, cols = len(name_grid), len(name_grid[0])
    hist_grid = [[None]*cols for i in range(rows)]
    tree = myfile.Get(input_tree)
    n = tree.GetEntries()
    for r,row in enumerate(name_grid):
        for c,names in enumerate(row):
            if(not names is None and len(names)==2):
                list_dataX = []
                list_dataY = []
                for i in range(0,n):
                    tree.GetEntry(i)
                    list_dataY.append(getattr(tree, names[0]))
                    list_dataX.append(getattr(tree, names[1]))
                histo = _get2Dhisto(list_dataX, list_dataY, [nbins_x,nbins_y],
                                    [0,0], '{}_{}'.format(names[0],names[1]))
                histo.SetTitle("")
                histo.GetYaxis().SetTitle(names[0])
                histo.GetXaxis().SetTitle(names[1])
                hist_grid[r][c] = histo
            elif(not names is None and len(names)==1):
                list_data = []
                for i in range(0,n):
                    tree.GetEntry(i)
                    list_data.append(getattr(tree, names[0]))
                x_range = _autoRangeList(list_data)
                histo = ROOT.TH1F("%s_%i_%i"%(names[0],r,c), names[0],
                                  nbins_x, x_range[0], x_range[1])
                for i in range(len(list_data)):
                    histo.Fill(list_data[i])
                histo.SetTitle("")
                histo.GetXaxis().SetTitle(names[0])
                hist_grid[r][c] = histo
            else:
                hist_grid[r][c] = None
    return hist_grid
