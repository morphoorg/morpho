#======================================================
# timeseries.py
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
"""

import ROOT as ROOT
import cmath as math
from array import array
import re
import uuid

import logging
logger = logging.getLogger('timeseries')
logger.setLevel(logging.DEBUG)
base_format = '%(asctime)s[%(levelname)-8s] %(name)s(%(lineno)d) -> %(message)s'
logging.basicConfig(format=base_format, datefmt='%m/%d/%Y %H:%M:%S')

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

def timeseries(param_dict):
    logger.info('Plotting timeseries')
    # Preparing the canvas
    if 'title' in param_dict and param_dict['title']!='':
        title = param_dict['title']
        set_style_options(0.04,0.15,0.07,0.12)

    else:
        title = ' ' #canvas_'+uuid.uuid4().get_hex()
        set_style_options(0.04,0.15,0.07,0.12)

    if 'output_width' in param_dict:
        width = param_dict['output_width']
    else:
        width = 600
    if 'output_height' in param_dict:
        height = param_dict['output_height']
    else:
        height = 400
    can = ROOT.TCanvas(title,title,width,height)
    ntimeseries = len(param_dict['data'])
    nCanx = int(ROOT.TMath.Sqrt(ntimeseries) )+1
    nCany = int(ROOT.TMath.Sqrt(ntimeseries) )+1
    can.Divide(nCanx,nCany)
    # Setting the titles
    if 'x_title' in param_dict:
        xtitle = param_dict['x_title']
    else:
        xtitle = ['']*ntimeseries
    if 'y_title' in param_dict:
        ytitle = param_dict['y_title']
    else:
        ytitle = ['']*ntimeseries

    if 'draw_opt' in param_dict:
        drawing_options = param_dict['draw_opt']
    else:
        drawing_options = "APL"

    lgraph = {}

    myfile = ROOT.TFile(param_dict['input_file_name'],"READ")
    tree = myfile.Get(param_dict['input_tree'])
    n = tree.GetEntries()
    iCanvas = 0
    for dataname in param_dict['data']:
        list_datax = [0.]*n
        list_datay = [0.]*n
        for i in range(0,n):
            tree.GetEntry(i)
            list_datax[i] = float(i)
            list_datay[i] = getattr(tree,dataname)
        lgraph[dataname] = ROOT.TGraph(n,array('d',list_datax),array('d',list_datay))
        can.cd(iCanvas+1)
        lgraph[dataname].Draw(drawing_options)
        lgraph[dataname].GetXaxis().SetTitle(xtitle[iCanvas])
        lgraph[dataname].GetYaxis().SetTitle(ytitle[iCanvas])
        lgraph[dataname].SetTitle("")
        iCanvas +=1
    can.Update()

    # gSave.append(list_histo)

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
    raw_input('Press <ret> to end -> ')

    return can
