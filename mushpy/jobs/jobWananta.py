# -*- coding:utf-8 -*-

from .job import Job, TriggerDefinition

class JobWananta(Job):
    _initTriList = (
        TriggerDefinition("leveldone", r"^[> ]*暗处的番邦武士对你一抱拳，道“阁下果然武功不凡", "_onleveldone", 1),
        TriggerDefinition("levelup", r"^[> ]*万安塔(.*)层\s*-\s*", "_onlevelup", 1),
        TriggerDefinition("killwin", r"^[> ]*你战胜了番邦武士!|^[> ]*经过一段时间后，你终于完全从紧张地战斗氛围中解脱出来", "_onkillwin", 1)
        )
    def __init__(self, owner, name='wat', **options):
        super().__init__(owner, name, **options)
        
        self.job = "万安塔"

    def _go_up(self, mod, args):
        self.mush.Execute('exert recover')
        self.mush.Execute('exert regenerate')
        self.mush.Execute('up')

    def _dazuotomax(self, mod, args):
        self.owner.RunModule('dazuoto', afterDone=self._go_up)

    def _onkillwin(self, sender, args):
        self.mush.Execute('k wushi')
        
    def _onleveldone(self, sender, args):
        if self.level < self.level_max:
            # liao,no dazuotomax, directly up
            self.owner.RunModule('liaoshang', afterDone=self._go_up)
        else:
            # end, out
            self.mush.Execute('qiao luo')
            self._enabled = False
            for tri in self._triggers.values():
                tri.Enabled = False

    def _onlevelup(self, sender, args):
        levelch = args.wildcards[0]
        self.level = '零一二三四五六七八九'.find(levelch)
        self.mush.Execute('ka wushi')
    
    def _start_wananta(self, mod, args):
        self.mush.Execute('exert recover')
        self.mush.Execute('ask ke about 进塔')
    
    def _ali_job_command(self, sender, args):
        # level = wildcards[0]   设置爬几层
        level = args.wildcards[0]
        
        try:
            self.level_max = int(level)
        except ValueError:
            self.level_max = 3
            
        self._enabled = True
        for tri in self._triggers.values():
            tri.Enabled = True
        self.owner.RunModule('dazuoto', afterDone=self._start_wananta)
