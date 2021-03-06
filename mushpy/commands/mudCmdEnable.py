# -*- coding:utf-8 -*-

from ..triggers import EffectiveSkill
from .mudCmd import MudCommand, TriggerDefinition

# enable
class CmdEnable(MudCommand):
    _initTriList = (
            TriggerDefinition('en_skill', r'\s*(\S+)\s*\((\S+)\)\s*：\s*(\S+)\s*有效等级：(\d+)' , '_onEffectiveSkillCapture', 1),
            TriggerDefinition('en_skill_end', r'^\S.*', '_onSuccess', 1),
            )
                
    def _onEffectiveSkillCapture(self, sender, args):
        wildcards = args.wildcards
        _efskill = EffectiveSkill(wildcards[1], wildcards[0], wildcards[2], wildcards[3])
        self._result["enables"][wildcards[1]] = _efskill
        
        self._triggers['en_skill_end'].Enabled = True
    
    def _beforeExecute(self, **params):
        self._triggers['en_skill_end'].Enabled = False
        self._triggers['en_skill'].Enabled = True
    
    def Execute(self, cmd = 'enable', **params):
        self._result["enables"] = {}
        super().Execute(cmd, **params)