# -*- coding:utf-8 -*-

import random
from .module import *

class ModuleFood(Module):
    _initTriList = (
        TriggerDefinition('eat_none', r'你将剩下的.*吃得干干净净', '_onEatNone', 1),
        TriggerDefinition('eat_next', r'你拿起.*咬了几口。', '_onEatNext', 1),
        TriggerDefinition('eat_done', r'你已经吃太饱了，再也塞不下任何东西了', '_onEatDone', 1),
        TriggerDefinition('drink_none', r'你已经将.*里的.*喝得一滴也不剩了', '_onDrinkNone', 1),
        TriggerDefinition('drink_next', r'你拿起.*咕噜噜地喝了几口清水。.*', '_onDrinkNext', 1),
        TriggerDefinition('drink_done', r'你已经喝太多了，再也灌不下一滴水了', '_onDrinkDone', 1),
        )
    
    def __init__(self, owner, modulename='food', **options):
        super().__init__(owner, modulename, **options)
        
        self.Inventory = owner.Commands["inventory"]
        self.food = []
        self.water = []
        
        # create the alias for user.
        self._alias = Alias(self, self._group, r'^chi$|^he$|^feed$', self._aliasFunction, name='food')
    
    def _aliasFunction(self, sender, args):
        self.Start()      
        
    def _onEatNone(self, sender, args):
        self._cur_food.count -= 1
        if self._cur_food.count <= 0:
            self.food.remove(self._cur_food)
        self._eat()
        
    def _onEatNext(self, sender, args):
        self.mush.Execute('eat ' + self._cur_food.id)
        
    def _onEatDone(self, sender, args):
        self._mode = "drink"
        self._drink()

    def _onDrinkNone(self, sender, args):
        self._cur_water.count -= 1
        if self._cur_water.count <= 0:
            self.water.remove(self._cur_water)
            
        self._drink()
        
    def _onDrinkNext(self, sender, args):
        self.mush.Execute('drink ' + self._cur_water.id)
        
    def _onDrinkDone(self, sender, args):
        self.Enabled = False
        
        msg_eat = '没吃饱' if self._nofood else '吃饱了'
        msg_drink = '没喝足' if self._nowater else '喝足了'
        print('module [eat&drink]: {} {}'.format(msg_eat, msg_drink))
        
        self._doEvent('AfterDone') 
        
    def _eat(self):
        if len(self.food) > 0:
            self._cur_food = random.choice(self.food)
            self.mush.Execute('eat ' + self._cur_food.id)
        else:
            self.Inventory.AfterDone = self._afterCheckThings
            self.Inventory.Execute()
    
    def _drink(self):
        if len(self.water) > 0:
            self._cur_water = random.choice(self.water)
            self.mush.Execute('drink ' + self._cur_water.id)
        else:
            # self.Inventory.AfterDone = self._afterCheckThings
            # self.Inventory.Execute()    
            pass
    
    def _afterCheckThings(self, sender, args):
        if args.state == CommandState.Success:
            self.Inventory.AfterDone = None
            self.food = args.result["food"]
            self.water = args.result["water"]
            
            if self._mode == 'eat':
                if len(self.food) > 0:
                    self._eat()
                else:
                    # no food, record and 
                    self._nofood = True
                    self._mode = 'drink'
                    
            if self._mode == 'drink':
                if len(self.water) > 0:
                    self._drink()
                else:
                    self._nowater = True
                    self._mode = 'done'
                    self._onDrinkDone(None)

    def Start(self, **options):
        self.Enabled = True
        self._mode = 'eat'
        self._nofood = False
        self._nowater = False
        
        self.Inventory.AfterDone = self._afterCheckThings
        self.Inventory.Execute()