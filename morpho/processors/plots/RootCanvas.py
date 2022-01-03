'''
Root-based canvas class
Authors: M. Guigue
Date: 06/26/18
'''

import os

from morpho.utilities import morphologging, reader, plots
# from morpho.processors import BaseProcessor
logger = morphologging.getLogger(__name__)


class RootCanvas:
    '''
    Create default ROOT canvas object.

    Parameters:
        width: window width (default=600)
        height: window height (default=400)
        title: canvas title
        x_title: title of the x axis
        y_title: title of the y axis
        options: other options (logy, logx)
        output_path: where to save the plot
        output_pformat: plot format (default=pdf)
    '''

    def __init__(self, input_dict, optStat='emr'):

        self.width = reader.read_param(input_dict, "width", 600)
        self.height = reader.read_param(input_dict, "height", 400)
        self.title = reader.read_param(
            input_dict, "title", 'can_{}_{}'.format(self.height, self.width))
        if self.title != "":
            plots._set_style_options(0.04, 0.1, 0.07, 0.12, optStat)
        else:
            plots._set_style_options(0.04, 0.1, 0.03, 0.12, optStat)
        self.xtitle = reader.read_param(input_dict, "x_title", "")
        self.ytitle = reader.read_param(input_dict, "y_title", "")
        self.canvasoptions = reader.read_param(input_dict, "options", "")

        # Creating Canvas
        from ROOT import TCanvas
        self.canvas = TCanvas(self.title, self.title, self.width, self.height)
        if "logy" in self.canvasoptions:
            can.SetLogy()
        if "logx" in self.canvasoptions:
            can.SetLogx()

        # Output path
        self.path = reader.read_param(input_dict, "output_path", "./")
        self.output_format = reader.read_param(
            input_dict, "output_format", "pdf")
        if not self.path.endswith('/'):
            self.path = self.path + "/"
        if self.title != ' ':
            self.figurefullpath = self.path+self.title+'_'
        else:
            self.figurefullpath = self.path
        if isinstance(input_dict['variables'], str):
            self.figurefullpath += input_dict['variables']
        elif isinstance(input_dict['variables'], list):
            for namedata in input_dict['variables']:
                self.figurefullpath += namedata + '_'

        if self.figurefullpath.endswith('_'):
            self.figurefullpath = self.figurefullpath[:-1]
        self.figurefullpath += "." + self.output_format

    def cd(self, number=0):
        '''
        Go to frame 'number' of the TCanvas
        '''
        self.canvas.cd(number)

    def Divide(self, cols, rows):
        '''
        Divide the TCanvas
        '''
        self.canvas.Divide(cols, rows)

    def Draw(self):
        '''
        Draw the TCanvas
        '''
        self.canvas.Draw()

    def Save(self):
        '''
        Save the TCanvas
        '''
        rdir = os.path.dirname(self.figurefullpath)
        if not os.path.exists(rdir):
            os.makedirs(rdir)
            logger.info("Creating folder: {}".format(rdir))
        self.canvas.SaveAs(self.figurefullpath)
