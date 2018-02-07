'''
    This module contains a 'general_data_reducer' method which histograms data points and saves the results to an output file (currently, only root is supported).
    This module must be called in a dictionary under "postprocessing" within the configuration file.
    Here is an example of such a dictionary:
    "postprocessing":
    {
    "which_pp":[
    {
    "method_name": "general_data_reducer", # Name of the method
    "module_name": "general_data_reducer", # Name of the python file that contains the method
    "input_file_name" : "./tritium_model/results/tritium_generator.root", # Path to the root file that contains the raw data
    "input_file_format" : "root", # Format of the input file
    "input_tree": "spectrum", #  Name of the root tree containing data of interest
    "data": ["KE"], # Optional list of names of branches of the data to be binned (default=100)
    "minX":[18500.], # Optional list of minimum x axis values of the data to be binned
    "maxX":[18600.], # Optional list of maximum x axis values of the data to be binned
    "nBinHisto":[50], # List of desired number of bins in each histogram
    "output_file_name" : "./tritium_model/results/tritium_generator_reduced_fake.root", # Path to the file where the binned data will be saved
    "output_file_format": "root", # Format of the output file
    "output_file_option": RECREATE # RECREATE will erase and recreate the output file. UPDATE will open a file (after creating it, if it does not exist) and update the file.
    }
]}

    To do: Update this code to allow for data of the form (X, Y) as input.
'''


import logging
logger = logging.getLogger(__name__)

try:
    import ROOT as ROOT# import ROOT, TStyle, TCanvas, TH1F, TGraph, TLatex, TLegend, TFile, TTree, TGaxis, TRandom3, TNtuple, TTree
    import numpy as np
except ImportError:
    pass
from array import array



def general_data_reducer(param_dict):
    logger.info("Reducing the generated data!")
    infile = read_input_file(param_dict)
    outfile = create_output_file(param_dict)
   
    if isinstance(param_dict['data'],list):
        X_val_array, nBinHisto, dX = find_histo_x_vals(param_dict, infile)
        Y_val_array = find_histo_y_vals(param_dict, infile, nBinHisto, X_val_array, dX)
    
        for i in range(len(param_dict['data'])):
            #Create a tree with the name param_dict['data'][i]
            out_tree = ROOT.TTree(param_dict['data'][i], param_dict['data'][i])
                       
            #Create branch X and fill with X_vals; create branch Y and fill with Y_vals
            tmp_x_axis_data = array('f',[ 0 ])
            tmp_y_axis_data = array('i',[ 0 ])
            out_tree.Branch('X', tmp_x_axis_data, 'X/F')
            out_tree.Branch('Y', tmp_y_axis_data, 'Y/I')

            for j in range(0, len(X_val_array[i])):
                tmp_x_axis_data[0] = X_val_array[i][j]
                tmp_y_axis_data[0] = Y_val_array[i][j]
                out_tree.Fill()

        outfile.Write()               
        outfile.Close()
                       
        logger.info('Data binning complete.')


def read_input_file(param_dict):
    logger.info("Input data file: {}".format(param_dict['input_file_name']))
    if (param_dict['input_file_name'].endswith('.root')):
        param_dict['input_file_format']='root'
    if (param_dict['input_file_name'].endswith('.h5')):
        param_dict['input_file_format']='h5'
    if (param_dict['input_file_format']=='root'):
        infile = ROOT.TFile(param_dict['input_file_name'],"READ")
        return infile
    elif (param_dict['input_file_format']=='h5'):
        logger.debug('h5 file is not yet supported in the data_reducer')
        return
    else:
        logger.debug('{} file is not a known format'.format(param_dict['input_file_format']))
        return


def create_output_file(param_dict):
    # Creating the root file
    if 'output_file_format' not in param_dict:
        param_dict['output_file_format']='root' # setting root as default
    if param_dict['output_file_format']=='root':
        if 'output_file_name' not in param_dict:
            param_dict['output_file_name'] = param_dict['input_file_name']
        logger.info("Output data file: {}".format(param_dict['output_file_name']))
            
        if param_dict['output_file_name'] == param_dict['input_file_name']:
            outfile = ROOT.TFile(param_dict['output_file_name'],"UPDATE")
        else:
            if 'output_file_option' in param_dict:
                outfile = ROOT.TFile(param_dict['output_file_name'],param_dict['output_file_option'])
            else:
                outfile = ROOT.TFile(param_dict['output_file_name'],"RECREATE")
        return outfile

    elif param_dict['output_file_format']=='h5':
        logger.debug('h5 file is not yet supported in the data_reducer')
        return
    else:
        logger.debug('{} file is not a known format'.format(param_dict['output_file_format']))
        return


def read_data_array(param_dict, infile, index):
    list_data = []
    tree = infile.Get(param_dict['input_tree'])
    n = tree.GetEntries()
    for j in range(0,n):
        tree.GetEntry(j)
        list_data.append(getattr(tree,param_dict['data'][index]))
    return list_data


def find_histo_x_vals(param_dict, infile):
    X_val_array=[]
    for i in range(len(param_dict['data'])):
        if 'nBinHisto' in param_dict:
            nBinHisto = param_dict['nBinHisto'][i]
        else:
            nBinHisto = 100
        if 'minX' in param_dict:
            minX = param_dict['minX'][i]
        else:
            minX = min(read_data_array(param_dict, infile, i))
        if 'maxX' in param_dict:
            maxX = param_dict['maxX'][i]
        else:
            maxX = max(read_data_array(param_dict, infile, i))
            
        dX = (maxX - minX)/nBinHisto
        X_vals = []
        temp_x = minX + dX/2.
        for j in range(nBinHisto):
            X_vals.append(temp_x)
            temp_x += dX
        X_val_array.append(X_vals)
    return np.array(X_val_array), nBinHisto, dX


def find_histo_y_vals(param_dict, infile, nBinHisto, X_val_array, dX):
    Y_val_array=[]
    for i in range(len(param_dict['data'])):
        list_data = read_data_array(param_dict, infile, i)
        Y_vals = [0]*nBinHisto

        #This hack is currently needed to account for a very small
        #rounding error (on the order of round_error/X = 10^{-13})
        if 'maxX' in param_dict:
            round_error = 0
        else:
            round_error = max(list_data) - max(X_val_array[i]) - dX/2

        for x in list_data:
            k = 0
            while x > X_val_array[i][k] - dX/2.:
                if x <= X_val_array[i][k] + dX/2. + round_error:
                    Y_vals[k]+=1
                    break 
                k += 1
        Y_val_array.append(Y_vals)
    return np.array(Y_val_array)
                       
           
            










