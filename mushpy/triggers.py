# -*- coding:utf-8 -*-

from collections import namedtuple
import webbrowser

from .objects import Trigger


EffectiveSkill = namedtuple('EffectiveSkill', ['name', 'basic', 'special', 'level'])


# 以下为特殊的Trigger，定义好特定类（主要是处理回馈数据）

class TriggerRoomTitle(Trigger):
    def __init__(self, owner, group, script = None, **options):
        super().__init__(owner, group, r"^[> ]*(\S*)\s*-\s*(?:\[(野外|城内|门派|0)\])?(?:\s*\[(存盘点|玩家储物柜)\])?$", script, **options)
        self.Enabled = True
        self._roomname = ''
        
    def __call__(self, name, line, wildcards):
        self._roomname = wildcards[0]

class TriggerEffectiveSkill(Trigger):
    def __init__(self, owner, group, script = None, **options):
        super().__init__(owner, group, r'\s*(\S+)\s*\((\S+)\)\s*：\s*(\S+)\s*有效等级：(\d+)', script, **options)
        self.enables = {}
        self.Enabled = True
    
    # override baseclass default
    def __call__(self, name, line, wildcards):
        _efskill = EffectiveSkill(wildcards[1], wildcards[0], wildcards[2], wildcards[3])
        self.enables[wildcards[1]] = _efskill
        
        #super().__call__(name, line, wildcards)  
        for callback in self._callbacks:
            callback(self, self.enables)
            
# need to "set brief long" in pkuxkx
class TriggerHpbrief(Trigger):
    hpKey = (('exp','pot','neilimax','neili','jinglimax','jingli'), \
                      ('qitotal','qimax','qi','jingtotal','jingmax','jing'), \
                      ('zhenqi','yi','food','water','combat','busy'))
                      
    def __init__(self, owner, group, script = None, **options):
        options['name'] = 'hpbrief'                                             # default trigger name: {group}_hpbrief
        options['multiline'] = True
        options['lines'] = 3
        
        super().__init__(owner, group, r'^[> ]*#(\S*)\n#(\S*)\n#(\S*)$', script, **options)
        
        self.hp = {}
        self.Enabled = True                                                     # default: allways enabled
        
    def __tonumber(self, val):
        if val.endswith('K'):
            val = int(float(val[:-1]) * 1000)
        elif val.endswith('M'):
            val = int(float(val[:-1]) * 1000000)
        elif val.startswith('-') and val[1:].isdigit():
            val = int(val)
        elif val.isdigit():
            val = int(val)
            
        return val    
        
    def __call__(self, name, line, wildcards):  
        for lineidx in range(0,3):
            for idx, val in enumerate(wildcards[lineidx].split(r',')):
                self.hp[self.hpKey[lineidx][idx]] = self.__tonumber(val)
        
        #super().__call__(name, line, wildcards)  
        for callback in self._callbacks:
            callback(self, self.hp)
            
class TriggerResponse(Trigger):
    def __init__(self, owner, group, script = None, **options):       
        super().__init__(owner, group, r'^[> ]*系统回馈：(\S+)\s*=\s*(\S+)\s*$', script, **options)
        
        self.response = {}
        self.Enabled = True                                                     # default: always enabled    
    
    def __call__(self, name, line, wildcards):    
        self.response[wildcards[0]] = wildcards[1]

        for callback in self._callbacks:
            callback(self, self.response)
 
            
class TriggerAntiRobot(Trigger):
    def __init__(self, owner, group, script = None, **options):
        super().__init__(owner, group, r'^http://pkuxkx.(?:net|com)/(antirobot/.+$)', script, **options)
        
        self.Enabled = True                                                     # default: always enabled
        
    def __call__(self, name, line, wildcards):
        param = wildcards[0]
        url = r'http://www.pkuxkx.net/{}'.format(param)
        
        webbrowser.open(url)
