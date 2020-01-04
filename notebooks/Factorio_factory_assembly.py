
# coding: utf-8

# In[1]:


import numpy as np
import importlib
# import os


# In[8]:


get_ipython().magic(u'load_ext autoreload')
get_ipython().magic(u'autoreload 2')


# In[310]:


from FactoryCalculator.Entities import Belt,Miner,Module,Inserter,Factory,Chest,Recipe


# In[357]:


sMod1 = Module('speed',1)
sMod2 = Module('speed',2)
sMod3 = Module('speed',3)
miner = Miner('electric',material='copper',lvl=3)
miner.add_modules([sMod1,sMod2])
miner.mining_base_speed
miner.mining_speed

miner_ouput = miner.get_output()

b = Belt('yellow')
# print(b.get_content())
b.load(miner_ouput)
# print(b.get_content())

I = Inserter('regular',lvl=1)
I.link_source(b,'copper')
I.get_output_max('copper',output_type='Factory')

chest = Chest()

recipe = Recipe()
recipe.create_recipe(name = 'copper cables',materials_in = {'copper':1},wait = 0.5,materials_out = {'copperCable':2})

f = Factory(recipe=recipe,prod_speed=0.5)
f.set_factory_io([I],[chest])
f.produce()
# print(b.get_content())


# In[359]:


#### setup some small miners

miner_iron_1 = Miner('electric',material='iron',lvl=3)
miner_iron_2 = Miner('electric',material='iron',lvl=3)

miners_iron1 = [miner_iron_1,miner_iron_2]
miner_iron_list_1 = MinerList(miners_iron1)
iron_ouput1 = miner_iron_list_1.get_output()


#### setup an array of 30 copper miners

im = 30
miners_copper1 = [Miner('electric',material='copper',lvl=3) for i in range(im)]
miner_copper_list_1 = MinerList(miners_copper1)
copper_ouput1 = miner_copper_list_1.get_output()

#### pipe output of iron and then copper onto yellow belt. Not all copper fits

b2 = Belt('yellow')

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
b3 = Belt('yellow')

recipe_gc = Recipe()
recipe_gc.create_recipe(name = 'green chip',materials_in = {'copper cable':3,'iron':1},wait = 0.5,materials_out = {'green chip':1})

recipe_cc = Recipe()
recipe_cc.create_recipe(name = 'copper cables',materials_in = {'copper':1},wait = 0.5,materials_out = {'copper cable':2})

I1 = Inserter('regular',lvl=1)
I2 = Inserter('regular',lvl=1)
I3 = Inserter('regular',lvl=1)

f1 = Factory(recipe=recipe_gc,prod_speed=0.5)
f2 = Factory(recipe=recipe_cc,prod_speed=0.5)

I1.link_source(b2,'iron')
I1.get_output_max('iron',output_type='Factory')

I3.link_source(b2,'copper')
I3.get_output_max('copper',output_type='Factory')

f2.set_factory_io([I3],[chest])

I2.link_source(f2,'copper cable')
I1.get_output_max('copper cable',output_type='Factory')

f1.set_factory_io([I1,I2],[b3])

f2.produce()
f1.produce()


# In[364]:


{m:items/f2.wait for m,items in f2.materials_out_max.items()}


# In[365]:


f2.wait


# In[360]:


f2.output


# In[361]:


f1.output


# In[210]:


import functools

def add_dicts(dicts):

    allkeys = functools.reduce(set.union, map(set, map(dict.keys, dicts)))
    c = {}
    for key in allkeys:
        items = 0
        for d in dicts:
            items += d[key] if key in d else 0
            c[key]=items
    return c

class MinerList:
    
    def __init__(self,minerList):
        self.objectType = self.__class__.__name__
        self.minerList = minerList
        
    def get_output(self):
        output = add_dicts([m.get_output() for m in self.minerList])
        return output


# #### Other stuff to implement

# Modules (these can be tagged in the relevant classes)
# 
# Energy consumption
# 
# Pollution
# 
# Power plants
