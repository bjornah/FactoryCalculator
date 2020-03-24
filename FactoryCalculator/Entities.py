import numpy as np
from IPython.core.debugger import set_trace
from FactoryCalculator import Data
from FactoryCalculator.Utils import add_dicts,removekey
from copy import copy
import sys

class Belt:
    '''
    belts can carry x items/second (x item_s). They do so over two lanes.
    A belt has property of carrying x_i item_s_i for any i=0,1,2...
    When adding a new material, specify material and item_s_i. This is added to the extend 
    that sum_i item_s_i \leq max_load
    '''
    def __init__(self, colour,objID=None):
        self.objectType = self.__class__.__name__
        self.set_type(colour)
        self.materials = {} #dict of material:item_s
        self.total_load = 0
        self.loadingStations = []
        self.unloadingStations = []
        self.objID = objID
        
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
            self.loadingStations.append({material:'{}/{}'.format(item_s_add,item_s)})
        
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
            self.unloadingStations.append({material:item_s_take})
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
    def __init__(self,tech,material,lvl=1,objID=None):
        self.objectType = self.__class__.__name__
        self.mining_base_speed,self.module_slots = self.set_type(tech)
        self.material = material
        self.modules = []
        self.lvl=lvl
        self.lvl_prod_bonus = self.get_miner_lvl_bonus()
        self.mining_speed = self.update_mining_speed()
        self.objID = objID
            
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
    
    # This function must be removed. lvl of miners are not a thing. The mining technology affects the size of mining patches, not the speed!
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
        

