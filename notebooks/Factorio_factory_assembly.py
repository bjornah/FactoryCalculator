
# coding: utf-8

# In[23]:


import numpy as np
# import os


# In[19]:


get_ipython().magic(u'load_ext autoreload')
get_ipython().magic(u'autoreload 1')


# In[21]:


from FactoryCalculator.Entities import Belt,Miner,Module,Inserter,Factory


# In[22]:


sMod1 = Module('speed',1)
sMod2 = Module('speed',2)
sMod3 = Module('speed',3)
miner = Miner('electric',material='iron',lvl=3)
miner.add_modules([sMod1,sMod2])
miner.mining_base_speed
miner.mining_speed

miner_ouput = miner.get_output()

b = Belt('yellow')
b.load(*miner_ouput)


# #### classes to make

# In[253]:


# class pump #mainly oil, but also water

# class pipe #similar to band, but only one type of fluid and maybe other issues

# class inserter #moves item/s. Similar to band

# class factory



# #### Other stuff to implement

# Modules (these can be tagged in the relevant classes)
# 
# Energy consumption
# 
# Pollution
# 
# Power plants
