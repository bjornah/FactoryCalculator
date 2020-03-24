import functools
# from IPython.core.debugger import set_trace
# from FactoryCalculator import Data
# from FactoryCalculator.Entities import Recipe
from FactoryCalculator.Entities import Recipe

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

def removekey(d,key):
    r = dict(d)
    del r[key]
    return r

def convertRecipe(recipeDict):
    recipe = Recipe()
    recipe.create_recipe(name=recipeDict['name'],
                        materials_in=recipeDict['materials_in'],
                        wait=recipeDict['wait'],
                        materials_out=recipeDict['materials_out'])
    return recipe
