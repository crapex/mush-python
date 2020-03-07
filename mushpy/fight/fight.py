# -*- coding:utf-8 -*-

from ..objects import MushObject, Trigger, Alias
from ..commands import TriggerDefinition, CommandState
from .fightKungfu import *

class Fight(MushObject):
    _initTriList = (
        TriggerDefinition('fight', r'^[> ]*你对著.*说道：.*，领教阁下的高招！|^[> ]*你大喝一声，开始对.*发动攻击！', '_onFightStart', 1),
        TriggerDefinition('hit', r'^[> ]*你大喝一声，开始对.*发动攻击！|^[> ]*你对著.*大喝一声：看招！', '_onFightStart', 1),
        TriggerDefinition('kill', r'^[> ]*你对着.*吼道：「畜生！你死期已到，今天就让.*我送你上西天吧！」|^[> ]*你长笑一声，开始对周围众人痛下杀手！', '_onFightStart', 1),
        TriggerDefinition('qishi', r'^[> ]*你在攻击中不断积蓄攻势。\(气势：(\d+)%\)', '_onCheckQishi', 1),
        TriggerDefinition('end', r'^[> ]*经过一段时间后，你终于完全从紧张地战斗氛围中解脱出来。', '_onFightEnd', 1),
        )
    
    def __init__(self, owner, **options):
        super().__init__(owner)
        
        self.options = options
        self._group = 'fight'
        
        self.npc = None
        
        self._initTriggers()
        
        for tri in self._triggers.values():
            tri.Enabled = True
        
        self._aliaspfm = Alias(self, self._group, r'^(pb|pw|ph|pr)(?:\s(.+))?$', self._ali_perform, name='ali_pfm')
        self._aliasfight = Alias(self, self._group, r'^(f|k|h|ka)\s(.+)$', self._ali_fight, name='ali_fight')
        
        if owner.playerMenpai == 'GB':
            self.pfm = KungfuGaibang(self)
        elif owner.playerMenpai == 'TL':
            self.pfm = KungfuTianlong(self)
        else:
            self.pfm = Kungfu(self)

    def _initTriggers(self):
        '''
        初始化保存在元组（self._initTriList）中的触发器列表
        '''
        self._triggers = {}
        for tri in self._initTriList:
            if tri.lines > 1:
                self._triggers[tri.name] = Trigger(self, self._group, tri.regx, getattr(self, tri.func), multiline = True, lines = tri.lines, name = tri.name)
            else:
                self._triggers[tri.name] = Trigger(self, self._group, tri.regx, getattr(self, tri.func), name = tri.name)
     
    def _ali_fight(self, sender, args):
        mode = args.wildcards[0]
        self.npc = args.wildcards[1]
        
        self.pfm.before_fight(self.npc)
        if mode == 'f':
            self.mush.Execute('fight %s' % self.npc)
        elif mode == 'h':
            self.mush.Execute('hit %s' % self.npc)
        elif mode == 'k':
            self.mush.Execute('kill %s' % self.npc)
        elif mode == 'ka':
            self.mush.Execute('killall %s' % self.npc)
     
    def _ali_perform(self, sender, args):
        # self.pfm.perform(line, self.npc)
        wildcards = args.wildcards
        if wildcards[1]:
            self.pfm.perform(wildcards[0], wildcards[1])
        else:
            self.pfm.perform(wildcards[0], None)
     
    def _onFightStart(self, sender, args):
        mode = args.line[:4]
        if mode == 'kill':
            self.mode = 'KILL'
        else:
            self.mode = 'FIGHT'
            
        # execute perform : such as perform dagou-bang.tiao
        self.pfm.after_fight(self.npc)
        
    def _onCheckQishi(self, sender, args):
        w = args.wildcards
        qishi = int(w[0])
        self.pfm.in_fighting(qishi, self.npc)
        
    def _onFightEnd(self, sender, args):
        self.mode = 'IDLE'