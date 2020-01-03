import numpy as np

class Belt:
    '''
    belts can carry x items/second (x item_s). They do so over two lanes.
    A belt has property of carrying x_i item_s_i for any i=0,1,2...
    When adding a new material, specify material and item_s_i. This is added to the extend 
    that sum_i item_s_i \leq max_load
    '''
    def __init__(self, colour):
        self.objectType = 'band'
        self.set_type(colour)
        self.materials = {}
        self.total_load = 0
        
    def check_load_balance(self,item_s,material,action):
        if action == 'load':
            if self.total_load + item_s < self.max_load:
                item_s_add = item_s
            else:
                item_s_add = self.max_load - self.total_load
            return item_s_add
        
        if action == 'unload':
            if not material in self.materials.keys():
                print('{} not on the belt'.format(material))
                return 0
            if self.materials[material] - item_s > 0:
                item_s_take = item_s
            else:
                item_s_take = self.materials[material]
            return item_s_take
        
    def load(self,material,item_s):
        '''
        Adds item_s items per second of some material to the belt. It does not add more material than is allowed.
        '''
        item_s_add = self.check_load_balance(item_s,material,action='load')
        if item_s_add > 0:
            if material in self.materials.keys():
                self.materials[material] += item_s_add
            else:
                self.materials[material] = item_s_add
            self.total_load += item_s_add
        
    def unload(self,material,item_s):
        '''
        Removes item_s items per second of some material to the belt.
        It checks if the material is present. It takes no more material than is available.
        '''
        item_s_take = self.check_load_balance(item_s,material,action='unload')
        if item_s_take > 0:
            if material in self.materials.keys():
                self.materials[material] -= item_s_take
            else:
                self.materials[material] = item_s_take

            self.tidy_materials()

            self.total_load -= item_s_take
            
        return (material,item_s_take)

    def removekey(self,d,key):
        r = dict(d)
        del r[key]
        return r
    
    def tidy_materials(self):
        for k,i in zip(self.materials.keys(),self.materials.values()):
            if i==0:
                self.materials = self.removekey(self.materials,k)
        
    def set_type(self,colour):
        self.type = colour
        self.set_max_load()
            
    def set_max_load(self):
        if self.type=='yellow':
            self.max_load = 15 #items/s
        elif self.type=='red':
            self.max_load = 30 
        elif self.type=='blue':
            self.max_load = 45
        else:
            print('Invalid belt type!')



class Miner:
    '''
    Miners produce self.mining_speed items per second of a given material. 
    They have attributes for modules and science upgrades.
    '''
    def __init__(self,tech,material,lvl=1):
        self.objectType = 'miner'
        self.mining_base_speed,self.module_slots = self.set_type(tech)
        self.material = material
        self.modules = []
        self.lvl=lvl
        self.lvl_prod_bonus = self.get_miner_lvl_bonus()
        self.mining_speed = self.update_mining_speed()
            
    def set_type(self,tech):
        
        self.type = tech
        if self.type=='burner':
            mining_base_speed = 0.25 #items/s
            module_slots = 0
        elif self.type=='electric':
            mining_base_speed = 0.5 
            module_slots = 3
        else:
            raise Exception('Invalid miner type, only "burner" and "electric" available') 
        return mining_base_speed,module_slots
            
    def add_modules(self,modules): # give modules as Module objects [sMod1 = Module(speed,1), etc]
        if len(modules) <= self.module_slots:
            self.modules = modules
            self.mining_speed = self.update_mining_speed()
        else:
            raise Exception('too many modules, only {} slots available'.format(self.module_slots))

    def update_mining_speed(self):
        mod_lvl = self.get_miner_lvl_bonus()
        
        if len(self.modules)>0:
            mod_mod = np.prod([m.speedMod for m in self.modules])
        else:
            mod_mod = 1
            
        mining_speed = self.mining_base_speed*mod_lvl*mod_mod
        return mining_speed
        
    def get_miner_lvl_bonus(self):
        lvl_bonus = 1 + 0.1 * (self.lvl-1)
        return lvl_bonus
            
        
    def get_output(self):
        return (self.material,self.mining_speed)
        


class Module:
    def __init__(self,tech,lvl):
        self.objectType = 'module'
        self.type = tech
        self.lvl = lvl
        if self.type=='speed':
            if self.lvl==1:
                self.speedMod = 1.20
            elif self.lvl==2:
                self.speedMod = 1.30
            elif self.lvl==3:
                self.speedMod = 1.50
        
        else:
            print('type not implemented')
        


