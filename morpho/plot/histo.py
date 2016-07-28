import ROOT as ROOT# import ROOT, TStyle, TCanvas, TH1F, TGraph, TLatex, TLegend, TFile, TTree, TGaxis, TRandom3, TNtuple, TTree
import cmath as math
from array import array
import re
import uuid

def histo(param_dict):
    print("Creating histo!")

    # Preparing the canvas
    if 'title' in param_dict:
        title = param_dict['title']
    else:
        title = 'canvas_'+uuid.uuid4().get_hex()
    if 'output_width' in param_dict:
        width = param_dict['output_width']
    else:
        width = 600
    if 'output_height' in param_dict:
        height = param_dict['output_height']
    else:
        height = 400

    # Setting the titles
    if 'xtitle' in param_dict:
        xtitle = param_dict['xtitle']
    else:
        xtitle = 'x'
    if 'ytitle' in param_dict:
        ytitle = param_dict['ytitle']
    else:
        ytitle = ''

    # Setting the picture file name
    if 'output_path' in param_dict:
        path = param_dict['output_path']
    else:
        path = "./"
    if !path.endswith('/'):
        path = path + '/'
    if 'output_format' in param_dict:
        figurefullpath = path+title+param_dict['output_format']
    else:
        figurefullpath = path+title+'.pdf'

    can =  ROOT.TCanvas(title,title,width,height)

    if isinstance(param_dict['data'],list):
        for namedata in param_dict['data']:

    for

    return can
#
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
