'''
Definitions for plots
Authors: J. Johnston, M. Guigue, T. Weiss
Date: 06/26/18
'''

from morpho.utilities import morphologging, stanConvergenceChecker
logger = morphologging.getLogger(__name__)

try:
    import ROOT
except ImportError:
    pass


def _set_style_options(rightMargin,  leftMargin,  topMargin,  botMargin, optStat='emr'):
    '''
    Change ROOT Style of the canvas
    '''
    style = ROOT.TStyle(ROOT.gStyle)
    style.SetOptStat(optStat)
    style.SetLabelOffset(0.01, 'xy')
    style.SetLabelSize(0.05, 'xy')
    style.SetTitleOffset(0.8, 'y')
    style.SetTitleSize(0.05, 'x')
    style.SetTitleSize(0.05, 'y')
    # style.SetLabelSize(0.05,'y')
    # style.SetLabelOffset(0,'y')
    # style.SetLabelSize(0.05,'x')
    style.SetTitleOffset(1.02, 'x')

    style.SetPadRightMargin(rightMargin)
    style.SetPadTopMargin(topMargin)
    style.SetPadBottomMargin(botMargin)
    style.SetPadLeftMargin(leftMargin)
    style.cd()


def _prepare_couples(list_data):
    '''
    Prepare a list of pairs of variables for the a posteriori distribution
    '''
    N = len(list_data)
    newlist = []
    for i in range(1, N):  # y
        for j in range(0, i):  # x
            newlist.append([list_data[j], list_data[i]])
    return newlist


def _get2Dhisto(list_dataX, list_dataY, nbins, ranges, histo_title):
    '''
    Internal function: return TH2F
    '''
    # logger.debug('Setting x axis')
    x_range = ranges[0]
    if isinstance(x_range, list):
        if isinstance(x_range[0], (float, int)) and isinstance(x_range[1], (float, int)):
            if x_range[0] < x_range[1]:
                xmin = x_range[0]
                xmax = x_range[1]
            else:
                xmin, xmax = _autoRangeList(list_dataX)
        elif isinstance(x_range[0], (float, int)):
            _, xmax = _autoRangeList(list_dataX)
            xmin = x_range[0]
        elif isinstance(x_range[1], (float, int)):
            xmin, _ = _autoRangeList(list_dataX)
            xmax = x_range[1]
        else:
            xmin, xmax = _autoRangeList(list_dataX)
    else:
        xmin, xmax = _autoRangeList(list_dataX)

    # logger.debug('Setting y axis')
    y_range = ranges[1]
    if isinstance(y_range, list):
        if isinstance(y_range[0], (float, int)) and isinstance(y_range[1], (float, int)):
            if y_range[0] < y_range[1]:
                ymin = y_range[0]
                ymax = y_range[1]
            else:
                ymin, ymax = _autoRangeList(list_dataY)
        elif isinstance(y_range[0], (float, int)):
            ytemp, ymax = _autoRangeList(list_dataY)
            ymin = y_range[0]
        elif isinstance(y_range[1], (float, int)):
            ymin, ytemp = _autoRangeList(list_dataY)
            ymax = y_range[1]
        else:
            ymin, ymax = _autoRangeList(list_dataY)
    else:
        ymin, ymax = _autoRangeList(list_dataY)
    temphisto = ROOT.TH2F(histo_title, histo_title,
                          nbins[0], xmin, xmax, nbins[1], ymin, ymax)
    if len(list_dataX) != len(list_dataX):
        logger.critical("list of data does not have the same size. x: {}; y: {}".format(
            len(list_dataX), len(list_dataY)))
        return 0
    for i, _ in enumerate(list_dataX):
        temphisto.Fill(list_dataX[i], list_dataY[i])
    return temphisto


def _autoRangeList(alist):
    # logger.debug('Using autoRange')
    xmin = min(alist)
    xmax = max(alist)
    dx = xmax - xmin
    xmin = xmin - dx*0.05
    xmax = xmax + dx*0.05
    return xmin, xmax


def _autoRangeContent(hist):
    # logger.debug('Using autoRange')
    alist = []
    for i in range(0, hist.GetNbinsX()):
        alist.append(hist.GetBinContent(i))
    xmin = min(alist)*0.9
    xmax = max(alist)*1.1  # need to be done
    return xmin, xmax


def _fill_variable_grid(variable_names, draw_opt_2d):
    """
    pre: variable_name: variables to plot
         draw_opt_2D: Draw option to be used for 2D plots
    post: Returns a 2-tuple, where the first element is a grid of
          lists of variable names and the sedon is a grid of
          options that should be used to plot each list.
          The grid of variable names will contain list length 1
          with a single variable when a 1D histogram should be
          plotted, and a list length 2 for 2D histograms.
          Positions that should not have a plot contain None
    """
    rows, cols = len(variable_names), len(variable_names)
    name_grid = [[None]*cols for i in range(rows)]
    draw_opts_grid = [[None]*cols for i in range(rows)]
    colors_grid = [[None]*cols for i in range(rows)]

    colors_arr = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen,
                  ROOT.kYellow, ROOT.kMagenta, ROOT.kCyan,
                  ROOT.kOrange, ROOT.kViolet, ROOT.kTeal,
                  ROOT.kSpring, ROOT.kPink, ROOT.kAzure]
    for i in range(len(variable_names)):
        for j in range(len(variable_names)):
            if(i == 0 and j < cols-1):
                # First Row
                name_grid[i][j] = [variable_names[j]]
                draw_opts_grid[i][j] = "bar"
                colors_grid[i][j] = colors_arr[j % len(colors_arr)]
            elif(j == cols-1 and i > 0):
                # Last Column
                name_grid[i][j] = [variable_names[(i-2) % cols]]
                draw_opts_grid[i][j] = "hbar"
                colors_grid[i][j] = colors_arr[(
                    (i-2) % cols) % len(colors_arr)]
            elif(i > 0 and i+(cols-j) <= cols+1):
                name_grid[i][j] = [
                    variable_names[(i-2) % cols], variable_names[j]]
                draw_opts_grid[i][j] = draw_opt_2d
    return (name_grid, draw_opts_grid, colors_grid)

