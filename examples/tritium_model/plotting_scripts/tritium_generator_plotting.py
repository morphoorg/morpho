from ROOT import ROOT, TStyle, TCanvas, TH1F, TGraph, TLatex, TLegend, TFile, TTree, TGaxis, TRandom3
import cmath as math
from display import displayHisto, displayGraph, plot_average

def set_style_options( rightMargin,  leftMargin,  topMargin,  botMargin):
    style = TStyle(ROOT.gStyle)
    style.SetOptStat(1)
    style.SetLabelOffset(0,'xy')
    style.SetLabelSize(0.05,'xy')
    style.SetTitleOffset(1.2,'y')
    style.SetTitleSize(0.05,'y')
    style.SetLabelSize(0.05,'y')
    style.SetLabelOffset(0,'y')
    style.SetTitleSize(0.05,'x')
    style.SetLabelSize(0.05,'x')
    style.SetTitleOffset(1.02,'x')

    style.SetPadRightMargin(rightMargin)
    style.SetPadTopMargin(topMargin)
    style.SetPadBottomMargin(botMargin)
    style.SetPadLeftMargin(leftMargin)
    style.cd()

def readTTree(tree_path):
    myfile = TFile(tree_path,"READ")
    tree = myfile.Get("procTracks")
    n = tree.GetEntries()

    time_data = []
    freq_data = []
    rate_data = []
    KE_recon = []
    events = []
    Q = []
    for i in range(0,n):
        tree.GetEntry(i)
    	time_data.append(tree.time_data)
    	freq_data.append(tree.freq_data)
        rate_data.append(tree.rate_data)
        KE_recon.append(tree.KE_recon)
        events.append(tree.events)
        Q.append(tree.Q)

    return time_data, freq_data, rate_data, KE_recon, events,Q


print "I am doing nice plots"
rightMargin = 0.08
leftMargin = 0.11
topMargin = 0.08
botMargin = 0.11

set_style_options(rightMargin, leftMargin, topMargin, botMargin)

time_data, freq_data, rate_data, KE_recon, events, Q = readTTree("tritium_model/results/tritium_generator.root")

can_time = displayHisto(time_data,["time_data","","time_data"],["",100,[0,-1]])
can_freq = displayHisto(freq_data,["freq_data","","freq_data"],["",100,[0,-1]])
can_rate = displayHisto(rate_data,["rate_data","","rate_data"],["",100,[0,-1]])
can_KE = displayHisto(KE_recon,["KE_recon","","KE_recon"],["",100,[0,-1]])
can_events = displayHisto(events,["events","","events"],["",100,[0,-1]])
can_Q = displayHisto(Q,["Q","","Q"],["",100,[0,-1]])

# plot_average(KE_recon,events)

topMargin = 0.06
set_style_options(rightMargin, leftMargin, topMargin, botMargin)
can_rate_freq = displayGraph([freq_data,rate_data],["freq_data","rate_data","rate_data_vs_freq_data"],["AP",[0,-1,0.,"inf"]])
can_rate_freq = displayGraph([freq_data,rate_data],["freq_data","rate_data","rate_data_vs_freq_data_logy"],["logy_AP",[0,-1,0.,"inf"]])
can_KE_freq = displayGraph([freq_data,KE_recon],["freq_data","KE_recon","KE_recon_vs_freq_data"],["AP",[0,-1,"inf","inf"]])
can_rate_KE = displayGraph([KE_recon,rate_data],["KE_recon","rate_data","rate_data_vs_KE_recon"],["AP",[0,-1,"inf","inf"]])
can_rate_KE = displayGraph([KE_recon,rate_data],["KE_recon","rate_data","rate_data_vs_KE_recon_logy"],["logy_AP",[0,-1,.5,"inf"]])
can_events_KE = displayGraph([KE_recon,events],["KE_recon","events","events_vs_KE_recon"],["AP",[0,-1,0.,"inf"]])
can_events_KE = displayGraph([KE_recon,events],["KE_recon","events","events_vs_KE_recon_logy"],["logy_AP",[0,-1,.5,"inf"]])
