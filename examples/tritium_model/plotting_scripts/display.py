from ROOT import TCanvas, TH1F, TGraphErrors
import math
from numbers import Number
from array import *
from termcolor import colored

def autorange(list):
    xmin = min(list)
    xmax = max(list)  # need to be done
    return xmin, xmax

def plot_average(KE_recon,events):
    can = TCanvas("ca","can",200,10,600,400)
    can.SetLogy()
    h=TH1F("h","",100,18550.,18575.)
    for i in range(0,len(events)):
        h.Fill(KE_recon[i],events[i])
    h.Draw()
    can.SaveAs("tritium_model/plotting_scripts/" + "events_vs_KE_recon_average.pdf")

def fillLogxHisto(list, xmin, xmax, nbins):

    print 'Option: Log x scale'


    logxmin = math.log10(xmin)
    logxmax = math.log10(xmax)
    binwidth = (logxmax - logxmin) / nbins
    tmp_xbins = []
#    print len(tmp_xbins)
    tmp_xbins.append(xmin)
#    print len(tmp_xbins)
    for i in range(1, nbins + 1):
        tmp = logxmin + (i) * binwidth
        ltmp = math.pow(10, tmp)
#         print '%.5f     %.5f' % (tmp, ltmp)
        tmp_xbins.append(ltmp)
    sort = sorted(tmp_xbins)
    xbins = array('d', sort)
#    for i in range(0,len(xbins)):
#        print xbins[i]


    h = TH1F("h", "", nbins, xbins)

    for j in range(1, len(list) + 1):
        xl = list[j - 1]
#        x = math.log10(xl)
#        print x
        h.Fill(xl)

    return h


def displayHisto(list, title, option):
#    Display and Save histo of the list data
#    The titles of the x and y axes are title[1] and title[2]
#    The pdf name is title[3].pdf
#    Various option in the option list
#    List of options:
#       - 1st item of the list: log scale or not
#         Example: "logx_logy" will display as logx and logy
#         Possible option: logx, logy, color...?
#         If unknown option, print error and stop
#       - 3rd/4st items of the list: array (xmin, xmax)
#         If "auto" or none, automatic selection of the the range
#         If xmin>xmax, print error and do "auto"




#    Setting x axis title
    if isinstance(title[0], basestring) == False:
        print colored('Warning:','yellow') + 'x axis title is not a string: ' + title[0]
        xtitle = "x"
    else:
        xtitle = title[0]
#    Setting y axis title
    if isinstance(title[1], basestring) == False:
        print colored('Warning:','yellow') + 'y axis title is not a string: ' + title[1]
        ytitle = " "
    else:
        ytitle = title[1]

    if isinstance(title[2], basestring) == False:
        print colored('Warning:','yellow') + 'pdfname is not a string: ' + title[2]
        can = TCanvas("default", "default", 200, 10, 600, 400)
        pdfname = "default"
    else:

        can = TCanvas(title[2], title[2], 200, 10, 600, 400)
        pdfname = title[2]

#    Checking if option format is OK
    if len(option) != 3:
        print colored('Error:','red') + 'Number of options != 3: (%d)' % len(option)
        return
    else :
        if isinstance(option[2][0],float ) == True & isinstance(option[2][1],basestring) == True:
            xmin, xmax = autorange(list)
            xmin = option[2][0]
        elif isinstance(option[2][0],basestring) == True & isinstance(option[2][1],float ) == True:
            xmin, xmax = autorange(list)
            xmax = option[2][1]
        elif option[2][0] < option[2][1]:
            xmin = option[2][0]
            xmax = option[2][1]
        else:
            print colored('Warning:','yellow') + 'Invalid range of histogram -> Setting automatic range!'
            xmin, xmax = autorange(list)
            print ' Range is: %d, %d' % (xmin, xmax)

    if option[1] >= 2:
        nbins = option[1]
    else:
        print colored('Warning:','yellow') + 'invalid number of bins -> Setting nbin = 100'
        nbins = 100

    if isinstance(option[0], basestring) == False:
        print colored('Error:','red') + 'first argument of option is not a string' + option[0]
        return

    if "logx" in option[0]:
        if xmin > 0:
            can.SetLogx()

            h1 = fillLogxHisto(list, xmin, xmax, nbins)
        else:
            print colored('Error:','red') + 'xmin negative or null -> Cannot have logx axis!'
            return
    else:
        h1 = TH1F("h1", "", nbins, xmin, xmax)
        for i in range(0, len(list)):
            h1.Fill(list[i])

    if "logy" in option[0]:
        can.SetLogy()

    can.cd()
    h1.GetXaxis().SetTitle(xtitle)
    h1.GetYaxis().SetTitle(ytitle)
    h1.Draw()
    can.SaveAs("tritium_model/plotting_scripts/" + pdfname + ".pdf")
    return can


