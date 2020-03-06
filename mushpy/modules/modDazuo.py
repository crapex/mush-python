# -*- coding:utf-8 -*-

from .module import Module, TriggerDefinition, CommandState

class ModuleDazuoTo(Module):
    _triList = (TriggerDefinition('done', r'[> ]*(..\.\.)*你运功完毕，深深吸了口气，站了起来。$', '_onDone', 1),
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
        
        # self.UpdateForceLevel()
        
        # link the useful commands
        self._Effective = self.owner.Commands['enable']
        
    def UpdateForceLevel(self):
        if self._forcelevel == 0:
            self.player.Effective.AfterDone = self._update_forcelevel
            self.player.Effective.Execute()

    def _update_forcelevel(self, sender, args):
        if args.state == CommandState.Success:
            self._Effective.AfterDone = None
            self._forcelevel = int(args["enables"]['force'].level)
            self._dazuo_point = (self._forcelevel - 5) // 10
            if self._always:
                self._dazuo_cmd = 'dazuo ' + str(self._dazuo_point)
            else:
                self._dazuo_cmd = 'dazuo max'
               
    def _onDone(self, sender, args):
        if self._always:
            self.mush.Execute(self._dazuo_cmd)
        else:
            self.mush.Execute('hpbrief')
        
    def _onNoQi(self, sender, args):
        if self._forcelevel >= 150:
            self.mush.Execute('exert recover')
            self.mush.Execute(self._dazuo_cmd)
        else:
            self.mush.DoAfter(5, self._dazuo_cmd)
        
    def _onNoJing(self, sender, args):
        self.mush.DoAfter(2, 'exert regenerate')
        self.mush.DoAfter(3, self._dazuo_cmd)
        
    def _onWait(self, sender, args):
        self.mush.DoAfter(3, self._dazuo_cmd)
        
    def _check_neili(self, sender, args):
        hp = args.result["hp"]
        _current = hp['neili']
        _max = 2 * hp['neilimax'] - 100
        
        if _current < _max:
            self.mush.info('当前内力：{}，需打坐到：{}，还差{}，打坐命令{}'.format(_current, _max, _max - _current, self._dazuo_cmd))
            self._onNoQi(sender, args)
        else:
            self.Enabled = False
                
            self.player.Hpbrief.RemoveCallback(self._check_neili)
            self.mush.Execute('exert recover')

            # execute callback when done.
            self.mush.info('function module [dazuoto] done.')
            if self._after:
                self.Execute('response dazuoto ' + self._after)
            
            self._doEvent('AfterDone')                
    
    def _onStop(self, sender, args):
        self.mush.info('function module [dazuoto] has been halted manually.')
        self._doEvent('AfterStop')
    
    def Start(self, **options):
        self.Enabled = True
        self._always = options.get('always', False)
        self._after = options.get('after', None)

        self.UpdateForceLevel()
        
        if self._always:
            self._dazuo_cmd = 'dazuo ' + str(self._dazuo_point)
            self.mush.info('function module [dazuoto]: start dazuo continuous')
            self.mush.Execute(self._dazuo_cmd) 
        else:
            self._dazuo_cmd = 'dazuo max'
            self.player.Hpbrief.AddCallback(self._check_neili)
            self.mush.info('function module [dazuoto]: start dazuo to max...')
            # self.mush.Execute('hpbrief')
            self.mush.Execute('dazuo max')
            
    def Stop(self, **options):
        self.Enabled = False
        self.player.Hpbrief.RemoveCallback(self._check_neili)            
        self.mush.DoAfter(1, 'halt')