# -*- coding:utf-8 -*-

from .module import *

class ModuleHeal(Module):
    _initTriList = (
        TriggerDefinition('jing', r'^[> ]*你全身放松，运转真气进行疗伤。$', '_onJing', 1),
        TriggerDefinition('jing_ok', r'^[> ]*你根本就没有受伤，疗什么伤啊！', '_onJingOK', 1),
        TriggerDefinition('qi_fail', r'^[> ]*你已经受伤过重，只怕一运真气便有生命危险！', '_onFail', 1),
        TriggerDefinition('low_neili', r'^[> ]*你的真气不够', '_onFail', 1),
        )
    
    def __init__(self, owner, modulename='heal', **options):
        super().__init__(owner, modulename, **options)
        
        self._Hpbrief = owner._triggers["hpbrief"]
        
        # create the alias for user.
        self._alias = Alias(self, self._group, r'^liao$', self._aliasFunction, name='liaoshang')
    
    def _aliasFunction(self, sender, args):
        self.Start()
    
    def _onJing(self, sender, args):
        self.mush.DoAfter(0.2, 'exert inspire')

    def _onJingOK(self, sender, args):
        self._triggers['jing'].Enabled = False
        # self._triggers['jing_ok'].RemoveCallback(self._onJingOK)
        
        self._Hpbrief.AddCallback(self._check_qi)
        self.mush.Execute('hpbrief')
        
    def _onFail(self, sender, args):
        self._Hpbrief.RemoveCallback(self._check_qi)
        self.mush.Warning('疗伤失败，原因：气过少或内力过低，建议fullme')
        self.Enabled = False
        self.mush.Execute('response heal fail')
        
        self._doEvent('AfterFail')
    
    def _check_qi(self, sender, args):  
        hp = args
        if hp['neili'] < 100:            
            self._onQiFail(sender, args)
        else:
            if hp['qimax'] < hp['qitotal']:
                self.mush.Execute('exert heal')
                self.mush.Execute('exert heal')
                self.mush.DoAfter(0.5, 'hpbrief')
            else:
                self._Hpbrief.RemoveCallback(self._check_qi)
                self.Enabled = False
                print('疗伤完成＿')

                self.mush.Execute('response heal done')
                self._doEvent('AfterDone')     
    
    def Start(self, **options):
        self.Enabled = True
        self.mush.Execute('exert inspire')