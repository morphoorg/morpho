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
To do:
    - Clean up
    - Add log scales
"""

import logging
logger = logging.getLogger(__name__)

import ROOT as ROOT
import cmath as math
from array import array
import re
import uuid

def set_style_options( rightMargin,  leftMargin,  topMargin,  botMargin):
    style = ROOT.TStyle(ROOT.gStyle)
    style.SetOptStat("emr")
    style.SetLabelOffset(0.01,'xy')
    style.SetLabelSize(0.05,'xy')
    style.SetTitleOffset(1.2,'y')
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

def preparingCanvas(param_dict):
    # Preparing the canvas
    if 'title' in param_dict and param_dict['title']!='':
        title = param_dict['title']
        set_style_options(0.04,0.1,0.07,0.12)

    else:
        title = ' ' #canvas_'+uuid.uuid4().get_hex()
        set_style_options(0.04,0.1,0.03,0.12)

    if 'output_width' in param_dict:
        width = param_dict['output_width']
    else:
        width = 600
    if 'output_height' in param_dict:
        height = param_dict['output_height']
    else:
        height = 400
    return title, width, height

def preparingTitles(param_dict):
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


def histo(param_dict):
    '''
    Create a histogram using a list of X
    '''

    # Preparing the canvas
    logger.debug("Preparing Canvas")
    title, width, height = preparingCanvas(param_dict)
    can = ROOT.TCanvas(title,title,width,height)
    if 'options' in param_dict.keys():
        if any("logy" in s for s in param_dict['options']):
            logger.debug("Setting Log Y")
            can.SetLogy()
    # Setting the titles
    logger.debug("Preparing Titles")
    xtitle, ytitle = preparingTitles(param_dict)

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
                            xmin,xmax = autoRangeList(list_data)
                    elif isinstance(param_dict['x_range'][0],float):
                        xtemp,xmax = autoRangeList(list_data)
                        xmin = param_dict['x_range'][0]
                    elif isinstance(param_dict['x_range'][1],float):
                        xmin,xtemp = autoRangeList(list_data)
                        xmax = param_dict['x_range'][1]
                    else:
                        xmin,xmax = autoRangeList(list_data)
                else:
                    xmin,xmax = autoRangeList(list_data)
            else:
                xmin,xmax = autoRangeList(list_data)
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
                        ytemp,ymax = autoRangeContent(list_histo[j])
                        ymin = param_dict['y_range'][0]
                        list_histo[j].GetYaxis().SetRangeUser(ymin,ymax)
                    elif isinstance(param_dict['y_range'][1],float):
                        ymin,ytemp = autoRangeContent(list_histo[j])
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
    title, width, height = preparingCanvas(param_dict)
    can = ROOT.TCanvas(title,title,width,height)
    if "logy" in param_dict.options:
        can.SetLogy()

    # Setting the titles
    logger.debug("Preparing Titles")
    xtitle, ytitle = preparingTitles(param_dict)

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
            logger.debug('Setting x axis')
            if 'x_range' in param_dict:
                if isinstance(param_dict['x_range'],list):

                    if (isinstance(param_dict['x_range'][0],float) or isinstance(param_dict['x_range'][0],int)) and (isinstance(param_dict['x_range'][1],float) or isinstance(param_dict['x_range'][1],int)):
                        if  param_dict['x_range'][0] < param_dict['x_range'][1]:
                            xmin = param_dict['x_range'][0]
                            xmax = param_dict['x_range'][1]
                        else:
                            xmin,xmax = autoRangeList(list_dataX)
                    elif isinstance(param_dict['x_range'][0],float):
                        xtemp,xmax = autoRangeList(list_dataX)
                        xmin = param_dict['x_range'][0]
                    elif isinstance(param_dict['x_range'][1],float):
                        xmin,xtemp = autoRangeList(list_dataX)
                        xmax = param_dict['x_range'][1]
                    else:
                        xmin,xmax = autoRangeList(list_dataX)
                else:
                    xmin,xmax = autoRangeList(list_dataX)
            else:
                xmin,xmax = autoRangeList(list_dataX)
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
                        ytemp,ymax = autoRangeContent(list_histo[j])
                        ymin = param_dict['y_range'][0]
                        list_histo[j].GetYaxis().SetRangeUser(ymin,ymax)
                    elif isinstance(param_dict['y_range'][1],float):
                        ymin,ytemp = autoRangeContent(list_histo[j])
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
    # raw_input('Press <ret> to end -> ')

    return can

def histo2D(param_dict):
    '''
    Plot 2D histogram
    '''
    # Preparing the canvas
    logger.debug("Preparing Canvas")
    title, width, height = preparingCanvas(param_dict)
    can = ROOT.TCanvas(title,title,width,height)
    if "logy" in param_dict.options:
        can.SetLogy()

    # Setting the titles
    logger.debug("Preparing Titles")
    xtitle, ytitle = preparingTitles(param_dict)

    gSave = []
    j = 0

    if isinstance(param_dict['data'],list):
        if 'n_bins_x' in param_dict:
            nbins_x = param_dict['n_bins_x']
        else:
            nbins_x = 100
        if 'n_bins_y' in param_dict:
            nbins_y = param_dict['n_bins_y']
        else:
            nbins_y = 100
        list_histo = []

        myfile = ROOT.TFile(param_dict['input_file_name'],"READ")

def _get2Dhisto(list_dataX, list_dataY, nbins, ranges,histo_title):
    '''
    Internal function to create 2D histograms
    '''
    logger.debug('Setting x axis')
    x_range = ranges[0]
    if isinstance(x_range,list):
        if isinstance(x_range[0],(float,int)) and isinstance(x_range[1],(float,int)):
            if  x_range[0] < x_range[1]:
                xmin = x_range[0]
                xmax = x_range[1]
            else:
                xmin,xmax = autoRangeList(list_dataX)
        elif isinstance(x_range[0],(float,int)):
            xtemp,xmax = autoRangeList(list_dataX)
            xmin = x_range[0]
        elif isinstance(x_range[1],(float,int)):
            xmin,xtemp = autoRangeList(list_dataX)
            xmax = x_range[1]
        else:
            xmin,xmax = autoRangeList(list_dataX)
    else:
        xmin,xmax = autoRangeList(list_dataX)

    logger.debug('Setting y axis')
    y_range = ranges[0]
    if isinstance(y_range,list):
        if isinstance(y_range[0],(float,int)) and isinstance(y_range[1],(float,int)):
            if  y_range[0] < y_range[1]:
                ymin = y_range[0]
                ymax = y_range[1]
            else:
                ymin,ymax = autoRangeList(list_dataX)
        elif isinstance(y_range[0],(float,int)):
            ytemp,ymax = autoRangeList(list_dataX)
            ymin = y_range[0]
        elif isinstance(y_range[1],(float,int)):
            ymin,ytemp = autoRangeList(list_dataX)
            ymax = y_range[1]
        else:
            ymin,ymax = autoRangeList(list_dataX)
    else:
        ymin,ymax = autoRangeList(list_dataX)

    temphisto = ROOT.TH1F(histo_title,histo_title,nbins,xmin,xmax)

def autoRangeList(list):
    logger.debug('Using autoRange')
    xmin = min(list)
    xmax = max(list)  # need to be done
    return xmin, xmax
def autoRangeContent(hist):
    logger.debug('Using autoRange')
    list = []
    for i in range(0,hist.GetNbinsX()):
        list.append(hist.GetBinContent(i))
    xmin = min(list)*0.9
    xmax = max(list)*1.1  # need to be done
    return xmin, xmax
