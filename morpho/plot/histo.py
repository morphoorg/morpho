import ROOT as ROOT# import ROOT, TStyle, TCanvas, TH1F, TGraph, TLatex, TLegend, TFile, TTree, TGaxis, TRandom3, TNtuple, TTree
import cmath as math
from array import array
import re
import uuid

def histo(param_dict):
    print("Creating histo!")

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

    can =  ROOT.TCanvas(title,title,width,height)


    return can
