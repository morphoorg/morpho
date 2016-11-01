import ROOT as ROOT# import ROOT, TStyle, TCanvas, TH1F, TGraph, TLatex, TLegend, TFile, TTree, TGaxis, TRandom3, TNtuple, TTree
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

def preparingTitles(paramdict):
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

    # Preparing the canvas
    title, width, height = preparingCanvas(param_dict)
    can = ROOT.TCanvas(title,title,width,height)

    # Setting the titles
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
            print(namedata)
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
                # print(list_data[i])
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
                print(xtitle)
            else:
                list_histo[j].Draw("SAME")
            # gSave.append(list_histo[j])
            can.Update()

            print(j)

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
    if 'output_format' in param_dict:
        figurefullpath += param_dict['output_format']
    else:
        figurefullpath += '.pdf'
    can.SaveAs(figurefullpath)
    raw_input('Press <ret> to end -> ')

    return can

def histo2D(param_dict):
    # Preparing the canvas
    title, width, height = preparingCanvas(param_dict)
    can = ROOT.TCanvas(title,title,width,height)

    # Setting the titles
    xtitle, ytitle = preparingTitles(paramdict)


def autoRangeList(list):
    print('Using autoRange')
    xmin = min(list)
    xmax = max(list)  # need to be done
    print(xmin,xmax)
    return xmin, xmax
def autoRangeContent(hist):
    print('Using autoRange')
    list = []
    for i in range(0,hist.GetNbinsX()):
        list.append(hist.GetBinContent(i))
    xmin = min(list)*0.9
    xmax = max(list)*1.1  # need to be done
    print(xmin,xmax)
    return xmin, xmax
