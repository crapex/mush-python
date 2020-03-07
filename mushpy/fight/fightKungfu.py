# -*- coding:utf-8 -*-

from ..objects import MushObject, Alias

class Kungfu(MushObject):
    def __init__(self, owner, **options):
        super().__init__(owner)
    
    def _execute_cmd_with_npc(self, cmd, npc=None):
        if npc:
            cmd = cmd + ' ' + npc
            
        self.mush.Execute(cmd)
    
    def before_fight(self, npc):
        pass
        
    def after_fight(self, npc):
        pass
        
    def in_fighting(self, qishi, npc):
        pass        
    
    def pfm_remove_weapon(self, npc):
        pass
    
    def perform(self, qishi, npc):
        pass
    
class KungfuGaibang(Kungfu):
    def __init__(self, owner, **options):
        super().__init__(owner)
        self._alias = Alias(self, 'fight', r'^(tiao|xiao|zhuan|chuo)(?:\s+(.*))?$', self._ali_perform, name='ali_gb')
     
    def _prepare_weapon(self):
        # self.mush.Execute('unwield all')
        self.mush.Execute('wield stick at right')
        self.mush.Execute('wield staff at right')
     
    def _ali_perform(self, sender, args):
        cmd = args.wildcards[0]
        npc = args.wildcards[1]
        if cmd == 'tiao':
            self._prepare_weapon()
            self._execute_cmd_with_npc('perform dagou-bang.tiao', npc)
        elif cmd == 'zhuan':
            self._prepare_weapon()
            self._execute_cmd_with_npc('perform dagou-bang.zhuan', npc)
        elif cmd == 'chuo':
            self._prepare_weapon()
            self._execute_cmd_with_npc('perform dagou-bang.chuo', npc)
        elif cmd == 'xiao':
            self.mush.Execute('enforce 50')
            self._execute_cmd_with_npc('perform xianglong-zhang.xiao', npc)
            self.mush.Execute('enforce 0')
        
    def before_fight(self, npc=None):
        self.mush.Execute('exert powerup')
        
    def after_fight(self, npc=None):
        self._prepare_weapon()
        self._execute_cmd_with_npc('perform dagou-bang.tiao', npc)
        
    def in_fighting(self, qishi, npc=None):
        if qishi >= 20:
            self._prepare_weapon()
            self._execute_cmd_with_npc('perform dagou-bang.zhuan', npc)
        elif qishi >= 14:
            self._prepare_weapon()
            self._execute_cmd_with_npc('perform dagou-bang.chan', npc)
     
    def perform(self, what, npc=None):
        if what == 'pw':
            self._prepare_weapon()
            self._execute_cmd_with_npc('perform dagou-bang.chuo', npc)
            pass
        elif what == 'ph':
            self._prepare_weapon()
            self._execute_cmd_with_npc('perform dagou-bang.zhuan', npc)
        elif what == 'pb':
            self._prepare_weapon()
            self._execute_cmd_with_npc('perform dagou-bang.chan', npc)
        elif what == 'pr':
            self._prepare_weapon()
            self._execute_cmd_with_npc('perform dagou-bang.tiao', npc)
            
class KungfuTianlong(Kungfu):
    def __init__(self, owner, **options):
        super().__init__(owner)
        self._alias = Alias(self, 'fight', r'^(bm|lm|qf|fx)(?:\s+(.*))?$', self._ali_perform, name='ali_tl')
     
    def _prepare_weapon(self):
        # self.mush.Execute('unwield all')
        self.mush.Execute('wield sword at right')
        # self.mush.Execute('wield staff at right')
     
    def _ali_perform(self, sender, args):
        cmd = args.wildcards[0]
        npc = args.wildcards[1]
        if cmd == 'bm':
            self._prepare_weapon()
            self._execute_cmd_with_npc('exert beiming', npc)
        elif cmd == 'lm':
            self._prepare_weapon()
            self._execute_cmd_with_npc('perform liumai-shenjian.liumai', npc)
        elif cmd == 'qf':
            self._prepare_weapon()
            self._execute_cmd_with_npc('perform liumai-shenjian.qifa', npc)
        elif cmd == 'fx':
            self._prepare_weapon()
            self._execute_cmd_with_npc('perform yiyang-zhi.fuxue', npc)
        
    def before_fight(self, npc=None):
        # self.mush.Execute('exert qi')
        pass
        
    def after_fight(self, npc=None):
        self._execute_cmd_with_npc('exert beiming', npc)
        
    def in_fighting(self, qishi, npc=None):
        if qishi >= 16:
            self._execute_cmd_with_npc('perform yiyang-zhi.fuxue', npc)
            self.mush.DoAfter(1, 'perform liumai-shenjian.liumai')
        
        elif qishi >= 12:
            self._prepare_weapon()
            self._execute_cmd_with_npc('perform liumai-shenjian.liumai', npc)
        
    def perform(self, what, npc=None):
        if what == 'pw':
            self._prepare_weapon()
            self._execute_cmd_with_npc('perform liumai-shenjian.liumai', npc)
            pass
        elif what == 'ph':
            self._prepare_weapon()
            self._execute_cmd_with_npc('perform liumai-shenjian.qifa', npc)
        elif what == 'pb':
            self._prepare_weapon()
            self._execute_cmd_with_npc('perform yiyang-zhi.fuxue', npc)
        elif what == 'pr':
            pass