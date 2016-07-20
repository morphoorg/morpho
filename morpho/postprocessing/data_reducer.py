'''
This module contains a 'data_reducer' method which transforms a spread of spectrum points (with frequency as a x axis) generated with STAN into a true spectrum-like plot.
This module must be called in the json config file by adding a new dictionary called 'processing' inside the main dictionary:
Here is an example of such new dictionary:

  "postprocessing":
  {
    "which_pp":[
      {
        "method_name": "data_reducer", #name of the method
        "module_name": "data_reducer", #name of the python file which contains the method
        "input_file_name" : "./tritium_model/results/tritium_generator.root", #path to the root file which contains the raw data
        "input_file_format" : "root", #format of the input file
        "input_tree": "stan_MC", # name of the tree (in case of root file)
        "minKE":18500., #minimal energy used for generating the STAN data
        "maxKE":18600., #maximal energy used for generating the STAN data
        "nBinHisto":50, # number of bins wanted for the output spectrum
        "output_file_name" : "./tritium_model/results/tritium_generator_reduced_fake.root", #path to the root file where to save the spectrum data
        "output_file_format": "root", #format of the output file
        "output_freq_spectrum_tree": "spectrum", #name of the tree (in case of root file) which contains the frequency spectrum
        "output_time_spectrum_tree": "time", #name of the tree (in case of root file) which contains the time spectrum
        "additional_file_name" : "./tritium_model/results/tritium_additionalData.out", #name of the file which contains the number of bins for the output histograms
      }
     ]

  }
Below is a  to-do list:
- easy tasks:
    - extend the number of nBinHisto to allow the user to have different spectrum depending on the nature of the histo (time, frequency...)
- harder tasks:
    - make this data reducer very generic (to be able to choose between frequency, energ or time spectrum) or add the energy spectrum by default
    - implement the h5 reader and writter
    - integrate the "additional_file_name" content into the "output_file" (this will require --in the case of root-- to be able to read single values directly from a root file).
    A possibility is also to make a tree with n branches with only one element, these elements are then read in the analyzer as the number of bin/data to be analyzed
'''

import ROOT as ROOT# import ROOT, TStyle, TCanvas, TH1F, TGraph, TLatex, TLegend, TFile, TTree, TGaxis, TRandom3, TNtuple, TTree
import cmath as math
from array import array
import re

