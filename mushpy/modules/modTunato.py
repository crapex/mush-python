# -*- coding:utf-8 -*-

from .module import *

class ModuleTunaTo(Module):
    _initTriList = (
        TriggerDefinition('done', r'[> ]*(..\.\.)*你吐纳完毕，睁开双眼，站了起来。$', '_onDone', 1),
        TriggerDefinition('noqi', r'^[> ]*你现在身体状况太差了，无法集中精神！$', '_onNoQi', 1),
        TriggerDefinition('nojing', r'^[> ]*你现在精不足，无法修行精力！$', '_onNoJing', 1),
        TriggerDefinition('dazuo', r'^[> ]*你运功完毕，深深吸了口气，站了起来。', "_onDazuo", 1),
        TriggerDefinition('wait', r'^[> ]*你正在运行内功加速全身气血恢复，无法静下心来搬运真气。$', '_onWait', 1),
        TriggerDefinition('halt', r'^[> ]*你强行收回精气，站了起来。|^[> ]*你现在不忙。', '_onStop', 1),
        TriggerDefinition('finish', r'^[> ]*你现在精力接近圆满状态。', '_onDone', 1),
        )
    
    def __init__(self, owner, modulename='tunato', **options):
        super().__init__(owner, modulename, **options)
        
        self._forcelevel = 0
        self._dazuo_point = 10
        self._always = False

        # link the useful commands
        self._Effective = owner.Commands['enable']
        self._Hpbrief = owner.Triggers['hpbrief']
        
        # create the alias for user.
        self._alias = Alias(self, self._group, r'^tnt(?:\s+(.*))?$', self._aliasFunction, name='tunato')
        
    def _aliasFunction(self, sender, args):
        param = args.wildcards[0]
        if param == 'stop':
            self.mush.Warning('module [tunato]: halt manually!')
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
                self._tuna_cmd = 'tuna ' + str(self._dazuo_point)
            else:
                self._tuna_cmd = 'tuna max'
       
    def _onDazuo(self, sender, args):
        self._triggers["dazuo"].Enabled = False
        self.mush.Execute(self._tuna_cmd)
               
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
        self.mush.Execute('exert regenerate')
        self._triggers["dazuo"].Enabled = True
        self.mush.Execute("dazuo 200")
        
    def _onWait(self, sender, args):
        self.mush.DoAfter(3, self._tuna_cmd)
        
    def _check_jingli(self, sender, args):
        hp = args
        
        _current = hp['jingli']
        _max = 2 * hp['jinglimax'] - 100
        
        if _current < _max:
            self.mush.Log('当前精力：{}，需吐纳到：{}，还差{}，打坐命令{}'.format(_current, _max, _max - _current, self._tuna_cmd))
            self._onNoQi(sender, args)
        else:
            self.Enabled = False
                
            self._Hpbrief.RemoveCallback(self._check_jingli)
            self.mush.Execute('exert recover')

            # execute callback when done.
            self.mush.Log('module [tunato] done.')
            if self._after:
                self.Execute('response tunato ' + self._after)
            
            self._doEvent('AfterDone')                
    
    def _onStop(self, sender, args):
        self.mush.Log('module [tunato] has been halted manually.')
        self._doEvent('AfterStop')
    
    def Start(self, **options):
        self.Enabled = True
        self._always = options.get('always', False)
        self._after = options.get('after', None)

        self.UpdateForceLevel()
        
        if self._always:
            self._tuna_cmd = 'tuna ' + str(self._dazuo_point)
            self.mush.Log('module [tunato]: start tuna continuous')
            self.mush.Execute(self._tuna_cmd) 
        else:
            self._tuna_cmd = 'tuna max'
            self._Hpbrief.AddCallback(self._check_jingli)
            self.mush.Log('module [tunato]: start tuna to max...')
            # self.mush.Execute('hpbrief')
            self.mush.Execute('tuna max')
            
    def Stop(self, **options):
        self.Enabled = False
        self._Hpbrief.RemoveCallback(self._check_jingli)            
        self.mush.DoAfter(1, 'halt')
        