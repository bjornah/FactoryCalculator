def test_Belt():
    '''
    This test should be improved
    '''
    # checks loading
    b = Belt('yellow')
    b.load('iron',10)
    b.load('copper',2)
    assert (b.materials=={'copper': 2, 'iron': 10})
    assert (b.total_load==12)
    
    b.unload('iron',5) # redundancy?
    b.unload('copper',3) # tests that we cannot take away more than we have
    assert (b.materials=={'iron': 5}) # tests that copper has been removed from the dictionary

    b.unload('iron',15) #checks that we unload all there is and that the dictionary is then empty
    
    assert (b.materials=={})
    assert (b.total_load==0)

def test_Miner():
    sMod1 = Module('speed',1)
    sMod2 = Module('speed',2)
    sMod3 = Module('speed',3)
    miner = Miner('electric',material='iron',lvl=3)
    miner.add_modules([sMod1,sMod2])
    miner.mining_base_speed
    miner.mining_speed
    