def data_reducer(param_dict):
    print("Reducing the generated data!")
    print("Input data is: {}".format(param_dict['input_file_name']))
    if (param_dict['input_file_format']=='root'):
        time_data, freq_data, spectrum_data, KE_recon = readTTree(param_dict['input_file_name'],param_dict['input_tree'])
    elif (param_dict['input_file_format']=='h5'):
        print('h5 file is not yet supported in the data_reducer')
    else:
        print('{} file is not a known format'.format(param_dict['input_file_format']))

    nBinHisto = param_dict['nBinHisto']
    dKE = (param_dict['maxKE'] - param_dict['minKE'])/nBinHisto

    # spectrum vs freq
    h = ROOT.TH1F("h","",nBinHisto,min(freq_data),max(freq_data))#KE_min and KE_max
    hw = ROOT.TH1F("hw","",nBinHisto,min(freq_data),max(freq_data))#KE_min and KE_max
    havg = ROOT.TH1F("havg","",nBinHisto,min(freq_data),max(freq_data))#KE_min and KE_max

    hFakeData = ROOT.TH1F("fake_data","",nBinHisto,min(freq_data),max(freq_data))

    ran = ROOT.TRandom3()
    list_fakespectrum_data = []
    list_freq_data = []
    list_spectrum_data = []
    for i in range(0,len(spectrum_data)):
        # if (isOK[i]==1):
            h.Fill(freq_data[i],spectrum_data[i]*dKE)
            hw.Fill(freq_data[i],1)
    for i in range(0,h.GetNbinsX()):
        list_freq_data.append(h.GetBinCenter(i))
        list_spectrum_data.append(h.GetBinContent(i)/max(1,hw.GetBinContent(i)))
        havg.Fill(h.GetBinCenter(i),list_spectrum_data[i])
        #Poisson distribution
        list_fakespectrum_data.append(ran.Poisson(list_spectrum_data[i]))
        hFakeData.Fill(h.GetBinCenter(i),list_fakespectrum_data[i])

    # This paragraph might be uncommented when doing debugging
    # can =  ROOT.TCanvas("can","can",200,10,600,400)
    # havg.Draw('hist')
    # hFakeData.Draw('samehist')
    # havg.GetXaxis().SetTitle("Measured frequency [Hz]")
    # havg.SetLineColor(1)
    # print 'Number of total event for a year : ', havg.Integral()
    # can.SaveAs("tritium_model/ploting_scripts/" + "spectrum_vs_freq_data_average.pdf")
    # can.SetLogy()
    # can.Update()
    # end of uncommentable paragraph

    # spectrum  vs KE
    he = ROOT.TH1F("he","",nBinHisto,min(KE_recon),max(KE_recon))#KE_min and KE_max
    hew = ROOT.TH1F("hew","",nBinHisto,min(KE_recon),max(KE_recon))#KE_min and KE_max
    heavg = ROOT.TH1F("heavg","",nBinHisto,min(KE_recon),max(KE_recon))#KE_min and KE_max
    list_KE = []
    list_spectrum_data = []
    for i in range(0,len(spectrum_data)):
        he.Fill(KE_recon[i],spectrum_data[i]*dKE)
        hew.Fill(KE_recon[i],1)
    for i in range(0,h.GetNbinsX()):
        list_KE.append(he.GetBinCenter(i))
        list_spectrum_data.append(h.GetBinContent(i)/max(1,hew.GetBinContent(i)))
        heavg.Fill(he.GetBinCenter(i),he.GetBinContent(i)/max(1,hew.GetBinContent(i)))

    # cane = ROOT.TCanvas("cane","cane",200,10,600,400)
    # heavg.Draw()
    # heavg.GetXaxis().SetTitle("Kinetic energy [eV]")
    # print 'Number of total event for a year : ', havg.Integral()
    # cane.SaveAs("tritium_model/ploting_scripts/" + "spectrum_vs_KE_recon_average.pdf")
    # cane.SetLogy()
    # cane.Update()
    # cane.SaveAs("tritium_model/ploting_scripts/" + "spectrum_vs_KE_recon_average_logy.pdf")

    # Time distribution
    htime = ROOT.TH1F("htime","",nBinHisto,0.,int(100000*max(time_data)+1)/100000)#time_min and time_max
    htimew = ROOT.TH1F("htimew","",nBinHisto,0.,int(100000*max(time_data)+1)/100000)#time_min and time_max
    htimeavg = ROOT.TH1F("htimeavg","",nBinHisto,0.,int(100000*max(time_data)+1)/100000)#time_min and time_max
    list_time = []
    list_Time_events = []
    for i in range(0,len(time_data)):
        htime.Fill(time_data[i],1)
    for i in range(0,htime.GetNbinsX()):
        list_time.append(htime.GetBinCenter(i))
        list_Time_events.append(htime.GetBinContent(i))

    # cant = ROOT.TCanvas("cant","cant",200,10,600,400)
    # htime.Draw();
    # htime.GetXaxis().SetTitle("Track duration [s]")
    # cant.SaveAs("tritium_model/ploting_scripts/" + "n_time_vs_time_data_average.pdf")

    # # Plot the poisson distribution of the spectrum
    # canfakedata = ROOT.TCanvas("canfd","canfd",200,10,600,400)
    # canfakedata.SetLogy()
    # hFakeData.Draw()
    # havg.Draw("same")
    # hFakeData.GetXaxis().SetTitle("Measured frequency [Hz]")
    # havg.SetLineColor(1)
    # canfakedata.Update()
    # canfakedata.SaveAs("tritium_model/ploting_scripts/" + "spectrum_vs_freq_data_average_logy.pdf")

    # Saving the additional data (aka the number of bin for each tree)
    f = open(param_dict['additional_file_name'],'w')
    value =(str(h.GetNbinsX()))
    s=str(value)
    f.write('nBinSpectrum <- ' + s + '\n')
    value =(str(htime.GetNbinsX()))
    s=str(value)
    f.write('nBinTime <- ' + s + '\n')
    f.close()

    # Creating the root file
    print("Output data is: {}".format(param_dict['output_file_name']))
    if param_dict['output_file_format']=='root':
        myfile = ROOT.TFile(param_dict['output_file_name'],"RECREATE")
    elif param_dict['output_file_format']=='h5':
        print('h5 file is not yet supported in the data_reducer')
    else:
        print('{} file is not a known format'.format(param_dict['output_file_format']))

    # tree spectrum
    tmp_freq_data = array('f',[ 0 ])
    tmp_number_events = array('i',[ 0 ])

    tree_spectrum = ROOT.TTree(param_dict['output_freq_spectrum_tree'], param_dict['output_freq_spectrum_tree'])
    tree_spectrum.Branch('freq_data', tmp_freq_data, 'freq_data/F')
    tree_spectrum.Branch('n_spectrum_data', tmp_number_events, 'n_spectrum_data/I')
    for i in range(0,len(list_freq_data)):
        tmp_freq_data[0] = list_freq_data[i]
        tmp_number_events[0] = int(list_fakespectrum_data[i] )
        tree_spectrum.Fill()
    tree_spectrum.Write()

    # tree time
    tmp_time_data = array('f',[ 0. ])
    tmp_Time_events = array('i',[ 0 ])

    tree_time = ROOT.TTree(param_dict['output_time_spectrum_tree'], param_dict['output_time_spectrum_tree'])
    tree_time.Branch('time_data', tmp_time_data, 'time_data/F')
    tree_time.Branch('n_time_data', tmp_Time_events, 'n_time_data/I')
    for i in range(0,len(list_time)):
        tmp_time_data[0] = list_time[i]
        tmp_Time_events[0] = int(list_Time_events[i] )
        tree_time.Fill()
    tree_time.Write()

    print('Prostprocessing complete!')

    # raw_input('Press <ret> to end -> ')

