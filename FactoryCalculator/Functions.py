import numpy as np

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
            item_s_available = availability_rate_dict[input_obj] # how much item / s is available in this input object
            input_rate = input_rate_dict[input_obj] # how much material can get transfered to f from this input object
            Input_relScale[input_obj] = input_rate/input_i # how much of the total available number of this material this particular source corresponds to
            if input_obj.objectType=='Factory':
                if item_s_available>0:
                    input_obj.productionScaling = min(input_obj.productionScaling,Input_relScale[input_obj]*item_s_requested/item_s_available)
        f.input_unload_dict[material] = {input_obj:Input_relScale[input_obj]*item_s_requested for input_obj in inputObjs}
        
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
    
def unload_materials(f):
    '''
    This unloads materials from all *sources*, i.e. not factories. 
    This includes belts, chests, miners, minerlists. Eventually this must also include fluid storage tanks, pipes and possibly trains
    Pass the actual factory object as f. 
    It needs to have its inputs and output set.
    Needs to have run calculate_productionScaling() already to a point where equilibrium is reached for all involved factories
    '''
    for input_obj,input_name,input_TopSpeed in f.inputList: # iterate over all input objects
        if input_obj.objectType in ['Belt','Chest']:
            for material in f.input_adjusted.keys(): # what the requested number of item/s is for each material requested
                unload_val = f.input_unload_dict[material][input_obj]
                if unload_val>0:
                    print('{} takes {} {} from {}'.format(f.objID,unload_val,material,input_name))
                    unload_dict = {material:unload_val}
                    input_obj.unload(unload_dict)