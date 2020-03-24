
# coding: utf-8

# In[410]:


from IPython.core.debugger import set_trace


# In[2]:


import numpy as np
import importlib
# import os
get_ipython().magic(u'load_ext autoreload')
get_ipython().magic(u'autoreload 2')
from FactoryCalculator.Entities2 import Belt,Miner,Module,Inserter,Factory,Chest,Recipe
from FactoryCalculator.Utils import overview,add_dicts,convertRecipe
from FactoryCalculator import Data
from FactoryCalculator.MetaEntities import MinerList


# - Initiate all factories
# - let them make requests of what they need. This creates a tree of requirements of {material:item_s} for each factory, setting a goal of what each factory must produce.
# 
# for each line of material: all n entities that want material from it gets 1/n of the available material. Starting with the entity that wants the least material this material is given to that entity. The remaining material is then divided to the n-1 entities, giving them 1/(n-1) each. This process continues until the material is out or all entities have all material they need.
# 
# Note that this assumes that the factories are taking material in parallel instead of serially from e.g. the belt. This is ok for small arrays of factories or where the belt layout respects this assumption or where there is sufficient material at the source to satisfy all entities.
# 
# For larger factories containing multiple arrays of entities drawing from the same source of materials, note that you need to set them up serially such that factory1, containing two entitites drawing from belt1, is sorted out completely and that their combined draw of resources from belt1 is accounted for before offering the remaining resources on belt1 to factory2.
# 
# - Create source of material
# - Create factories and initiate them
# - Connect factories
#     - This involves putting other objects in a list. However, these objects come in tuples, together with a speed, which represents the inserter used to transport them. We thus make away with the inserter class. This speed can be retrieved from Data.InserterSpeeds.
#     

# In[435]:


#### setup some small miners

miner_iron_1 = Miner('electric',material='iron',lvl=1)
miner_iron_2 = Miner('electric',material='iron',lvl=1)

miners_iron1 = [miner_iron_1,miner_iron_2]
miner_iron_list_1 = MinerList(miners_iron1)
iron_ouput1 = miner_iron_list_1.get_output()


#### setup an array of 30 copper miners

im = 30
miners_copper1 = [Miner('electric',material='copper',lvl=1) for i in range(im)]
miner_copper_list_1 = MinerList(miners_copper1)
copper_ouput1 = miner_copper_list_1.get_output()

#### pipe output of iron and then copper onto yellow belt. Not all copper fits

b2 = Belt('yellow',objID='b2')

b2.load(iron_ouput1)

b2.load(copper_ouput1)

print(b2.get_content())

#### use two inserters, one for iron and one for copper, to transfer material.
# Iron -> green chip
# 
# copper -> copper cables -> green chip 
# 
# green chip -> yellow belt

# create everything backwards, starting with the end product and where it ends up
b3 = Belt('yellow',objID='b3')

recipe_gc = Recipe()
recipe_gc.create_recipe(name = 'green chip',materials_in = {'copper cable':3,'iron':1},wait = 0.5,materials_out = {'green chip':1})

recipe_cc = Recipe()
recipe_cc.create_recipe(name = 'copper cables',materials_in = {'copper':1},wait = 0.5,materials_out = {'copper cable':2})

f_greenChip = Factory(recipe=recipe_gc,prod_speed=0.5,FactoryType='factory1',objID='f_greenChip',fuel=None)
f_copperCable = Factory(recipe=recipe_cc,prod_speed=0.5,FactoryType='factory1',objID='f_copperCable',fuel=None)
f_copperCable2 = Factory(recipe=recipe_cc,prod_speed=0.5,FactoryType='factory1',objID='f_copperCable2',fuel=None)
f_copperCable3 = Factory(recipe=recipe_cc,prod_speed=0.5,FactoryType='factory1',objID='f_copperCable3',fuel=None)

f_greenChip.clear_IO()
f_copperCable.clear_IO()


# In[436]:


inserter = 'regular'
inserterLvl = 1
inserterMode='item_s_chest_to_chest'
Inserter_speed = Data.Inserters[inserter][inserterLvl][inserterMode] # gives item_s


# In[437]:


