import ROOT as ROOT# import ROOT, TStyle, TCanvas, TH1F, TGraph, TLatex, TLegend, TFile, TTree, TGaxis, TRandom3, TNtuple, TTree
import cmath as math
from array import array
import re

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

def get_min_max_KE(file_path):
    fo = open(file_path, "rw+")
    line = fo.readline()

    minKE = -1.
    maxKE = -1.
    print "Name of the file: ", fo.name
    while line:
        # print line
        if "minKE <- " in line:
            x=re.findall(r"[-+]?\d*\.\d+|\d+",line )
            # print x[0]
            minKE = float(x[0])
            print minKE
            # except ValueError, e:
        if "maxKE <- " in line:
            x=re.findall(r"[-+]?\d*\.\d+|\d+",line )
            # print x[0]
            maxKE = float(x[0])
            print maxKE
            # except ValueError, e:
    # fo.close()
        line = fo.readline()

    if minKE<0:
        print 'Error: could not find minKE!'
    if maxKE<0:
        print 'Error: could not find maxKE!'
    return minKE,maxKE

def readTTree(tree_path):
    myfile = ROOT.TFile(tree_path,"READ")
    tree = myfile.Get("generated")
    n = tree.GetEntries()

#    time_data = []
    KE_data = []
    spectrum_data = []
#    KE_recon = []
    for i in range(0,n):
        tree.GetEntry(i)
#   	time_data.append(tree.time_data)
    	KE_data.append(tree.KE_data)
        spectrum_data.append(tree.spectrum_data)
#        KE_recon.append(tree.KE_recon)

#    return KE_data, spectrum_data


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
file_path = "MassHierarchy/results/MHtest_generator.root"
print file_path

KE_data, spectrum_data = readTTree(file_path)

can = ROOT.TCanvas("can","can",200,10,600,400)

minKE, maxKE = get_min_max_KE("MassHierarchy/data/MH_generate.data")

# can.SetLogy();

nBinHisto = 100
dKE = (maxKE - minKE)/nBinHisto

# spectrum vs freq
h = ROOT.TH1F("h","",nBinHisto,min(KE_data),max(KE_data))#KE_min and KE_max
hw = ROOT.TH1F("hw","",nBinHisto,min(KE_data),max(KE_data))#KE_min and KE_max
havg = ROOT.TH1F("havg","",nBinHisto,min(KE_data),max(KE_data))#KE_min and KE_max

hFakeData = ROOT.TH1F("fake_data","",nBinHisto,min(KE_data),max(KE_data))
hresidu = ROOT.TH1F("residu","",50,-3,3)

ran = ROOT.TRandom3()
list_fakespectrum_data = []
list_KE_data = []
list_spectrum_data = []
for i in range(0,len(spectrum_data)):
    # if (isOK[i]==1):
        h.Fill(KE_data[i],spectrum_data[i]*dKE)
        hw.Fill(KE_data[i],1)
for i in range(0,h.GetNbinsX()):
    list_KE_data.append(h.GetBinCenter(i))
    list_spectrum_data.append(h.GetBinContent(i)/max(1,hw.GetBinContent(i)))
    havg.Fill(h.GetBinCenter(i),list_spectrum_data[i])
    #Poisson distribution
    list_fakespectrum_data.append(ran.Poisson(list_spectrum_data[i]))
    hFakeData.Fill(h.GetBinCenter(i),list_fakespectrum_data[i])
    print list_KE_data[i], list_fakespectrum_data[i] , list_spectrum_data[i]
    # Residu calculation
    if list_spectrum_data[i]!=0:
        hresidu.Fill((list_fakespectrum_data[i]-list_spectrum_data[i])/pow(list_spectrum_data[i],0.5))


havg.Draw()
hFakeData.Draw("same")
havg.GetXaxis().SetTitle("Measured Kinetic Energy [eV]")
havg.SetLineColor(1)
print 'Total number of events: ', havg.Integral()
can.SaveAs("MassHierarchy/plotting_scripts/" + "spectrum_vs_KE_data_average.pdf")
can.SetLogy()
can.Update()

