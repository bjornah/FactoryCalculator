
# coding: utf-8

# In[1]:


import numpy as np
import importlib
# import os


# In[8]:


get_ipython().magic(u'load_ext autoreload')
get_ipython().magic(u'autoreload 2')


# In[57]:


from FactoryCalculator.Entities import Belt,Miner,Module,Inserter,Factory,Chest


# In[135]:


sMod1 = Module('speed',1)
sMod2 = Module('speed',2)
sMod3 = Module('speed',3)
miner = Miner('electric',material='copper',lvl=3)
miner.add_modules([sMod1,sMod2])
miner.mining_base_speed
miner.mining_speed

miner_ouput = miner.get_output()

b = Belt('yellow')
print(b.get_content())
b.load(miner_ouput)
print(b.get_content())

I = Inserter('regular',lvl=1)
I.link_source(b,'copper')
I.get_output_max('copper',output_type='factory')

chest = Chest()

f = Factory('reg_fact',{'copper':1},0.5,{'copperCable':2})

f.set_factory_io([I],[chest])
f.produce()
print(b.get_content())


# #### Other stuff to implement

# Modules (these can be tagged in the relevant classes)
# 
# Energy consumption
# 
# Pollution
# 
# Power plants