f_greenChip.addInput(f_copperCable,Inserter_speed)
f_greenChip.addInput(f_copperCable2,Inserter_speed)
f_greenChip.addInput(f_copperCable3,Inserter_speed)
f_greenChip.addInput(b2,Inserter_speed)
f_greenChip.addOutput(b3,Inserter_speed)

f_copperCable.addInput(b2,Inserter_speed)
f_copperCable.addOutput(f_greenChip,Inserter_speed)

f_copperCable2.addInput(b2,Inserter_speed)
f_copperCable2.addOutput(f_greenChip,Inserter_speed)

f_copperCable3.addInput(b2,Inserter_speed)
f_copperCable3.addOutput(f_greenChip,Inserter_speed)

fList = [f_greenChip,f_copperCable,f_copperCable2,f_copperCable3]


# In[427]:


f_greenChip.clear_IO()
f_copperCable.clear_IO()


# In[445]:


def calculate_productionScaling(f):
    '''
    updates the production scaling [0:1] of factory f. 
    Pass the actual factory object as f. 
    It needs to have its inputs and output set.
    '''
    outputSpeed = f.outputDestination[2] # this gets the output speed of the factory
    print('At maximum capacity {} produces {:.3f} {} per second'.format(f.objID,list(f.output_max.values())[0],list(f.output_max.keys())[0]))
    print('{} has a maximal transfer of {:.3f} {} per second to {}'.format(f.objID,outputSpeed,list(f.output_max.keys())[0],f.outputDestination[1])) 
    print('----')
    # This sets the production scaling to respect the speed by which we can remove items from the factory
    # It also checks what quantity of material is requested and adjusts the speed to this as well
    f.productionScaling = min(1,f.productionScaling,float(outputSpeed)/list(f.get_output_adjusted().values())[0]) 
    for material in f.input_adjusted.keys(): # what the requested number of item/s is
        item_s_requested = f.input_adjusted[material] # note that we need to do this, instead of looping over f.input_items() since we are updating f inside the loop
        print('{} requests {:.3f} {} at a production scaling of {:.3f}'.format(f.objID,item_s_requested,material,f.productionScaling))
        input_i = 0 # material provided by all input sources that carries the material in question
        Input_relScale = {}
        input_rate_dict = {}
        availability_rate_dict = {}
        inputObjs = np.array(f.inputList)[:,0]
        for input_obj,input_name,input_TopSpeed in f.inputList: # iterate over all input objects
            input_rate = 0 #start by assuming that the source does not provide the material
            item_s_available = 0
            if input_obj.objectType=='Factory': # check what type the input is. This, sort of unfortunately, currently dictates what function names must be used 
                if material in input_obj.get_output_adjusted(): # make sure that the requested material is indeed at this location
                    item_s_available = input_obj.get_output_adjusted()[material]
            elif input_obj.objectType=='Belt':
                if material in input_obj.get_content():                    
                    item_s_available = input_obj.get_content()[material]
            elif input_obj.objectType=='Miner':
                if material in input_obj.get_content():
                    item_s_available = input_obj.get_output()[material]
            if item_s_available:
                input_rate = min(item_s_requested,item_s_available,input_TopSpeed) #find the bottleneck amongst requested item/s, available item/s or transfer speed as set by insterter
                print('from {} we have maximal transfer of {:.3f} {} per second to {}'.format(input_name,input_rate,material,f.objID))
            else:
                input_rate = 0
            input_i += input_rate # if the input source provides the requested material, add it to the total rate                
            input_rate_dict[input_obj] = input_rate # save this value in dict to be used to caluclate relative rates
            availability_rate_dict[input_obj] = item_s_available
            
        for input_obj in inputObjs:
            input_rate = input_rate_dict[input_obj]
            item_s_available = availability_rate_dict[input_obj]
            Input_relScale[input_obj] = input_rate/input_i # how much of the total available number of this material does this particular source correspond to
            if input_obj.objectType=='Factory':
                if item_s_available>0:
                    input_obj.productionScaling = min(input_obj.productionScaling,Input_relScale[input_obj]*item_s_requested/item_s_available)
        
        print('There is {:.3f} {} per second a priori available out of {:.3f} requested'.format(input_i,material,item_s_requested))
        scaling = float(input_i)/float(f.input_max[material])        
        
        if scaling<f.productionScaling:
            print('New production scaling set to {:.3f} due to bottleneck in delivery of {}'.format(scaling,material))
            f.add_bottleneck(material)
            f.productionScaling = scaling
            adjust_materialRequests(f)
        
    print('----')
    print('production scaling for {} is {:.3f}'.format(f.objID,f.productionScaling))
    