# spectrum  vs KE
#cane = ROOT.TCanvas("cane","cane",200,10,600,400)
#he = ROOT.TH1F("h","",nBinHisto,min(KE_recon),max(KE_recon))#KE_min and KE_max
#hew = ROOT.TH1F("hw","",nBinHisto,min(KE_recon),max(KE_recon))#KE_min and KE_max
#heavg = ROOT.TH1F("hw","",nBinHisto,min(KE_recon),max(KE_recon))#KE_min and KE_max
#list_KE = []
#list_spectrum_data = []
#for i in range(0,len(spectrum_data)):
#    he.Fill(KE_recon[i],spectrum_data[i]*dKE)
#    hew.Fill(KE_recon[i],1)
#for i in range(0,h.GetNbinsX()):
#    list_KE.append(he.GetBinCenter(i))
#    list_spectrum_data.append(h.GetBinContent(i)/max(1,hew.GetBinContent(i)))
#    heavg.Fill(he.GetBinCenter(i),he.GetBinContent(i)/max(1,hew.GetBinContent(i)))
#heavg.Draw()
#heavg.GetXaxis().SetTitle("Kinetic energy [eV]")
#print 'Number of total event for a year : ', havg.Integral()
#cane.SaveAs("tritium_model/ploting_scripts/" + "spectrum_vs_KE_recon_average.pdf")
#cane.SetLogy()
#cane.Update()
#cane.SaveAs("tritium_model/ploting_scripts/" + "spectrum_vs_KE_recon_average_logy.pdf")

# Time distribution
#cant = ROOT.TCanvas("cant","cant",200,10,600,400)
#htime = ROOT.TH1F("htime","",nBinHisto,0.,int(100000*max(time_data)+1)/100000)#time_min and time_max
#htimew = ROOT.TH1F("htimew","",nBinHisto,0.,int(100000*max(time_data)+1)/100000)#time_min and time_max
#htimeavg = ROOT.TH1F("htimeavg","",nBinHisto,0.,int(100000*max(time_data)+1)/100000)#time_min and time_max
#list_time = []
#list_Time_events = []
#for i in range(0,len(time_data)):
#    htime.Fill(time_data[i],1)
#for i in range(0,htime.GetNbinsX()):
#    list_time.append(htime.GetBinCenter(i))
#    list_Time_events.append(htime.GetBinContent(i))
#print 'Number of total event for a year : ', htime.Integral()
#htime.Draw();
#htime.GetXaxis().SetTitle("Track duration [s]")
#cant.SaveAs("tritium_model/ploting_scripts/" + "n_time_vs_time_data_average.pdf")

# Plot the poisson distribution of the spectrum
canfakedata = ROOT.TCanvas("canfd","canfd",200,10,600,400)
canfakedata.SetLogy()
hFakeData.Draw()
havg.Draw("same")
hFakeData.GetXaxis().SetTitle("Measured Kinetic Energy [eV]")
havg.SetLineColor(1)
canfakedata.Update()
canfakedata.SaveAs("MassHierarchy/plotting_scripts/" + "spectrum_vs_KE_data_average_logy.pdf")

# Plot residu
canres = ROOT.TCanvas("canR","canR",200,10,600,400)
hresidu.Draw()
hresidu.GetXaxis().SetTitle("Residus")
canres.Update()
canres.SaveAs("MassHierarchy/plotting_scripts/" + "Poisson_residus.pdf")

# Saving the additional data (aka the number of bin for each tree)
f = open('MassHierarchy/results/spectrum_additionalData.out','w')
value =(str(h.GetNbinsX()))
s=str(value)
f.write('nBinSpectrum <- ' + s + '\n')
#value =(str(htime.GetNbinsX()))
#s=str(value)
#f.write('nBinTime <- ' + s + '\n')
f.close()



# Creating the root file
tree_path = "MassHierarchy/results/generator_reduced.root"
myfile = ROOT.TFile(tree_path,"RECREATE")

# tree spectrum
tmp_KE_data = array('f',[ 0 ])
tmp_number_events = array('i',[ 0 ])

tree_spectrum = ROOT.TTree('spectrum', 'spectrum')
tree_spectrum.Branch('KE_data', tmp_KE_data, 'KE_data/F')
tree_spectrum.Branch('n_spectrum_data', tmp_number_events, 'n_spectrum_data/I')
for i in range(0,len(list_KE_data)):
    tmp_KE_data[0] = list_KE_data[i]
    tmp_number_events[0] = int(list_fakespectrum_data[i] )
    tree_spectrum.Fill()
tree_spectrum.Write()

# tree time
#tmp_time_data = array('f',[ 0. ])
#tmp_Time_events = array('i',[ 0 ])

#tree_time = ROOT.TTree('time', 'time')
#tree_time.Branch('time_data', tmp_time_data, 'time_data/F')
#tree_time.Branch('n_time_data', tmp_Time_events, 'n_time_data/I')
#for i in range(0,len(list_time)):
#    tmp_time_data[0] = list_time[i]
#    tmp_Time_events[0] = int(list_Time_events[i] )
#    tree_time.Fill()
#tree_time.Write()

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
Contact GitHub API Training Shop Blog About
© 2016 GitHub, Inc. Terms Privacy Security Status Help
