# -*- coding:utf-8 -*-

from .module import *

class ModuleDazuoTo(Module):
    _initTriList = (
        TriggerDefinition('done', r'[> ]*(..\.\.)*你运功完毕，深深吸了口气，站了起来。$', '_onDone', 1),
        TriggerDefinition('noqi', r'^[> ]*你现在的气太少了，无法产生内息运行全身经脉。$', '_onNoQi', 1),
        TriggerDefinition('nojing', r'^[> ]*你现在精不够，无法控制内息的流动！$', '_onNoJing', 1),
        TriggerDefinition('wait', r'^[> ]*你正在运行内功加速全身气血恢复，无法静下心来搬运真气。$', '_onWait', 1),
        TriggerDefinition('halt', r'^[> ]*你把正在运行的真气强行压回丹田，站了起来。|^[> ]*你现在不忙。', '_onStop', 1),
        TriggerDefinition('finish', r'^[> ]*你现在内力接近圆满状态。', '_onDone', 1),
        )
    
    def __init__(self, owner, modulename='dazuoto', **options):
        super().__init__(owner, modulename, **options)
        
        self._forcelevel = 0
        self._dazuo_point = 10
        self._always = False

        # link the useful commands
        self._Effective = owner.Commands['enable']
        self._Hpbrief = owner.Triggers['hpbrief']
        
        # create the alias for user.
        self._alias = Alias(self, self._group, r'^dzt(?:\s+(.*))?$', self._aliasFunction, name='dazuoto')
        
    def _aliasFunction(self, sender, args):
        param = args.wildcards[0]
        if param == 'stop':
            self.mush.Warning('module [dazuoto]: halt manually!')
            self.Stop()
        elif param == '0':
            self.Start(always=True)
        else:
            self.Start(after=param)
    
    def UpdateForceLevel(self):
        if self._forcelevel == 0:
            self._Effective.AfterDone = self._update_forcelevel
            self._Effective.Execute()

    def _update_forcelevel(self, sender, args):
        if args.state == CommandState.Success:
            self._Effective.AfterDone = None
            self._forcelevel = int(args.result["enables"]['force'].level)
            self._dazuo_point = (self._forcelevel - 5) // 10
            if self._always:
                self._tuna_cmd = 'dazuo ' + str(self._dazuo_point)
            else:
                self._tuna_cmd = 'dazuo max'
               
    def _onDone(self, sender, args):
        if self._always:
            self.mush.Execute(self._tuna_cmd)
        else:
            self.mush.Execute('hpbrief')
        
    def _onNoQi(self, sender, args):
        if self._forcelevel >= 150:
            self.mush.Execute('exert recover')
            self.mush.Execute(self._tuna_cmd)
        else:
            self.mush.DoAfter(5, self._tuna_cmd)
        
    def _onNoJing(self, sender, args):
        self.mush.DoAfter(2, 'exert regenerate')
        self.mush.DoAfter(3, self._tuna_cmd)
        
    def _onWait(self, sender, args):
        self.mush.DoAfter(3, self._tuna_cmd)
        
    def _check_jingli(self, sender, args):
        hp = args
        
        _current = hp['neili']
        _max = 2 * hp['neilimax'] - 100
        
        if _current < _max:
            self.mush.Log('当前内力：{}，需打坐到：{}，还差{}，打坐命令{}'.format(_current, _max, _max - _current, self._tuna_cmd))
            self._onNoQi(sender, args)
        else:
            self.Enabled = False
                
            self._Hpbrief.RemoveCallback(self._check_jingli)
            self.mush.Execute('exert recover')

            # execute callback when done.
            self.mush.Log('module [dazuoto] done.')
            if self._after:
                self.Execute('response dazuoto ' + self._after)
            
            self._doEvent('AfterDone')                
    
    def _onStop(self, sender, args):
        self.mush.Log('module [dazuoto] has been halted manually.')
        self._doEvent('AfterStop')
    
    def Start(self, **options):
        self.Enabled = True
        self._always = options.get('always', False)
        self._after = options.get('after', None)

        self.UpdateForceLevel()
        
        if self._always:
            self._tuna_cmd = 'dazuo ' + str(self._dazuo_point)
            self.mush.Log('module [dazuoto]: start dazuo continuous')
            self.mush.Execute(self._tuna_cmd) 
        else:
            self._tuna_cmd = 'dazuo max'
            self._Hpbrief.AddCallback(self._check_jingli)
            self.mush.Log('module [dazuoto]: start dazuo to max...')
            # self.mush.Execute('hpbrief')
            self.mush.Execute('dazuo max')
            
    def Stop(self, **options):
        self.Enabled = False
        self._Hpbrief.RemoveCallback(self._check_jingli)            
        self.mush.DoAfter(1, 'halt')
        