def adjust_materialRequests(f):
    input_adjusted = {material:item_s_requested*f.productionScaling for material,item_s_requested in f.input_max.items()}
    f.input_adjusted = input_adjusted
    print('input is adjusted to a production scaling of {:.3f}, to\n{}'.format(f.productionScaling,input_adjusted))
    


# In[446]:


for f in fList:
    f.reset_scales()


# In[447]:


for f in fList:
    calculate_productionScaling(f)
    print('===========')
# print('\nagain:\n')
# for f in fList:
#     calculate_productionScaling(f)
#     print('===========')


# In[441]:


0.72*3*1.2


# In[358]:


f = fList[0]


# In[359]:


for input_obj,input_name,input_TopSpeed in f.inputList: # iterate over all input objects
    


# In[365]:


inputObjs = np.array(f.inputList)[:,0]


# In[366]:


def unload_materials(f):
    '''

    Pass the actual factory object as f. 
    It needs to have its inputs and output set.
    Needs to have run calculate_productionScaling() already to a point where equilibrium is reached for all involved factories
    '''
    for material in f.input_adjusted.keys(): # what the requested number of item/s is for each material requested
        item_s_requested = f.input_adjusted[material] 
        print('{} requests {:.3f} {} at a production scaling of {:.3f}'.format(f.objID,item_s_requested,material,f.productionScaling))
        inputObjs = np.array(f.inputList)[:,0]
        Input_relScale = {}
        for input_obj,input_name,input_TopSpeed in f.inputList: # iterate over all input objects
            item_s_available = 0
            if input_obj.objectType=='Factory': # check what type the input is. This, sort of unfortunately, currently dictates what function names must be used 
                if material in input_obj.get_output_adjusted(): # make sure that the requested material is indeed at this location
                    item_s_available = input_obj.get_output_adjusted()[material]
            elif input_obj.objectType=='Belt':
                if material in input_obj.get_content():
                    item_s_available = input_obj.get_content()[material]
            elif input_obj.objectType=='Miner':
                if material in input_obj.get_content():
                    item_s_available = input_obj.get_output()[material]
        # This is how much is to be unloaded from each input_object
        
            Input_relScale[input_obj] = item_s_available/item_s_requested
        
        for input_obj in inputObjs:
            
# def produce(fList):
#     for f in fList:
#         for input_obj in np.array(f.inputList)[:,0]:
#             if 


# In[378]:


input_obj.get_content()


# In[367]:


f = fList[0]


# In[371]:


i1 = f.inputList[0][0]
i3 = f.inputList[2][0]


# In[370]:


i1.get_output_adjusted()


# In[373]:


i3.get_content()


# In[376]:


class MetaFactory:
    def __init__(self,fList,objID=None):
        self.objectType = self.__class__.__name__
        self.objID = objID
        self.fList = fList
        
        self.inputs = [] # List of belts,miners,etc
        self.outputs = None # {material:item_s} this must no go into a chest
        
        for f in fList:
            for input_obj in np.array(f.inputList)[:,0]:
                if input_obj


# In[377]:


f.inputList


# In[342]:


b2.get_content()


# In[343]:


b3.get_content()


# In[344]:


f_greenChip.get_output_adjusted()


# In[331]:


f = fList[0]
calculate_productionScaling(f)
adjust_materialRequests(f)


# In[332]:


f = fList[1]
calculate_productionScaling(f)
adjust_materialRequests(f)
print('--------')
f = fList[2]
calculate_productionScaling(f)
adjust_materialRequests(f)


# # To do
# - add that it draws from simultaneously multiple sources in proportion to their available output
# - make more complicated test case
