# -*- coding:utf-8 -*-

from .module import *

class ModuleSellThings(Module):
    _initTriList = (
        # TriggerDefinition('busy', r'^[> ]*\S*哟，抱歉啊，我这儿正忙着呢……您请稍候。', '_onRetry', 1),
                  )
                 
    def __init__(self, owner, modulename='savemoney', **options):
        super().__init__(owner, modulename, **options)
       
        self.Response = owner.Triggers["response"]
        self.Inventory = owner.Commands["inventory"]
        self.CmdWait = owner.Commands["wait"]
        
        # create the alias for user.
        self._alias = Alias(self, self._group, r'^sellall$', self._aliasFunction, name='sellall')
    
    def _aliasFunction(self, sender, args):
        self.Start()      

    def _onResponseCheck(self, sender, args):
        if args.get('sell', None) == 'check':
            self.Response.RemoveCallback(self._onResponseCheck)
            
            self.Inventory.AfterDone = self._checkThingsAgain
            self.Inventory.Execute()
    
    def _timerWait(self, sender, args):
        if args.state == CommandState.Success:
            if len(self.sells) > 0:
                item = self.sells.pop()
                # self.mush.Execute('sell {}}'.format(item))
                self.mush.Execute('sell {} for {}'.format(item.id, item.count))
                self.CmdWait.Wait(1)
            else:
                self.CmdWait.AfterDone = None
                self.Response.AddCallback(self._onResponseCheck)
                self.mush.Execute('response sell check')
    
    def _checkSells(self):
        if len(self.sells) > 0:
            self.CmdWait.AfterDone = self._timerWait
            self._timerWait(self.CmdWait, CommandState.Success)
        else:
            self.mush.Log('module [SellThings]：身上已经没东西可卖了\n')
            self.Enabled = False
            self._doEvent('AfterDone')      
    
    def _checkThingsAgain(self, sender, args):
        if args.state == CommandState.Success:
            self.Inventory.AfterDone = None
            self.sells = args.result["sells"]
            self._checkSells()
    
    def _arrived_pawnshop(self, mod):
        self._checkSells()
    
    def _afterCheckThings(self, sender, args):
        if args.state == CommandState.Success:
            self.Inventory.AfterDone = None
            
            self.sells = args.result["sells"]
            if len(self.sells) > 0:
                self.mush.Log('module [SellThings]：准备去最近的当铺卖东西!')
                self.owner.RunModule('runto', afterDone=self._arrived_pawnshop, to='pawnshop')
            else:
                self.mush.Log('module [SellThings]：身上已经没东西可卖了')
                self.Enabled = False
                self._doEvent('AfterDone')      
    
    def Start(self, **options):
        self.Enabled = True

        self.Inventory.AfterDone = self._afterCheckThings
        self.Inventory.Execute()
