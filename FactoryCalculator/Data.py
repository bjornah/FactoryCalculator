import pandas as pd

# amount of kJ per consumed (burned) entity of the given material
FuelDict = {'wood':2e3,
            'coal':4e3,
            'solid':12e3,
            'rocket':100e3,
            'nuclear':1.21e6,
            'uranium':8e6}

# energy consumption in kW from different smelters/furnaces
SmelterPower = {'stoneSmelter':90,
                 'steelSmelter':90,
                 'electricSmelter':180}

# Production speed factor of different smelters/furnaces
SmelterProdSpeed = {'stoneSmelter':1,
                    'steelSmelter':2,
                    'electricSmelter':2}

FurnaceRecipes = {'iron-plate':{'name':'iron-plate',
                                'materials_in':{'iron-ore':1},
                                'wait':3.2,
                                'materials_out':{'iron-plate':1}
                                },
                'copper-plate':{'name':'copper-plate',
                                'materials_in':{'copper-ore':1},
                                'wait':3.2,
                                'materials_out':{'copper-plate':1}
                                },
                'stone-brick':{'name':'stone-brick',
                                'materials_in':{'stone-ore':2},
                                'wait':3.2,
                                'materials_out':{'stone-brick':1}
                                },
                'steel-plate':{'name':'steel-plate',
                                'materials_in':{'iron-plate':5},
                                'wait':16,
                                'materials_out':{'steel-plate':1}
                                }
                }

Inserters = {
            'burner':{
                    1:{
                    'item_s_chest_to_chest':0.60,
                    'item_s_chest_to_belt_yellow':0.60,
                    'item_s_chest_to_belt_red':0.60,
                    'item_s_chest_to_belt_blue':0.60
                    },
                    2:{
                    'item_s_chest_to_chest':1.20,
                    'item_s_chest_to_belt_yellow':1.19,
                    'item_s_chest_to_belt_red':1.19,
                    'item_s_chest_to_belt_blue':1.19
                    },
                    7:{
                    'item_s_chest_to_chest':0.83,
                    'item_s_chest_to_belt_yellow':0.83,
                    'item_s_chest_to_belt_red':0.83,
                    'item_s_chest_to_belt_blue':0.83
                    }
                },
            'regular':{
                    1:{
                    'item_s_chest_to_chest':1.20,
                    'item_s_chest_to_belt_yellow':1.20,
                    'item_s_chest_to_belt_red':1.20,
                    'item_s_chest_to_belt_blue':1.20
                    }
                }
            }

        #     if (self.lvl>=2)&(self.lvl<7):
        #         self.item_s_chest_to_chest = 1.67
        #         self.item_s_chest_to_belt_yellow = 1.64
        #         self.item_s_chest_to_belt_red = 1.64
        #         self.item_s_chest_to_belt_blue = 1.64
        #     if self.lvl==7:
        #         self.item_s_chest_to_chest = 2.50 
        #         self.item_s_chest_to_belt_yellow = 2.25
        #         self.item_s_chest_to_belt_red = 2.37
        #         self.item_s_chest_to_belt_blue = 2.43
        # elif self.type=='long':
        #     if self.lvl==1:
        #         self.item_s_chest_to_chest = 1.20
        #         self.item_s_chest_to_belt_yellow = 1.20
        #         self.item_s_chest_to_belt_red = 1.20
        #         self.item_s_chest_to_belt_blue = 1.20
        #     if (self.lvl>=2)&(self.lvl<7):
        #         self.item_s_chest_to_chest = 2.40
        #         self.item_s_chest_to_belt_yellow = 2.35
        #         self.item_s_chest_to_belt_red = 2.35
        #         self.item_s_chest_to_belt_blue = 2.35
        #     if self.lvl==7:
        #         self.item_s_chest_to_chest = 3.60
        #         self.item_s_chest_to_belt_yellow = 3.10
        #         self.item_s_chest_to_belt_red = 3.33
        #         self.item_s_chest_to_belt_blue = 3.46
        # elif self.type=='fast': #same as filter inserters
        #     if self.lvl==1:
        #         self.item_s_chest_to_chest = 2.31 
        #         self.item_s_chest_to_belt_yellow = 2.31 
        #         self.item_s_chest_to_belt_red = 2.31 
        #         self.item_s_chest_to_belt_blue = 2.31 
        #     if (self.lvl>=2)&(self.lvl<7):
        #         self.item_s_chest_to_chest = 4.62
        #         self.item_s_chest_to_belt_yellow = 4.44
        #         self.item_s_chest_to_belt_red = 4.44
        #         self.item_s_chest_to_belt_blue = 4.44
        #     if self.lvl==7:
        #         self.item_s_chest_to_chest = 6.92
        #         self.item_s_chest_to_belt_yellow = 5.29
        #         self.item_s_chest_to_belt_red = 6.00
        #         self.item_s_chest_to_belt_blue = 6.43
        # elif self.type=='stack':
        #     if self.lvl==1:
        #         self.item_s_chest_to_chest = 4.62
        #         self.item_s_chest_to_belt_yellow = 4.44
        #         self.item_s_chest_to_belt_red = 4.44
        #         self.item_s_chest_to_belt_blue = 4.44

        #     if self.lvl==2: # fix this! implement the remaining lvls for stack inserters

        #         self.item_s_chest_to_chest = 9.23
        #         self.item_s_chest_to_belt_yellow = 5.71
        #         self.item_s_chest_to_belt_red = 7.06
        #         self.item_s_chest_to_belt_blue = 7.74
        #     if self.lvl==7:
        #         self.item_s_chest_to_chest = 27.69
        #         self.item_s_chest_to_belt_yellow = 6.79
        #         self.item_s_chest_to_belt_red = 10.91
        #         self.item_s_chest_to_belt_blue = 13.85