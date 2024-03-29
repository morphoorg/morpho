'''
ROOT IO processor
Authors: M. Guigue
Date: 06/26/18
'''

from __future__ import absolute_import

import os

from morpho.utilities import morphologging, reader

logger = morphologging.getLogger(__name__)

from morpho.processors.IO import IOProcessor

__all__ = []
__all__.append(__name__)


class IOROOTProcessor(IOProcessor):
    '''
    Base IO ROOT Processor
    The ROOT Reader and Writer

    Parameters:
        filename (required): path/name of file
        variables (required): variables to extract
        action: read or write (default="read")
        tree_name (required): name of the tree
        file_option: option for the file (default=Recreate)

    Input:
        None

    Results:
        data: dictionary containing the data
    '''

    def InternalConfigure(self, params):
        super().InternalConfigure(params)
        self.tree_name = reader.read_param(params, "tree_name", "required")
        self.file_option = reader.read_param(params, "file_option", "Recreate")
        return True

    def Reader(self):
        '''
        Read the content of a TTree in a ROOT File.
        Note the use of the uproot package.
        The variables should be a list of the "variable" to read.
        '''
        logger.debug("Reading {}".format(self.file_name))
        import uproot
        for key in self.variables:
            self.data.update({str(key): []})
        try:
            tree = uproot.open(self.file_name)[self.tree_name]
            for data in tree.iterate(self.variables):
                for key, value in data.items():
                    varName = key.decode("utf-8")
                    self.data.update({str(varName): self.data[str(varName)] + value.tolist()})
        except:
            logger.warning("An uproot related error was encountered. Switching to ROOT.")
            try:
                import ROOT
            except ImportError:
                logger.warning("Failed importing ROOT")
            else:
                infile = ROOT.TFile(self.file_name, "READ")
                tree = infile.Get(self.tree_name)
                for i in range(0, tree.GetEntries()):
                    tree.GetEntry(i)
                    for varName in self.variables:
                        if str(varName) not in self.data.keys():
                            logger.debug("Adding {} to data".format(varName))
                            self.data.update({str(varName): list()})
                        val = getattr(tree, varName)
                        if isinstance(val, int) or isinstance(val, float) or isinstance(val, list):
                            self.data[varName].append(val)
                        else:
                            self.data[varName].append(list(val))
                            
        return True

    def Writer(self):
        '''
        Write the data into a TTree in a ROOT File.
        The variables should be a list of dictionaries where
            - "variable" is the variable name in the input dictionary,
            - "root_alias" is the name of the branch in the tree,
            - "type" is the type of data to be saved.
        '''
        logger.debug("Saving data in {}".format(self.file_name))

        rdir = os.path.dirname(self.file_name)
        if not rdir == "" and not os.path.exists(rdir):
            os.makedirs(rdir)
            logger.debug("Creating folder: {}".format(rdir))

        logger.debug("Creating a file and tree")
        try:
            import ROOT
        except ImportError:
            pass

        f = ROOT.TFile(self.file_name, self.file_option)
        t = ROOT.TTree(self.tree_name, self.tree_name)
        info_data = {}
        numberData = -1
        hasUpdatedNumberData = False

        # Determine general properties of the tree: type and size of branches, number of iterations for the tree
        logger.debug("Defining tree properties")
        for a_item in self.variables:
            if isinstance(a_item, dict) and "variable" in a_item.keys():
                varName = a_item["variable"]
                if "root_alias" in a_item:
                    varRootAlias = a_item.get("root_alias")
                else:
                    varRootAlias = varName
                varType = a_item.get("type")
            elif isinstance(a_item, str):
                varName = a_item
                varRootAlias = a_item
                varType = None
            else:
                logger.error("Unknown type: {}".format(a_item))

            if numberData < len(self.data[varName]):
                if hasUpdatedNumberData:
                    logger.warning(
                        "Number of datapoints updated more than once: potential problem with input data")
                else:
                    logger.debug("Updating number datapoints")
                numberData = len(self.data[varName])
                hasUpdatedNumberData = True
            if isinstance(self.data[varName][0], list):
                info_subDict = {
                    "len": len(self.data[varName][0]),
                    "type": _branch_element_type_from_string(varType) or _branch_element_type(self.data[varName][0][0]),
                    "root_alias": varRootAlias
                }
            else:
                info_subDict = {
                    "len": 0,
                    "type": _branch_element_type_from_string(varType) or _branch_element_type(self.data[varName][0]),
                    "root_alias": varRootAlias
                }
            info_data.update({str(varName): info_subDict})

        # Create an empty class where the attributes will be used to write the tree
        class AClass(object):
            pass

        tempObject = AClass()

        logger.debug("Creating branches")
        from array import array
        for key in info_data:
            if info_data[key]["len"] == 0:
                setattr(tempObject, str(info_data[key]["root_alias"]), array(info_data[key]['type'].lower(), [
                    _get_zero_with_type(info_data[key]['type'])]))
                t.Branch(str(str(info_data[key]['root_alias'])), getattr(
                    tempObject, str(info_data[key]["root_alias"])),
                         '{}/{}'.format(str(info_data[key]['root_alias']), info_data[key]['type']))
            else:
                setattr(tempObject, str(info_data[key]["root_alias"]), array(info_data[key]['type'].lower(), int(
                    info_data[key]['len']) * [_get_zero_with_type(info_data[key]['type'])]))
                t.Branch(str(str(info_data[key]['root_alias'])),
                         getattr(tempObject, str(info_data[key]['root_alias'])),
                         '{}[{}]/{}'.format(str(info_data[key]['root_alias']), info_data[key]['len'],
                                            info_data[key]['type']))

        logger.debug("Adding data")
        for i in range(numberData):
            for key in info_data:
                temp_var = getattr(tempObject, str(info_data[key]['root_alias']))
                if info_data[key]["len"] == 0:
                    temp_var[0] = self.data[str(key)][i]
                else:
                    for j in range(info_data[key]["len"]):
                        temp_var[j] = self.data[str(key)][i][j]
                setattr(tempObject, str(key), temp_var)
            t.Fill()
        f.cd()
        t.Write()
        f.Close()
        logger.debug("File saved!")
        return True


def _branch_element_type(element):
    if isinstance(element, int):
        return "I"
    elif isinstance(element, float):
        return "F"
    else:
        logger.warning("{} not supported; using float".format(type(element)))
        return "F"


def _branch_element_type_from_string(string):
    if string == "float":
        return "F"
    elif string == "int":
        return "I"

    logger.debug(
        "{} not supported; while use data to determine type".format(string))
    return None


def _get_zero_with_type(a_type):
    if a_type == "F":
        return 0.
    elif a_type == "I":
        return 0
    else:
        logger.warning("{} not supported; using float".format(a_type))
        return 0.
