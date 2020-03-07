# -*- coding:utf-8 -*-
from collections import namedtuple
from .mudCmd import MudCommand, TriggerDefinition

Skill = namedtuple('Skill', ['cname', 'name', 'level'])


class CmdSkills(MudCommand):
    '''
    用于skills命令结果获取
    '''
    _initTriList = (
        TriggerDefinition('sk_skill', r'│(?:□|\s*)(\S+)\s*│(\S+)\s*│\S*│\s*(\d+\.\d+)│.*│$', '_onSkillCapture', 1),
        TriggerDefinition('sk_skill_end', r'└─────────────┴─────────────┴───◎ 北大侠客行 ◎──┘', '_onSuccess', 1),
        )      

    # def _onSkillCapture(self, name, line, wildcards):
    def _onSkillCapture(self, sender, args):
        wildcards = args.wildcards
        self._result["skills"].append(Skill(wildcards[0], wildcards[1], float(wildcards[2])))

    def Execute(self, cmd='skills', **params):
        self._result["skills"] = []
        super().Execute(cmd, **params)