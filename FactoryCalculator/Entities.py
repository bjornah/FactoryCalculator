import numpy as np
from IPython.core.debugger import set_trace

def removekey(d,key):
    r = dict(d)
    del r[key]
    return r

class Belt:
    '''
    belts can carry x items/second (x item_s). They do so over two lanes.
    A belt has property of carrying x_i item_s_i for any i=0,1,2...
    When adding a new material, specify material and item_s_i. This is added to the extend 
    that sum_i item_s_i \leq max_load
    '''
    def __init__(self, colour):
        self.objectType = self.__class__.__name__
        self.set_type(colour)
        self.materials = {} #dict of material:item_s
        self.total_load = 0
        
    def _check_load_balance(self,item_s,material,action):
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
        
    def load(self,materials):
        '''
        Adds item_s items per second of some material to the belt. It does not add more material than is allowed.
        '''
        if len(materials)>1:
            raise Exception('you can only load one material at the time!')

        material,item_s = [*materials.keys()][0],[*materials.values()][0]
        item_s_add = self._check_load_balance(item_s,material,action='load')
        if item_s_add > 0:
            if material in self.materials.keys():
                self.materials[material] += item_s_add
            else:
                self.materials[material] = item_s_add
            self.total_load += item_s_add
        
    def unload(self,materials):
        '''
        Removes item_s items per second of some material to the belt.
        It checks if the material is present. It takes no more material than is available.
        '''
        if len(materials)>1:
            raise Exception('you can only load one material at the time!')
        material,item_s = [*materials.keys()][0],[*materials.values()][0]


        item_s_take = self._check_load_balance(item_s,material,action='unload')
        if item_s_take > 0:
            if material in self.materials.keys():
                self.materials[material] -= item_s_take
            else:
                self.materials[material] = item_s_take

            self.tidy_materials()

            self.total_load -= item_s_take
            
        return {material:item_s_take}

    def tidy_materials(self):
        for k,i in zip(self.materials.keys(),self.materials.values()):
            if i==0:
                self.materials = removekey(self.materials,k)
        
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

    def get_content(self):
        return self.materials
        # return [(k,v) for k,v in zip(self.materials.keys(),self.materials.values())]



class Miner:
    '''
    Miners produce self.mining_speed items per second of a given material. 
    They have attributes for modules and science upgrades.
    '''
    def __init__(self,tech,material,lvl=1):
        self.objectType = self.__class__.__name__
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
        # return (self.material,self.mining_speed)
        return {self.material:self.mining_speed}
        


