
# coding: utf-8

# In[1]:


import numpy as np
import importlib
# import os


# In[2]:


get_ipython().magic(u'load_ext autoreload')
get_ipython().magic(u'autoreload 2')


# In[12]:


from FactoryCalculator.Entities import Belt,Miner,Module,Inserter,Factory,Chest,Recipe #,Smelter
from FactoryCalculator.Utils import overview,add_dicts,convertRecipe
from FactoryCalculator.MetaEntities import MinerList
from FactoryCalculator import Data


# In[5]:


sMod1 = Module('speed',1)
sMod2 = Module('speed',2)
sMod3 = Module('speed',3)
miner1 = Miner('electric',material='copper',lvl=1)
miner1.add_modules([sMod1,sMod2])

miner2 = Miner('electric',material='iron',lvl=1)

b = Belt('yellow')
print(b.get_content())
b.load(miner1.get_output())
print(b.get_content())
b.load(miner2.get_output())
print('belt now contains {} in terms of items per s'.format(b.get_content()))


# In[6]:


I = Inserter('regular',lvl=1)
I.link_source(sourceObj=b)
I.get_output_max('copper',output_type='Factory')


# In[8]:



chest = Chest()

recipe = Recipe()
recipe.create_recipe(name = 'copper cables', materials_in = {'copper':1}, wait = 0.5, materials_out = {'copperCable':2})

f = Factory(recipe=recipe,prod_speed=0.5,FactoryType='factory_1')
f.set_factory_io([I],[chest])
f.produce()


# In[9]:


print('belt now contains {} in terms of items per s'.format(b.get_content()))


# ### want a summary function.
# 
# - call function to get overview of:
#     - all miners and their respective outputs
#     - all belts and their contents
#     - the input and output of all factories
# 
# what is reasonable:
# - feed all objects about which you want information to the overview function
# 
# What needs to be implemented, but requires massive changes to structure of how loading/unloading is logged:
# - what is loaded onto what, etc.

# In[10]:


overview([b,miner1,miner2,f])


# In[13]:


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

I1 = Inserter('regular',lvl=1)
I2 = Inserter('regular',lvl=1)
I3 = Inserter('regular',lvl=1)
I4 = Inserter('regular',lvl=1)

f_greenChip = Factory(recipe=recipe_gc,prod_speed=0.5,FactoryType='factory1',objID='f_greenChip')
f_copperCable = Factory(recipe=recipe_cc,prod_speed=0.5,FactoryType='factory1',objID='f_copperCable')

I1.link_source(b2)
# I1.get_output_max('iron',output_type='Factory')

I3.link_source(b2)
# I3.get_output_max('copper',output_type='Factory')

f_copperCable.set_factory_io([I3],I2)

I2.link_source(f_copperCable)
# I2.get_output_max('copper cable',output_type='Factory')

f_greenChip.set_factory_io([I1,I2],I4)

f_copperCable.produce()
# print(f2.get_output())
# print(I2.get_output_max('copper cable'))
f_greenChip.produce()
f_copperCable.adjust_ProdScale_output()
I4.link_source(f_greenChip)
I4.take_materials(f_greenChip.output_total)

f_greenChip.adjust_ProdScale_output()
#


# In[14]:


overview([b2,b3,f_copperCable,f_greenChip])


# ## TO DO:
# 
# - Put stuff back on belt once factory speed is adjusted!
# 
# - Automate adjusting speed for all connected factories upstream when producing in factory.
# 
# - merge Smelter and Factory class. Essentially, move all fuel based functions and attributes to the factory class. Also move all power attributes. Add note about no fuel implying electricity. Electricity and productionScaling scales together.

# In[395]:


1.2/2.


# In[396]:


f_copperCable.store

