# -*- coding:utf-8 -*-

from .module import *

class ModuleSaveMoney(Module):
    # TODO: Replace the error chinese code. 
    _initTriList = (
        TriggerDefinition('busy', r'^[> ]*\S*说道：「哟，抱歉啊，我这儿正忙着呢……您请稍候。」', '_onRetry', 1),
        TriggerDefinition('ok', r'^[> ]*你拿出.*，存进了银号。', '_onNext', 1),
        )
                 
    def __init__(self, owner, modulename='savemoney', **options):
        super().__init__(owner, modulename, **options)
        
        self.Response = owner.Triggers["response"]
        self.Inventory = owner.Commands["inventory"]
        
        # create the alias for user.
        self._alias = Alias(self, self._group, r'^cunqian', self._aliasFunction, name='savemoney')
    
    def _aliasFunction(self, sender, args):
        self.Start()
              
    def _onNext(self, sender, args):
        if self._saved == "cash":
            self._cash = 0
        elif self._saved == "gold":
            self._gold = 0
        elif self._saved == "silver":
            self._silver = 0
        
        if self._cash > 0:
                self._saved = "cash"
                self._cmd_cun = 'deposit {} cash'.format(self._cash)
                self.mush.Execute(self._cmd_cun)    
        elif self._gold > 0:
                self._saved = "gold"
                self._cmd_cun = 'deposit {} gold'.format(self._gold)
                self.mush.Execute(self._cmd_cun)
        elif self._silver >= 100:
                self._saved = "silver"
                self._cmd_cun = 'deposit {} silver'.format((self._silver // 100) * 100)
                self.mush.Execute(self._cmd_cun)
        else:
            self.mush.Log('module [SaveMoney]：存钱完毕')
            self.Enabled = False
            self._doEvent('AfterDone')     

    def _onRetry(self, sender, args):
        self.mush.DoAfter(1, self._cmd_cun)
    
    def _arrived_bank(self, sender, args):
        if args.get('gps', None) == 'ok':
            self.Response.RemoveCallback(self._arrived_bank)
            self.mush.Log('module [SaveMoney]：到达银行，开始存钱...')
            self._onNext(sender, args)
    
    def _afterCheckMoney(self, sender, args):
        if args.state == CommandState.Success:
            self._cash = args.result["cash"]
            self._gold = args.result["gold"]
            self._silver = args.result["silver"]

            if (self._cash > 0) or (self._gold > 0) or (self._silver > 100):
                self.mush.Log('module [SaveMoney]：身上钱折合黄金{:.2f}，不少了，去存一下吧 :)'.format(self._cash * 10 + self._gold + self._silver / 100))
                self.Response.AddCallback(self._arrived_bank)
                self.mush.Execute('rt bank')
            else:
                self.mush.Log('module [SaveMoney]：身上钱折合黄金{:.2f}，这么点钱，就没必要去存了'.format(self._cash * 10 + self._gold + self._silver / 100))
                self.Enabled = False
                self._doEvent('AfterDone')     
                
            self.Inventory.AfterDone = None
    
    def Start(self, **options):
        self.Enabled = True
        self._saved = None
        self.Inventory.AfterDone = self._afterCheckMoney
        self.Inventory.Execute()