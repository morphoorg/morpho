from morpho.utilities import morphologging, reader
logger=morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)

class RootHistogram(object):

    def _createHisto(self):
        from ROOT import TH1F
        self.histo = TH1F(self.title,self.title,self.n_bins_x,self.x_min,self.x_max)
        self.histo.SetTitle("{};{};".format(self.title,self.xtitle))
    
    def __init__(self,input_dict,optStat='emr'):

        self.n_bins_x = reader.read_param(input_dict,"n_bins_x",100)
        self.x_min, self.x_max = reader.read_param(input_dict,"range",[0.,-1.])
        self.dataName = reader.read_param(input_dict,"data","required")
        self.title = str(reader.read_param(input_dict,"title",'hist_{}'.format(self.dataName)))
        self.xtitle = reader.read_param(input_dict,"x_title",self.dataName)
        self._createHisto()
        
    def Fill(self,input_data):
        if not isinstance(input_data,list):
            logger.error("Data given <{}> not a list")
            raise
        if self.x_min>self.x_max:
            logger.warning("Inappropriate x range: {}>{}".format(self.x_min,self.x_max))
            self.x_min = min(input_data)
            self.x_max = max(input_data)
            self._createHisto()
        for value in input_data:
            self.histo.Fill(value)
    
    def SetBinsContent(self,a_list):
        if len(a_list) != self.n_bins_x:
            logger.error("List size <{}> is not equal to number of bins <{}>".format(len(a_list),self.n_bins_x))
            raise
        for i, value in enumerate(a_list):
            self.histo.SetBinContent(i,value)

    def Draw(self,arg='hist'):
        self.histo.Draw(arg)

    