class Chest:
    '''
    A class to store materials. Assume infinite input capacity. 
    Assume it can output the same capacity that it has as total input. 
    i.e. if 1 iron-plate / s is being loaded into is, you can withdraw no more than 1 iron-plate / s.
    '''
    def __init__(self,objID=None):
        self.objectType = self.__class__.__name__
        self.materials = {}
        self.objID=objID
        self.total_load = 0

    def tidy_materials(self):
        for k,i in zip(self.materials.keys(),self.materials.values()):
            if i==0:
                self.materials = removekey(self.materials,k)

    # def set_input(self,materials): # should be turned into "add"
        # self.materials = materials

    def _check_balance(self,item_s,material):
        if not material in self.materials.keys():
            print('{} not in the chest'.format(material))
            return 0
        if self.materials[material] - item_s > 0:
            item_s_take = item_s
        else:
            item_s_take = self.materials[material]
        return item_s_take

    def load(self,materials):
        '''
        Adds item_s items per second of some material to the chest
        '''
        if len(materials)>1:
            raise Exception('you can only load one material at the time!')

        material,item_s = [*materials.keys()][0],[*materials.values()][0]
        if item_s > 0:
            if material in self.materials.keys():
                self.materials[material] += item_s
            else:
                self.materials[material] = item_s
            self.total_load += item_s

    def unload(self,materials):
        '''
        Removes item_s items per second of some material from the chest.
        It checks if the material is present. 
        It takes no more material than is available.
        '''
        if len(materials)>1:
            raise Exception('you can only load one material at the time!')
        material,item_s = [*materials.keys()][0],[*materials.values()][0]
        item_s_take = self._check_balance(item_s,material)
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
    In the case of Miners the output of a miner, use miner.get_output() and use as input for the factory.
    In case of Inserters, link the inserter to the factory (add inserter to input list). Also link the factory to the inserter.
    '''
    def __init__(self,recipe,prod_speed,FactoryType,objID=None,fuel=None):
        self.objectType = self.__class__.__name__
        self.objID = objID

        self.FactoryType = FactoryType
        self.fuel = fuel
        self.Basepower = self._set_BasePower()
        self.base_wait = recipe.wait
        self.prod_speed = prod_speed #self._set_prod_speed()
        self.wait = self.base_wait/self.prod_speed

        self._calc_FuelConsumption() # in terms of fuel quantity per second
        if self.fuelConsumption_s > 0:
            recipe.add_fuelCost({self.fuel:self.fuelConsumption_s})

        self.effectiveRecipe = recipe
        self.name = recipe.name
        
        self.materials_in_max = recipe.materials_in # on the form [(material1,number1),(material2,number2)] #obs not item / s
        self.materials_out_max = recipe.materials_out # on the form [(material1,number1),(material2,number2)] #obs not item / s

        self.input_max = {m:items/self.wait for m,items in self.materials_in_max.items()} #zip(self.materials_in_max.keys(),self.materials_in_max.values())}
        self.output_max = {m:items/self.wait for m,items in self.materials_out_max.items()} #zip(self.materials_out_max.keys(),self.materials_out_max.values())}

        # So far nothing is controversial or dependent on any other part of the essembly
        # This is just a statement of facts about the recipe and the type of factory being used

        self.inputList = [] # This is to be a set of links to other objects from which we gather material
        self.outputDestination = None # This is where we put the output

        # self.modules = []

        self.productionScaling = 1 #used to modify input and output if lacking resources

        self.input_adjusted = copy(self.input_max)
        self.output_adjusted = copy(self.output_max)

        self.output_total = None # self.output_max*self.productionScaling # This is how much is produces under the current production speed
        # self.store = None # the amount of residual material/s after production has been initated. This should always be zero once the material is transported elsewhere
        self.input_unload_dict = {} # This is a dict of the form {material:{input_obj_i:item_s}}. Note that it does not contain data on material that is collected directly from a factory. This can be called upon when it is time to unload material from sources

        self.bottlenecks = []

    def reset_scales(self):
    	self.productionScaling = 1
    	self.input_adjusted = copy(self.input_max)
    	self.output_total = None

    def add_bottleneck(self,material):
    	self.bottlenecks.append(material)

    def _set_BasePower(self):
        '''
        Sets the energy consumption based on if the smelter is a stone, steel or electric furnace
        '''
        if not self.fuel:
            return 0
        try:
            BasePower = Data.SmelterPower[self.SmelterType]
        except:
            try:
                print('no such smelter name. Acceptable SmelterTypes are {}'.format(Data.SmelterProdSpeed.keys()))
                raise
            except:
                print('There appears to be some error in Data.py regarding the smelter dictionary')
                raise
        return BasePower

    def _set_prod_speed(self):
        '''
        Sets the production speed factor based on if the smelter is a stone, steel or electric furnace
        '''
        try:
            prod_speed = Data.SmelterProdSpeed[self.SmelterType]
        except:
            try:
                print('no such smelter name. Acceptable SmelterTypes are {}'.format(Data.SmelterProdSpeed.keys()))
                raise
            except:
                print('There appears to be some error in Data.py regarding the smelter dictionary')
                raise
        return prod_speed

    def _calc_FuelConsumption(self):
        '''
        calculate fuel consumption.
        - get fuel energy content based on fuel type.
        - actual energy consumption (base power * production scaling) is calculated when producing
        - fuel consumption rate is calculated as power/fuelEnergyContent * waitTime
        '''
        # self.power = self.Basepower*self.productionScaling
        if not self.fuel:
            print('No fuel present!')
            self.fuelConsumption_s = 0
        else:
            self.fuelConsumption_s = self.Basepower/Data.FuelDict[self.fuel]*self.wait

    # def _calc_ProdScale(self):
    #     '''
    #     loop over all materials. Loop over input sources. Save list of input sources with the requested material and their respective rates. 
    #     check what percentual coverage they have of max rate required by factory. Do this for all materials. 
    #     Get total rate scale parameter of available/required resources. 
    #     One input source can currently only yield one type of material!
    #     '''
    #     self.productionScaling = 1
    #     # inputs = []
    #     for material in self.materials_in_max.keys():
    #         sourceList = []
    #         for inObj in self.inputObjects:
    #             if inObj.objectType == 'Inserter': #the only relevant input type for now. Fluids to be added at some point
    #                 input_i = inObj.get_output_max(material,output_type='Factory')
    #                 sourceList.append(input_i)

    #         tot_input_material_i = np.sum(sourceList) #total rate of input materials available
    #         input_required_material_i = self.input_max[material] #total required rate for maximal production
    #         # compare the two
    #         if tot_input_material_i>=input_required_material_i:
    #             self.productionScaling = self.productionScaling
    #             # print('-----')
    #             # print('{} has enough materials in for maximal production'.format(material))
    #             # print('-----')
    #         else:
    #             scaling = float(tot_input_material_i)/float(input_required_material_i)
    #             self.productionScaling = min(self.productionScaling,scaling)
    #             print('-----')
    #             print('{} requires {} input but only {} is available. Scaling production by factor {}'.format(material,input_required_material_i,tot_input_material_i,scaling))
    #             print('-----')
    #     # print('Report for factory {}, producing {}'.format(self.name,[*self.materials_out_max.keys()]))
        # print('I/O scaled by factor of {}'.format(self.productionScaling))
        # print('-----')

    # def adjust_ProdScale_output(self):
    #     '''
    #     Adjusts prodscale based on output requirement. 
    #     i.e. how much is requested from connected factory, and how fast 
    #     can inserters move the output.
    #     In practice this means that if there is a surplus of output, we scale the output until
    #     there is no surplus (i.e. self.store = 0)
    #     '''
    #     for material,item_s_max in self.output_total.items():
    #         if material in self.store.keys():
    #             self.productionScaling = (self.output_total[material]-self.store[material])/self.output_total[material]
    #             print('Rescaling production to a speed of {}'.format(self.productionScaling)) 
    #     return

    def clear_IO(self):
    	self.inputList = []
    	self.outputDestination = None

    def addInput(self,inputObj,Inserter_speed):
        self.inputList.append((inputObj,inputObj.objID,Inserter_speed))

    def addOutput(self,outputObj,Inserter_speed):
        self.outputDestination = (outputObj,outputObj.objID,Inserter_speed)

    # def _calc_relative_inputScale(self,material,inputObjects):
    #     sourceList = []
    #     for inObj in inputObjects:
    #         if inObj.objectType == 'Inserter': #the only relevant input type for now. Fluids to be added at some point
    #             input_i = inObj.get_output_max(material,output_type='Factory')
    #             sourceList.append(input_i)
    #     Input_relScale = {inObj:inObj.get_output_max(material,output_type='Factory')/max(sourceList) for inObj in inputObjects} #this is the relative amount taken from the respective input sources. Maybe change from using the object itself as key to its name
    #     return Input_relScale

    def produce(self):
        if not self.output_total:
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
            output_total = {material:item_s_max*self.productionScaling for material,item_s_max in self.output_max.items()}
            self.output_total = output_total
            self.store = copy(output_total)
            # for material,item_s in self.input_max.items():
                # for inObj in self.inputObjects:
                    # inObj.take_materials({material:item_s*self.productionScaling}) # actually take material from source

        else:
            print('factory already producing!')

    def _check_balance(self,item_s,material):
        if not material in self.store.keys():
            print('{} not in factory {}'.format(material,self.name))
            return 0
        if self.store[material] - item_s > 0:
            item_s_take = item_s
        else:
            item_s_take = self.store[material]
        # print(item_s_take)
        # print(self.store)
        return item_s_take

    def tidy_output(self):
        for k,i in zip(self.store.keys(),self.store.values()):
            if i==0:
                self.store = removekey(self.store,k)

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
            if material in self.store.keys():
                self.store[material] -= item_s_take
            else:
                self.store[material] = item_s_take

            self.tidy_output()
        return {material,item_s_take}


    def get_output_adjusted(self):
        # if not self.output_total:
            # self._calc_ProdScale()
        output_total = {material:item_s_max*self.productionScaling for material,item_s_max in self.output_max.items()}
        return output_total
        # else:
            # return self.output_total

    def get_input(self):
        if not self.output_total:
            self._calc_ProdScale()        
        input = {material:item_s_max*self.productionScaling for material,item_s_max in self.input_max.items()}
        return input


class Recipe:
    def __init__(self):
        self.objectType = self.__class__.__name__

    def create_recipe(self,name,materials_in,wait,materials_out):
        self.name = name
        self.materials_in = materials_in
        self.wait = wait
        self.materials_out = materials_out

    def add_fuelCost(self,fuelCost):
        '''
        Adds a fuel cost as {fuelType:item_s}. 
        This has been scaled in Smelter (for example) to correspond to the actual production rate
        The fuel cost is calculated in Smelter._calc_fuelConsumption()
        '''
        self.materials_in = Utils.add_dicts([self.materials_in,fuelCost])
