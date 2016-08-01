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

def histo(param_dict):

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

    can = ROOT.TCanvas(title,title,width,height)

    # Setting the titles
    if 'x_title' in param_dict:
        xtitle = param_dict['x_title']
    else:
        xtitle = ''
    if 'y_title' in param_dict:
        ytitle = param_dict['y_title']
    else:
        ytitle = ''



    # if option[2][0] < option[2][1]:
    #     xmin = option[2][0]
    #     xmax = option[2][1]
    # else:
    #     print 'Error: Invalid range of histogram -> Setting automatic range!'
    #     xmin, xmax = autoRange(list)
    #     print ' Range is: %d, %d' % (xmin, xmax)
    # can =  ROOT.TCanvas(title,title,width,height)

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
                if isinstance(param_dict['x_range'],list):

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
                list_histo[j].Draw()
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
    if 'output_format' in param_dict:
        figurefullpath += param_dict['output_format']
    else:
        figurefullpath += '.pdf'
    can.SaveAs(figurefullpath)
    raw_input('Press <ret> to end -> ')

    return can


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
# can = TCanvas("can", "can", 200, 10, 600, 400)
# #    Setting x axis title
# if isinstance(title[0], basestring) == False:
#     print 'Error: x axis title is not a string: ' + title[0]
#     xtitle = "x"
# else:
#     xtitle = title[0]
# #    Setting y axis title
# if isinstance(title[1], basestring) == False:
#     print 'Error: y axis title is not a string: ' + title[1]
#     ytitle = " "
# else:
#     ytitle = title[1]
#
# if isinstance(title[2], basestring) == False:
#     print 'Error: pdfname is not a string: ' + title[2]
#     pdfname = "default"
# else:
#     pdfname = title[2]
#
# #    Checking if option format is OK
# if len(option) != 3:
#     print 'Error: Number of options != 3: (%d)' % len(option)
#     return
# else :
#     if option[2][0] < option[2][1]:
#         xmin = option[2][0]
#         xmax = option[2][1]
#     else:
#         print 'Error: Invalid range of histogram -> Setting automatic range!'
#         xmin, xmax = autoRange(list)
#         print ' Range is: %d, %d' % (xmin, xmax)
#
# if option[1] >= 2:
#     nbins = option[1]
#     print nbins
# else:
#     print 'Error: invalid number of bins -> Setting nbin = 100'
#     nbins = 100
#
# if isinstance(option[0], basestring) == False:
#         print 'Error: first argument of option is not a string' + option[0]
#         return
#
#
#
#
# if "logx" in option[0]:
#     if xmin > 0:
#         can.SetLogx()
#
#         h1 = fillLogxHisto(list, xmin, xmax, nbins)
#     else:
#         print 'Error: xmin negative or null -> Cannot have logx axis!'
#         return
# else:
#     h1 = TH1F("h1", "", nbins, xmin, xmax)
#     for i in range(0, len(list)):
#         h1.Fill(list[i])
#
# if "logy" in option[0]:
#     can.SetLogy()
#
# can.cd()
# h1.GetXaxis().SetTitle(xtitle)
# h1.GetYaxis().SetTitle(ytitle)
# h1.Draw()
# can.SaveAs("plots/" + pdfname + ".pdf")
# return can