class Module:
    def __init__(self,tech,lvl):
        self.objectType = self.__class__.__name__
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
    A class for taking item_s items per second away from something (e.g. belt) of some material and putting it in a factory, another belt, or chest.
    '''
    def __init__(self,tech,lvl):

        self.objectType = self.__class__.__name__
        self.type = tech
        self.lvl = lvl
        self.set_speed()
        self.sourceObj = None
        # self.input_rate_max = 0 #cannot take any material if not connected to source object
    
    def set_speed(self):
        if self.type=='burner':
            if self.lvl==1:
                self.item_s_chest_to_chest = 0.60
                self.item_s_chest_to_belt_yellow = 0.60
                self.item_s_chest_to_belt_red = 0.60
                self.item_s_chest_to_belt_blue = 0.60
            if (self.lvl>=2)&(self.lvl<7):
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
            if (self.lvl>=2)&(self.lvl<7):
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
            if (self.lvl>=2)&(self.lvl<7):
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
            if (self.lvl>=2)&(self.lvl<7):
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

            if self.lvl==2: # fix this! implement the remaining lvls for stack inserters

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
        if self.sourceObj.objectType == 'Belt':
            self.input_rate_max = self.sourceObj.get_content()[material] #item / s of material
            self.input_type = 'Belt.'+self.sourceObj.type #what colour?
        if self.sourceObj.objectType == 'Miner':
            self.input_rate_max = self.sourceObj.get_output()[material] #item / s of material
            self.input_type = 'Chest'
        if self.sourceObj.objectType == 'Factory':
            # set_trace()
            self.input_rate_max = self.sourceObj.get_output()[material] #item / s of material
            self.input_type = 'Factory'

    def get_output_max(self,material,output_type='Factory'):
        if output_type in ['Chest','Factory']:
            if self.input_type in ['Chest','Factory']:
                self.output_max = min(self.item_s_chest_to_chest,self.input_rate_max)
            elif self.input_type.split('.')[0]=='Belt':
                if self.input_type.split('.')[1]=='yellow':
                    self.output_max = min(self.item_s_chest_to_belt_yellow,self.input_rate_max)
                elif self.input_type.split('.')[1]=='red':
                    self.output_max = min(self.item_s_chest_to_belt_red,self.input_rate_max)
                elif self.input_type.split('.')[1]=='blue':
                    self.output_max = min(self.item_s_chest_to_belt_blue,self.input_rate_max)
        else:
            print('{} not a valid output location'.format(output_type))
        return self.output_max
        
    def take_materials(self,materials): #materials is {material:item_s}
        if self.sourceObj.objectType == 'Belt':
            IO = self.sourceObj.unload(materials)
        elif self.sourceObj.objectType == 'Chest':
            IO = self.sourceObj.unload(materials)
        elif self.sourceObj.objectType == 'Factory':
            IO = self.sourceObj.unload(materials)
        return IO

class Chest:
    '''
    A class to store materials. Assume infinite input capacity. Assume has same output capacity as it has input.
    '''
    def __init__(self):
        self.objectType = self.__class__.__name__
        self.materials = {}

    def tidy_materials(self):
        for k,i in zip(self.materials.keys(),self.materials.values()):
            if i==0:
                self.materials = removekey(self.materials,k)

    def set_input(self,materials): # should be turned into "add"
        self.materials = materials

    def _check_balance(self,item_s,material):
        if not material in self.materials.keys():
            print('{} not in the chest'.format(material))
            return 0
        if self.materials[material] - item_s > 0:
            item_s_take = item_s
        else:
            item_s_take = self.materials[material]
        return item_s_take

    def add_input(self,materials):
        '''
        Adds item_s items per second of some material to the chest
        '''
        if len(materials)>1:
            raise Exception('you can only load one material at the time!')

        material,item_s = [*materials.keys()][0],[*materials.values()][0]
        if item_s_add > 0:
            if material in self.materials.keys():
                self.materials[material] += item_s_add
            else:
                self.materials[material] = item_s_add
            self.total_load += item_s_add

    def unload(self,materials):
        '''
        Removes item_s items per second of some material from the chest.
        It checks if the material is present. It takes no more material than is available.
        '''
        if len(materials)>1:
            raise Exception('you can only load one material at the time!')
        material,item_s = [*materials.keys()][0],[*materials.values()][0]
        item_s_take = self._check_balance(item_s,material,action='unload')
        if item_s_take > 0:
            if material in self.materials.keys():
                self.materials[material] -= item_s_take
            else:
                self.materials[material] = item_s_take

            self.tidy_materials()

            self.total_load -= item_s_take
            
        return {material:item_s_take}


class Factory:
    '''
    A generic class for (input - wait - ouput) kind of systems.
    Input is managed by Inserters or Miners.
    In the case of Miners the output of a miner, use miner.get_output() and use as input for the factory.
    In case of Inserters, link the inserter to the factory (add inserter to input list). Also link the factory to the inserter.
    '''
    def __init__(self,recipe,prod_speed):
        self.objectType = self.__class__.__name__
        # self.objID = 

        self.name = recipe.name
        
        self.materials_in_max = recipe.materials_in # on the form [(material1,number1),(material2,number2)] #obs not item / s
        self.materials_out_max = recipe.materials_out # on the form [(material1,number1),(material2,number2)] #obs not item / s
        self.base_wait = recipe.wait

        self.prod_speed = prod_speed
        self.wait = self.base_wait/self.prod_speed
        
        self.modules = []

        self.input_max = {m:items/self.wait for m,items in self.materials_in_max.items()} #zip(self.materials_in_max.keys(),self.materials_in_max.values())}
        self.output_max = {m:items/self.wait for m,items in self.materials_out_max.items()} #zip(self.materials_out_max.keys(),self.materials_out_max.values())}

        self.productionScaling = 1 #used to modify input and output if lacking resources

        self.output = None


    def _calc_ProdScale(self):
        '''
        loop over all materials. Loop over input sources. Save list of input sources with the requested material and their respective rates. 
        check what percentual coverage they have of max rate required by factory. Do this for all materials. 
        Get total rate scale parameter of available/required resources. 
        One input source can currently only yield one type of material!
        '''
        self.productionScaling = 1
        inputs = []
        for material in self.materials_in_max.keys():
            sourceList = []
            for inObj in self.inputObjects:
                if inObj.objectType == 'Inserter': #the only relevant input type for now. Fluids to be added at some point
                    input_i = inObj.get_output_max(material,output_type='Factory')
                    sourceList.append(input_i)

            tot_input_material_i = np.sum(sourceList) #total rate of input materials available
            input_required_material_i = self.input_max[material] #total required rate for maximal production
            # compare the two
            if tot_input_material_i>=input_required_material_i:
                self.productionScaling = self.productionScaling
                # print('-----')
                # print('{} has enough materials in for maximal production'.format(material))
                # print('-----')
            else:
                scaling = float(tot_input_material_i)/float(input_required_material_i)
                self.productionScaling = min(self.productionScaling,scaling)
                print('-----')
                print('{} requires {} input but only {} is available. Scaling production by factor {}'.format(material,input_required_material_i,tot_input_material_i,scaling))
                print('-----')
        # print('Report for factory {}, producing {}'.format(self.name,[*self.materials_out_max.keys()]))
        # print('I/O scaled by factor of {}'.format(self.productionScaling))
        # print('-----')


    def set_factory_io(self,inputObjects,outputObjects):

        self.inputObjects = inputObjects # list of e.g. Inserters
        self.outputObjects = outputObjects # list of e.g. Inserters

    def _calc_relative_inputScale(self,material,inputObjects):
        sourceList = []
        for inObj in inputObjects:
            if inObj.objectType == 'Inserter': #the only relevant input type for now. Fluids to be added at some point
                input_i = inObj.get_output_max(material,output_type='Factory')
                sourceList.append(input_i)
        Input_relScale = {inObj:inObj.get_output_max(material,output_type='Factory')/max(sourceList) for inObj in inputObjects} #this is the relative amount taken from the respective input sources. Maybe change from using the object itself as key to its name
        return Input_relScale

    def produce(self):
        if not self.output:
            self._calc_ProdScale()
            for material,item_s_max in self.input_max.items():
                Input_relScale = self._calc_relative_inputScale(material,self.inputObjects) # the rule is that each input source only yields one type of material!

                # collect material from each inObj
                for inObj in self.inputObjects:
                    # set_trace()
                    take_rate = Input_relScale[inObj]*inObj.get_output_max(material,output_type='Factory')#calculate rate by which to get material #item_s

                    materials = {material:take_rate}
                    
                    inObj.take_materials(materials) # actually take material from source

            # print(self.output_max)
            # print(self.productionScaling)
            self.output = {material:item_s_max*self.productionScaling for material,item_s_max in self.output_max.items()}

            # for material,item_s in self.input_max.items():
                # for inObj in self.inputObjects:
                    # inObj.take_materials({material:item_s*self.productionScaling}) # actually take material from source

        else:
            print('factory already producing!')

    def _check_balance(self,item_s,material):
        if not material in self.output.keys():
            print('{} not in factory {}'.format(material,self.name))
            return 0
        if self.output[material] - item_s > 0:
            item_s_take = item_s
        else:
            item_s_take = self.output[material]
        return item_s_take

    def tidy_output(self):
        for k,i in zip(self.output.keys(),self.output.values()):
            if i==0:
                self.output = removekey(self.output,k)

    def unload(self,materials):
        '''
        Removes item_s items per second of some material from the factory.
        It checks if the material is present. It takes no more material than is available.
        '''
        if len(materials)>1:
            raise Exception('you can only unload one material at the time!')
        material,item_s = [*materials.keys()][0],[*materials.values()][0]
        item_s_take = self._check_balance(item_s,material)
        if item_s_take > 0:
            if material in self.output.keys():
                self.output[material] -= item_s_take
            else:
                self.output[material] = item_s_take

            self.tidy_output()
            
        return {material,item_s_take}


    def get_output(self):
        if not self.output:
            self._calc_ProdScale()
            output = {material:item_s_max*self.productionScaling for material,item_s_max in self.output_max.items()}
            return output
        else:
            return self.output


class Recipe:
    def __init__(self):
        self.objectType = self.__class__.__name__

    def create_recipe(self,name,materials_in,wait,materials_out):
        self.name = name
        self.materials_in = materials_in
        self.wait = wait
        self.materials_out = materials_out



# 