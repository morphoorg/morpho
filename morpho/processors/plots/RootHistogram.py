import os

from morpho.utilities import morphologging, reader
# from morpho.processors import BaseProcessor
logger=morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)

class RootHistogram(object):
    
    def __init__(self,input_dict,optStat='emr'):

        self.n_bins_x = reader.read_param(input_dict,"n_bins_x",100)
        self.x_min, self.x_max = reader.read_param(input_dict,"range",[0.,-1.])
        self.dataName = reader.read_param(input_dict,"data","required")        
        self.title = str(reader.read_param(input_dict,"title",'hist_{}'.format(self.dataName)))
        self.xtitle = reader.read_param(input_dict,"x_title",self.dataName)
        
        # Creating Canvas
        from ROOT import TH1F
        self.histo = TH1F(self.title,self.title,self.n_bins_x,self.x_min,self.x_max)
        self.histo.SetTitle("{};{};".format(self.title,self.xtitle))
    
    def Fill(self,input_data):
        if not isinstance(input_data,list):
            logger.error("Data given <{}> not a list") 
            raise
        for value in input_data:
            self.histo.Fill(value)

    def Draw(self,arg='hist'):
        self.histo.Draw(arg)

    