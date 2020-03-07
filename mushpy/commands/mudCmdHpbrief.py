# -*- coding:utf-8 -*-

from .mudCmd import MudCommand, CommandState, TriggerDefinition

class CmdHpbrief(MudCommand):
    _initTriList = (TriggerDefinition('hpbrief', r'^#(\S*)\n#(\S*)\n#(\S*)$', '_onSuccess', 3),)
    
    hpKey = (('exp', 'pot', 'neilimax', 'neili', 'jinglimax', 'jingli'), \
              ('qitotal', 'qimax', 'qi', 'jingtotal', 'jingmax', 'jing'), \
              ('zhenqi', 'yi', 'food', 'water', 'combat', 'busy'))
                 
    def _tonumber(self, val):
        if isinstance(val, str):
            if val.endswith('K'):
                val = int(float(val[:-1]) * 1000)
            elif val.endswith('M'):
                val = int(float(val[:-1]) * 1000000)
            elif val.isnumeric():
                val = int(val)
        return val
        
    # def _onSuccess(self, name, line, wildcards):
    def _onSuccess(self, sender, args):
        wildcards = args.wildcards
        try:
            self._result["hp"] = {}
            for lineidx in range(0, 3):
                for idx, val in enumerate(wildcards[lineidx].split(',')):
                    self._result["hp"][self.hpKey[lineidx][idx]] = self._tonumber(val)
                    
            self._generator.send(CommandState.Success)
        except StopIteration:
            pass

    def Execute(self, cmd='hpbrief', **params):
        super().Execute(cmd, **params)