import ROOT as ROOT# import ROOT, TStyle, TCanvas, TH1F, TGraph, TLatex, TLegend, TFile, TTree, TGaxis, TRandom3, TNtuple, TTree
import cmath as math
from array import array

def set_style_options( rightMargin,  leftMargin,  topMargin,  botMargin):
    style = ROOT.TStyle(ROOT.gStyle)
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
    myfile = ROOT.TFile(tree_path,"READ")
    tree = myfile.Get("procTracks")
    n = tree.GetEntries()

    time_data = []
    freq_data = []
    rate_data = []
    KE_recon = []
    events = []
    isOK = []
    for i in range(0,n):
        tree.GetEntry(i)
    	time_data.append(tree.time_data)
    	freq_data.append(tree.freq_data)
        rate_data.append(tree.rate_data)
        KE_recon.append(tree.KE_recon)
        events.append(tree.events)
        isOK.append(tree.isOK)

    return time_data, freq_data, rate_data, KE_recon, events, isOK


def writeTTree(tree_path,title,branches_names,branches):
    for i in range(0,len(title)):#number of tree to fill
        tree = ROOT.TNtuple(title[i],title[i],":".join(branches_names[i]))
        list_branches = []
        for k in range(len(branches[i])):

            branch = ROOT.TBranch()
            list_branches.append()
        for j in range(0,len(branches[i][0])): #number of events in this tree
            list = []
            for k in range(len(branches[i])):
                list.append(branches[i][k][j])
            tree.Fill(array.array("f",list))
        tree.Write()

    return 0

print "Reducing the generated data!"

time_data, freq_data, rate_data, KE_recon, events, isOK = readTTree("tritium_model/results/tritium_generator.root")

can = ROOT.TCanvas("can","can",200,10,600,400)

h = ROOT.TH1F("h","",100,int(min(freq_data)),int(max(freq_data)+1))#KE_min and KE_max
list_freq_data = []
list_events = []
for i in range(0,len(rate_data)):
    if (isOK[i]==1):
        h.Fill(freq_data[i],events[i])
for i in range(1,h.GetNbinsX()):
    list_freq_data.append(h.GetBinCenter(i))
    list_events.append(h.GetBinContent(i))
h.Draw()
can.SaveAs("tritium_model/plotting_scripts/" + "events_vs_freq_data_average.pdf")

cant = ROOT.TCanvas("cant","cant",200,10,600,400)

htime = ROOT.TH1F("htime","",100,0.,int(100000*max(time_data)+1)/100000)#time_min and time_max
list_time = []
list_Time_events = []
for i in range(0,len(time_data)):
    if (isOK[i]==1):
        htime.Fill(time_data[i])
for i in range(1,htime.GetNbinsX()):
    list_time.append(htime.GetBinCenter(i))
    list_Time_events.append(htime.GetBinContent(i))
    print htime.GetBinCenter(i),  htime.GetBinContent(i)
htime.Draw();
cant.SaveAs("tritium_model/plotting_scripts/" + "n_time_vs_time_data_average.pdf")

# Saving the additional data (aka the number of bin for each tree)
f = open('tritium_model/results/tritium_additionalData.txt','w')
value =(str(h.GetNbinsX()-1))
s=str(value)
f.write('nBinEvents <- ' + s + '\n')
value =(str(htime.GetNbinsX()-1))
s=str(value)
f.write('nBinTime <- ' + s + '\n')
f.close()

# Creating the root file
tree_path = "tritium_model/results/tritium_generator_reduced.root"
myfile = ROOT.TFile(tree_path,"RECREATE")

# tree spectrum
tmp_freq_data = array('f',[ 0 ])
tmp_events = array('i',[ 0 ])

tree_spectrum = ROOT.TTree('spectrum', 'spectrum')
tree_spectrum.Branch('freq_data', tmp_freq_data, 'freq_data/F')
tree_spectrum.Branch('n_events', tmp_events, 'n_events/I')
for i in range(0,len(list_freq_data)):
    tmp_freq_data[0] = list_freq_data[i]
    tmp_events[0] = int(list_events[i] )
    tree_spectrum.Fill()
tree_spectrum.Write()

# tree time
tmp_time_data = array('f',[ 0. ])
tmp_Time_events = array('i',[ 0 ])

tree_time = ROOT.TTree('time', 'time')
tree_time.Branch('time_data', tmp_time_data, 'time_data/F')
tree_time.Branch('n_time_data', tmp_Time_events, 'n_time_data/I')
for i in range(0,len(list_time)):
    tmp_time_data[0] = list_time[i]
    tmp_Time_events[0] = int(list_Time_events[i] )
    tree_time.Fill()
tree_time.Write()

# title = ["spectrum","time"]
# branches_names = [["freq_data","n_events"],["time_data","n_time_data"]]
# branches = [[list_freq_data,list_events],[list_time,list_Time_events]]
# writeTTree(path,title,branches_names,branches)
#
# from ROOT import TFile, TTree
# from array import array

# h = ROOT.TH1F( 'h1', 'test', 100, -10., 10. )
#
# f = ROOT.TFile( 'test.root', 'recreate' )
# t = ROOT.TTree( 't1', 'tree with histos' )
#
# maxn = 10
# n = array( 'i', [ 0 ] )
# d = array( 'f', maxn*[ 0. ] )
# t.Branch( 'mynum', n, 'mynum/I' )
# t.Branch( 'myval', d, 'myval[mynum]/F' )
#
# for i in range(25):
#    n[0] = min(i,maxn)
#    for j in range(n[0]):
#       d[j] = i*0.1+j
#    t.Fill()
#
# f.Write()
# f.Close()


raw_input('Press <ret> to end -> ')
