# -*- coding:utf-8 -*-

import re
from .mudCmd import MudCommand, TriggerDefinition

class Room:
    def __init__(self):
        self.Name = ''
        self.Relation = ''
        self.Description = ''
        self.Exit = ''
        self.Season = ''
        self.Weather = ''
        self.Objects = None

class CmdRoom(MudCommand):
    '''
    用于类似look命令判断位置
    '''
    _initTriList = (
            TriggerDefinition('room_name', r'^[> ]*([^-]*)\s*-\s*(?:\[(野外|城内|门派|0)\])?(?:\s*\[(存盘点|玩家储物柜)\])?$', '_onNameTrigger', 1),
            TriggerDefinition('room_relation', r'^[>]*\s{10,}(\S+)\s+$', '_onRelationTrigger', 1),
            TriggerDefinition('room_desc', r'^\s{0,9}(\S+)\s*$', '_onDescTrigger', 1),
            TriggerDefinition('room_weather', r'^\s*「(.*)」: (.*)$', '_onWeatherTrigger', 1),
            TriggerDefinition('room_exits', r'\s*这里(?:明显|唯一)的(?:出口|方向)(?:是|有)(.*)$|^\s*这里没有任何明显的(?:出路|方向|出口)\。$', '_onSuccess', 1),
            TriggerDefinition('room_retry', r'^(> |)风景要慢慢的看\w*', '_onRetry', 1),
            )
    
    def __init__(self, owner, group):
        super().__init__(owner, group)
    
    def _onNameTrigger(self, sender, args):
        wildcards = args.wildcards
        self._result["room"].Name = wildcards[0].strip()
        self._triggers['room_retry'].Enabled = False
        self._triggers['room_name'].Enabled = False
        self._triggers['room_relation'].Enabled = True
        self._triggers['room_desc'].Enabled = True
        self._triggers['room_weather'].Enabled = True
        self._triggers['room_exits'].Enabled = True
        
    def _onRelationTrigger(self, sender, args):
        wildcards = args.wildcards
        self._result["room"].Relation += wildcards[0].strip()

    def _onDescTrigger(self, sender, args):
        wildcards = args.wildcards
        desc = wildcards[0].strip()
        omit_exits = re.match(r'^这里(?:明显|唯一)的(?:方向|出口)|^这里没有任何明显的(?:出路|方向)', desc)
        omit_changjiang = re.match(r'一片浓雾中，什么也看不清。', desc)
        omit_page = re.match(r'未完继续', desc) 
        omit_weather = re.match(r'「\S*」:', desc)
        omit_node = re.match('^你可以看看', desc)

        if omit_exits != None or omit_weather != None or omit_node != None or omit_changjiang != None or omit_page != None:
            desc=''
        
        self._result["room"].Description += desc     
        self._triggers['room_relation'].Enabled = False
          
    def _onWeatherTrigger(self, sender, args):
        wildcards = args.wildcards
        self._result["room"].Season = wildcards[0].strip()
        self._result["room"].Weather = wildcards[1].strip()
        self._triggers['room_desc'].Enabled = False
    
    def _onRetry(self, sender, args):
        self.mush.DoAfter(0.5, 'look')
        
    def _onSuccess(self, sender, args):
        line, wildcards = args.line, args.wildcards
        if re.match(r'\s*这里没有任何明显的出路', line):
            exits='look'
        else:
            exits=wildcards[0].strip()
        exits = exits.replace('。','').replace(' ', '').replace('、', ';').replace('和', ';')  # 去除句号、空格；将顿号、和转换为;
        exit_list = exits.split(';')
        exit_list.sort()
        self._result["room"].Exit = ';'.join(exit_list)
                
        super()._onSuccess(sender, args)        
    
    def _beforeExecute(self, **params):
        self._result["room"] = Room()
        self.Enable(False)
        self._triggers['room_retry'].Enabled = True
        self._triggers['room_name'].Enabled = True
        
    def Execute(self, cmd = 'look', **params):        
        return super().Execute(cmd, **params)