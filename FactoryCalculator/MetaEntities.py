from FactoryCalculator.Utils import add_dicts

class MinerList:
    '''
    Takes list of miners as input when initiated. get_output() calculates collective outuput
    '''    
    def __init__(self,minerList,objID=None):
        self.objectType = self.__class__.__name__
        self.minerList = minerList
        self.objID = objID

    def get_output(self):
        output = add_dicts([m.get_output() for m in self.minerList])
        return output

class MetaFactory:
    '''
    Takes list of factories. Does magic. Supposed to collect input/output to facilitate making larger factories.
    '''
    def __init__(self,fList,objID=None):
        self.objectType = self.__class__.__name__
        self.objID = objID
        self.fList = fList
        
        self.inputs = [] # List of belts,miners,etc
        self.outputs = None # {material:item_s} this must no go into a chest
        
        # for f in fList:
        #     for input_obj in np.array(f.inputList)[:,0]:
        #         if input_obj