def displayGraph(list, title, option):
#    Display and Save histo of the list data
#    The titles of the x and y axes are title[1] and title[2]
#    The pdf name is title[3].pdf
#    Various option in the option list
#    List of options:
#       - 1st item of the list: log scale or not
#         Example: "logx_logy" will display as logx and logy
#         Possible option: logx, logy, color...?
#         If unknown option, print error and stop
#       - 2nd items of the list: array (xmin, xmax, ymin,ymax)
#         If "auto" or none, automatic selection of the the range
#         If xmin>xmax, print error and do "auto"
#         If ymin>ymax, print error and do "auto"

    # Setting the type of plot you want
    if len(list)<2:
        print colored('Error:','red') + 'There are not X AND Y data'
        return
    elif len(list)==2:
        plot_errors = False
    elif len(list)==4:
        plot_errors = True
    else:
        return

#    Setting x axis title
    if isinstance(title[0], basestring) == False:
        print colored('Warning:','yellow') + 'x axis title is not a string: ' + title[0]
        xtitle = "x"
    else:
        xtitle = title[0]
#    Setting y axis title
    if isinstance(title[1], basestring) == False:
        print colored('Warning:','yellow') + 'y axis title is not a string: ' + title[1]
        ytitle = " "
    else:
        ytitle = title[1]

    if isinstance(title[2], basestring) == False:
        print colored('Warning:','yellow') + 'pdfname is not a string: ' + title[2]
        can = TCanvas("default", "default", 200, 10, 600, 400)
        pdfname = "default"
    else:
        can = TCanvas(title[2], title[2], 200, 10, 600, 400)
        pdfname = title[2]

#    Checking if option format is OK
    if len(option) != 2:
        print colored('Error:','red') + 'Number of options != 3: (%d)' % len(option)
        return
    else :
        # Setting the ranges of the plot
        if len(option[1])<4:
            print colored('Warning:','yellow') + 'Not enough range in options list -> Setting automatic range!'
            xmin, xmax = autorange(list[0])
            ymin, ymax = autorange(list[1])
            print 'Range x is: %d, %d' % (xmin, xmax)
            print 'Range y is: %d, %d' % (ymin, ymax)
        else:
            if isinstance(option[1][0],float ) == True & isinstance(option[1][1],basestring) == True:
                xmin, xmax = autorange(list[0])
                xmin = option[1][0]
            elif isinstance(option[1][0],basestring) == True & isinstance(option[1][1],float ) == True:
                xmin, xmax = autorange(list[0])
                xmax = option[1][1]
            elif option[1][0] < option[1][1]:
                xmin = option[1][0]
                xmax = option[1][1]
            else:
                print colored('Warning:','yellow') + 'Invalid range for x-> Setting automatic range!'
                xmin, xmax = autorange(list[0])
                print 'Range x is: %d, %d' % (xmin, xmax)

            if isinstance(option[1][2],float ) == True & isinstance(option[1][3],basestring) == True:
                ymin, ymax = autorange(list[1])
                ymin = option[1][2]
                print option[1][2]
                print option[1][3]
            elif isinstance(option[1][2],basestring) == True & isinstance(option[1][3],float ) == True:
                ymin, ymax = autorange(list[1])
                ymax = option[1][3]
            elif option[1][2] < option[1][3]:
                ymin = option[1][2]
                ymax = option[1][3]
            else:
                print colored('Warning:','yellow') + 'Invalid range -> Setting automatic range!'
                ymin, ymax = autorange(list[1])
                print 'Range y is: %d, %d' % (ymin, ymax)

    # Checking if first option item is a string
    if isinstance(option[0], basestring) == False:
        print colored('Error:','red') + 'first argument of option is not a string' + option[0]
        return

    # Setting logScales
    if "logx" in option[0]:
        if xmin > 0:
            can.SetLogx()
        else:
            print colored('Error:','red') + 'xmin negative or null -> Cannot have logx axis!'
            return
    if "logy" in option[0]:
        if ymin > 0:
            can.SetLogy()
        else:
            print colored('Error:','red') + 'xmin negative or null -> Cannot have logx axis!'
            return

    if len(list[0])!=len(list[1]):
        print colored('Error:','red') + 'Not the same number of X and Y'
        return

    g = TGraphErrors(len(list[0]))
    g.SetTitle("")
    if plot_errors:
        # print 'Plotting a TGraphError'
        for i in range(0,len(list[0])):
            # print i
            g.SetPoint(i,list[0][i],list[1][i])
            g.SetPointError(i,list[2][i],list[3][i])
    else:
        for i in range(0,len(list[0])):
            # print i
            g.SetPoint(i,list[0][i],list[1][i])



    can.cd()
    print ymin
    print ymax
    print xmin
    print xmax
    g.GetXaxis().SetRangeUser(xmin,xmax)
    g.GetYaxis().SetRangeUser(ymin,ymax)
    # print 'a'
    g.GetXaxis().SetTitle(xtitle)
    g.GetYaxis().SetTitle(ytitle)
    g.Draw("AP")
    # print 'a'
    can.SaveAs( "tritium_model/plotting_scripts/" + pdfname + ".pdf")
    return can