class Inserter:
    '''
    A class for taking item_s items per second away from something (e.g. belt) of some material and putting it in factory, another belt, or chest.
    The key is that it is linked to the output place. This is how we know the max pace at which it can take material.
    '''
    def __init__(self,tech,lvl):

        self.objectType = 'inserter'
        self.type = tech
        self.lvl = lvl
        self.set_speed()
    
    def set_speed(self):
        if self.type=='burner':
            if self.lvl==1:
                self.item_s_chest_to_chest = 0.60
                self.item_s_chest_to_belt_yellow = 0.60
                self.item_s_chest_to_belt_red = 0.60
                self.item_s_chest_to_belt_blue = 0.60
            if self.lvl==2:
                self.item_s_chest_to_chest = 1.20
                self.item_s_chest_to_belt_yellow = 1.19
                self.item_s_chest_to_belt_red = 1.19
                self.item_s_chest_to_belt_blue = 1.19
            if self.lvl==7:
                self.item_s_chest_to_chest = 0.83
                self.item_s_chest_to_belt_yellow = 0.83
                self.item_s_chest_to_belt_red = 0.83
                self.item_s_chest_to_belt_blue = 0.83
        elif self.type=='regular':
            if self.lvl==1:
                self.item_s_chest_to_chest = 1.20
                self.item_s_chest_to_belt_yellow = 1.20
                self.item_s_chest_to_belt_red = 1.20
                self.item_s_chest_to_belt_blue = 1.20
            if self.lvl==2:
                self.item_s_chest_to_chest = 1.67
                self.item_s_chest_to_belt_yellow = 1.64
                self.item_s_chest_to_belt_red = 1.64
                self.item_s_chest_to_belt_blue = 1.64
            if self.lvl==7:
                self.item_s_chest_to_chest = 2.50 
                self.item_s_chest_to_belt_yellow = 2.25
                self.item_s_chest_to_belt_red = 2.37
                self.item_s_chest_to_belt_blue = 2.43
        elif self.type=='long':
            if self.lvl==1:
                self.item_s_chest_to_chest = 1.20
                self.item_s_chest_to_belt_yellow = 1.20
                self.item_s_chest_to_belt_red = 1.20
                self.item_s_chest_to_belt_blue = 1.20
            if self.lvl==2:
                self.item_s_chest_to_chest = 2.40
                self.item_s_chest_to_belt_yellow = 2.35
                self.item_s_chest_to_belt_red = 2.35
                self.item_s_chest_to_belt_blue = 2.35
            if self.lvl==7:
                self.item_s_chest_to_chest = 3.60
                self.item_s_chest_to_belt_yellow = 3.10
                self.item_s_chest_to_belt_red = 3.33
                self.item_s_chest_to_belt_blue = 3.46
        elif self.type=='fast': #same as filter inserters
            if self.lvl==1:
                self.item_s_chest_to_chest = 2.31 
                self.item_s_chest_to_belt_yellow = 2.31 
                self.item_s_chest_to_belt_red = 2.31 
                self.item_s_chest_to_belt_blue = 2.31 
            if self.lvl==2:
                self.item_s_chest_to_chest = 4.62
                self.item_s_chest_to_belt_yellow = 4.44
                self.item_s_chest_to_belt_red = 4.44
                self.item_s_chest_to_belt_blue = 4.44
            if self.lvl==7:
                self.item_s_chest_to_chest = 6.92
                self.item_s_chest_to_belt_yellow = 5.29
                self.item_s_chest_to_belt_red = 6.00
                self.item_s_chest_to_belt_blue = 6.43
        elif self.type=='stack':
            if self.lvl==1:
                self.item_s_chest_to_chest = 4.62
                self.item_s_chest_to_belt_yellow = 4.44
                self.item_s_chest_to_belt_red = 4.44
                self.item_s_chest_to_belt_blue = 4.44
            if self.lvl==2:
                self.item_s_chest_to_chest = 9.23
                self.item_s_chest_to_belt_yellow = 5.71
                self.item_s_chest_to_belt_red = 7.06
                self.item_s_chest_to_belt_blue = 7.74
            if self.lvl==7:
                self.item_s_chest_to_chest = 27.69
                self.item_s_chest_to_belt_yellow = 6.79
                self.item_s_chest_to_belt_red = 10.91
                self.item_s_chest_to_belt_blue = 13.85
        
    def link_source(self,sourceObj,material):
        self.sourceObj = sourceObj
        if sourceObj.objectType == 'band':
            self.input_rate_max = sourceObj.material[material] #item / s of material
        if sourceObj.objectType == 'miner':
            self.input_rate_max = sourceObj.get_output()[1] #item / s of material
        
    def link_output(self,outputObj,material):
        return
        




class Factory:
    '''
    A generic class for (input - wait - ouput) kind of systems.
    Assume that a belt comes with some 
    '''
    def __init__(self,name,material_in,wait,material_out):
        self.objectType = 'factory'
        
        self.material_in = material_in # on the form [(material1,number1),(material2,number2)] #obs not item / s
        self.wait = wait
        self.modules = []

        self.item_s = ''
    
