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
    
    '''    
    def __init__(self,constituentList,objID=None):
        self.objectType = self.__class__.__name__
        self.objID = objID
        