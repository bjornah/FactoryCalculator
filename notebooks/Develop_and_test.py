
# coding: utf-8

# In[ ]:


get_ipython().magic(u'load_ext autoreload')
get_ipython().magic(u'autoreload 2')


# In[564]:


from IPython.core.debugger import set_trace
import numpy as np
import importlib
from FactoryCalculator.Entities2 import Belt,Miner,Module,Factory,Chest,Recipe
from FactoryCalculator.Utils import add_dicts,convertRecipe
from FactoryCalculator import Data
from FactoryCalculator.Functions import calculate_productionScaling,adjust_materialRequests,unload_materials,overview
from FactoryCalculator.MetaEntities import MinerList


# In[565]:


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

#### transfer material.
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

inserter = 'regular'
inserterLvl = 1
inserterMode='item_s_chest_to_chest'
Inserter_speed = Data.Inserters[inserter][inserterLvl][inserterMode] # gives item_s

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


# In[549]:


f_greenChip.clear_IO()
f_copperCable.clear_IO()


# In[566]:


for f in fList:
    f.reset_scales()

# probably need to perform this once for each level of factories
for f in fList:
    calculate_productionScaling(f)
    print('===========')
print('0000000000000000000')
for f in fList:
    calculate_productionScaling(f)
    print('===========')
for f in fList:
    unload_materials(f)


# # To do
# ## First
# - improve comments in code and descriptions in functions
# - test setup where we have two copper cable factories but two inserters for each
# - implement proper unit tests
# - make additional and more complex test cases
# - clean up printed output when running factories
#     - implement log files and python logging functionality
# - test how we can make sure we have called calculate_productionScaling() enough times before calling unload_materials()
# - create miner-smelter setup (maybe meta entity for this?)
# 
# ----
# ## later 
# - make documentation
#     - import summary of functions using some library
#     - summarise overarching goals of package
# - create meta factories
# - create functions for data scraping for recipes and entity statistics
# - fix global power information
# - implement fluids
# - implement all aspects of modules (beacons can be implemented by simply adding more modules in module list for each factory)
# 
# ----
# ## aaand even later
# - create solver that can tell you what factories and input you need in order to get certain output, given some inserter level and type of factory etc
# - fix graphical representation of factory, input and output
# - make ML to try to go from MetaFactory to suggestion on actual setup in factorio

# # chalk board
# 
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
