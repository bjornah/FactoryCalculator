import functools
from IPython.core.debugger import set_trace
# from FactoryCalculator import Data
# from FactoryCalculator.Entities import Recipe
from FactoryCalculator.Entities2 import Recipe

def overview(objs):
    '''
    Takes list of miners, belts and factories. Shows what is produced in miners.
    It shows what is loaded onto each belt, what is unloaded from each belt and what the final state of the belt currently is. 
    It also shows (real, i.e. taking availability and inserters into account) input/output of each factory.
    '''
    belts = [obj for obj in objs if obj.objectType=='Belt']
    miners = [obj for obj in objs if obj.objectType=='Miner']
    factories = [obj for obj in objs if obj.objectType=='Factory']

    print('This is a first, coarse overview of the given objects:\n')

    print('Miners:')
    for miner in miners:
        if miner.objID:
            ID = miner.objID
        else:
            ID = ''
        print('-{} miner {} outputing {}'.format(miner.type,ID,miner.get_output()))
    print('------\n')

    print('Belts:')
    for i,belt in enumerate(belts,1):
        if belt.objID:
            ID = belt.objID
        else:
            ID = ''
        print('-Belt #{} ({}, {}):'.format(i,belt.type,ID))
        for item_s_add_item_s in belt.loadingStations:
            print('{} is loaded onto the belt'.format(item_s_add_item_s))
        for item_s in belt.unloadingStations:
            print('{} is offloaded'.format(item_s))
        # print('belt now contains {} in terms of items per s'.format(belt.get_content()))
        print('final state of belt is that it contains {} in terms of items per s'.format(belt.get_content()))
    print('------\n')

    print('Factories:')
    for factory in factories:
        if factory.objID:
            ID = factory.objID
        else:
            ID = ''
        print('-Factory {} using {} and outputing {}, operating at {:.0f}% speed'.format(ID,factory.get_input(),factory.get_output_total(),factory.productionScaling*100))
    print('------\n')

def add_dicts(dicts):
    '''
    Merges dictionaries such that items are added if they have matching keys. Assumes that items are floats or ints
    '''
    allkeys = functools.reduce(set.union, map(set, map(dict.keys, dicts)))
    c = {}
    for key in allkeys:
        items = 0
        for d in dicts:
            items += d[key] if key in d else 0
            c[key]=items
    return c

def convertRecipe(recipeDict):
    recipe = Recipe()
    recipe.create_recipe(name=recipeDict['name'],
                        materials_in=recipeDict['materials_in'],
                        wait=recipeDict['wait'],
                        materials_out=recipeDict['materials_out'])
    return recipe