def readTTree(root_file_path,tree_name):
    myfile = ROOT.TFile(root_file_path,"READ")
    tree = myfile.Get(tree_name)
    n = tree.GetEntries()

    time_data = []
    freq_data = []
    spectrum_data = []
    KE_recon = []
    # isOK = []
    for i in range(0,n):
        tree.GetEntry(i)
    	time_data.append(tree.time_data)
    	freq_data.append(tree.freq_data)
        spectrum_data.append(tree.spectrum_data)
        KE_recon.append(tree.KE_recon)

    return time_data, freq_data, spectrum_data, KE_recon

# depreciated
# def get_min_max_KE(file_path):
#     fo = open(file_path, "rw+")
#     line = fo.readline()
#
#     minKE = -1.
#     maxKE = -1.
#     print "Name of the file: ", fo.name
#     while line:
#         # print line
#         if "minKE <- " in line:
#             x=re.findall(r"[-+]?\d*\.\d+|\d+",line )
#             # print x[0]
#             minKE = float(x[0])
#             print minKE
#             # except ValueError, e:
#         if "maxKE <- " in line:
#             x=re.findall(r"[-+]?\d*\.\d+|\d+",line )
#             # print x[0]
#             maxKE = float(x[0])
#             print maxKE
#             # except ValueError, e:
#     # fo.close()
#         line = fo.readline()
#
#     if minKE<0:
#         print 'Error: could not find minKE!'
#     if maxKE<0:
#         print 'Error: could not find maxKE!'
#     return minKE,maxKE



# ARCHIVE: Not used in the data reducer now but could be used somewhere else...
# def writeTTree(tree_path,title,branches_names,branches):
#     for i in range(0,len(title)):#number of tree to fill
#         tree = ROOT.TNtuple(title[i],title[i],":".join(branches_names[i]))
#         list_branches = []
#         for k in range(len(branches[i])):
#
#             branch = ROOT.TBranch()
#             list_branches.append()
#         for j in range(0,len(branches[i][0])): #number of events in this tree
#             list = []
#             for k in range(len(branches[i])):
#                 list.append(branches[i][k][j])
#             tree.Fill(array.array("f",list))
#         tree.Write()
#
#     return 0
# def set_style_options( rightMargin,  leftMargin,  topMargin,  botMargin):
#     style = ROOT.TStyle(ROOT.gStyle)
#     style.SetOptStat(1)
#     style.SetLabelOffset(0,'xy')
#     style.SetLabelSize(0.05,'xy')
#     style.SetTitleOffset(1.2,'y')
#     style.SetTitleSize(0.05,'y')
#     style.SetLabelSize(0.05,'y')
#     style.SetLabelOffset(0,'y')
#     style.SetTitleSize(0.05,'x')
#     style.SetLabelSize(0.05,'x')
#     style.SetTitleOffset(1.02,'x')
#
#     style.SetPadRightMargin(rightMargin)
#     style.SetPadTopMargin(topMargin)
#     style.SetPadBottomMargin(botMargin)
#     style.SetPadLeftMargin(leftMargin)
#     style.cd()

# depreciated
# def get_min_max_KE(file_path):
#     fo = open(file_path, "rw+")
#     line = fo.readline()
#
#     minKE = -1.
#     maxKE = -1.
#     print "Name of the file: ", fo.name
#     while line:
#         # print line
#         if "minKE <- " in line:
#             x=re.findall(r"[-+]?\d*\.\d+|\d+",line )
#             # print x[0]
#             minKE = float(x[0])
#             print minKE
#             # except ValueError, e:
#         if "maxKE <- " in line:
#             x=re.findall(r"[-+]?\d*\.\d+|\d+",line )
#             # print x[0]
#             maxKE = float(x[0])
#             print maxKE
#             # except ValueError, e:
#     # fo.close()
#         line = fo.readline()
#
#     if minKE<0:
#         print 'Error: could not find minKE!'
#     if maxKE<0:
#         print 'Error: could not find maxKE!'
#     return minKE,maxKE