def _fill_variable_grid_corr_plot(variable_names):
    """
    pre: variable_name: variables to plot
    post: returns a grid of length 2 lists. The list in
          position [i,j] contains the ith variable name
          then the jth variable name
    """
    rows, cols = len(variable_names), len(variable_names)
    name_grid = [[None]*cols for i in range(rows)]
    for i in range(rows):
        for j in range(cols):
            name_grid[i][j] = [variable_names[i],
                               variable_names[j]]
    return name_grid



def _fill_hist_grid(input_dict, name_grid,
                    nbins_x, nbins_y):
    '''
    Creates a grid of histograms from a dictionary of data.
    Note that it removes the warmup part of the chain.
    '''
    rows, cols = len(name_grid), len(name_grid[0])
    hist_grid = [[None]*cols for i in range(rows)]
    warmup = input_dict["is_sample"].count(0)
    # tree = myfile.Get(input_tree)
    # n = tree.GetEntries()
    # n = len(input_dict[list(input_dict.keys())[0]])
    for r, row in enumerate(name_grid):
        for c, names in enumerate(row):
            if (names is not None and len(names) == 2):
                list_dataX = []
                list_dataY = []
                # for i in range(0,n):
                # tree.GetEntry(i)
                # list_dataY.append(getattr(tree, names[0]))
                # list_dataX.append(getattr(tree, names[1]))
                list_dataY = input_dict[names[0]][warmup:]
                list_dataX = input_dict[names[1]][warmup:]
                histo = _get2Dhisto(list_dataX, list_dataY, [nbins_x, nbins_y],
                                    [0, 0], '{}_{}'.format(names[0], names[1]))
                histo.SetTitle("")
                histo.GetYaxis().SetTitle(names[0])
                histo.GetXaxis().SetTitle(names[1])
                hist_grid[r][c] = histo
            elif (names is not None and len(names) == 1):
                list_data = []
                # for i in range(0,n):
                # tree.GetEntry(i)
                # list_data.append(getattr(tree, names[0]))
                list_data = input_dict[names[0]][warmup:]
                x_range = _autoRangeList(list_data)
                histo = ROOT.TH1F("%s_%i_%i" % (names[0], r, c), names[0],
                                  nbins_x, x_range[0], x_range[1])
                for value in list_data:
                    histo.Fill(value)
                histo.SetTitle("")
                histo.GetXaxis().SetTitle(names[0])
                hist_grid[r][c] = histo
            else:
                hist_grid[r][c] = None
    return hist_grid

def _fill_hist_grid_divergence(input_dict, name_grid,
                               nbins_x, nbins_y):
    '''
    Creates a grid of histograms from a dictionary of data.
    Note that it removes the warmup part of the chain.
    A two-tuple of histograms is created for each 2D grid,
    with the first for convergent points and the second for
    divergent points.
    '''
    rows, cols = len(name_grid), len(name_grid[0])
    hist_grid = [[None]*cols for i in range(rows)]
    warmup = input_dict["is_sample"].count(0)
    for r, row in enumerate(name_grid):
        for c, names in enumerate(row):
            if (names is not None and len(names) == 2):
                list_dataY = input_dict[names[0]][warmup:]
                list_dataX = input_dict[names[1]][warmup:]
                y_div0, y_div1 = stanConvergenceChecker.partition_div(input_dict, names[0])
                x_div0, x_div1 = stanConvergenceChecker.partition_div(input_dict, names[1])
                if(len(x_div0)>0):
                    histo_div0 = _get2Dhisto(x_div0, y_div0, [nbins_x, nbins_y],
                                             [0, 0], '{}_{}'.format(names[0], names[1]))
                    histo_div0.SetTitle("")
                    histo_div0.GetYaxis().SetTitle(names[0])
                    histo_div0.GetXaxis().SetTitle(names[1])
                else:
                    histo_div0 = None
                if(len(x_div1)>0):
                    histo_div1 = _get2Dhisto(x_div1, y_div1, [nbins_x, nbins_y],
                                             [0, 0], '{}_{}'.format(names[0], names[1]))
                    histo_div1.SetTitle("")
                    histo_div1.GetYaxis().SetTitle(names[0])
                    histo_div1.GetXaxis().SetTitle(names[1])
                else:
                    histo_div1 = None
                hist_grid[r][c] = (histo_div0, histo_div1)
            elif (names is not None and len(names) == 1):
                list_data = []
                list_data = input_dict[names[0]][warmup:]
                x_range = _autoRangeList(list_data)
                histo = ROOT.TH1F("%s_%i_%i" % (names[0], r, c), names[0],
                                  nbins_x, x_range[0], x_range[1])
                for value in list_data:
                    histo.Fill(value)
                histo.SetTitle("")
                histo.GetXaxis().SetTitle(names[0])
                hist_grid[r][c] = histo
            else:
                hist_grid[r][c] = None
    return hist_grid
