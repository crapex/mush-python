# -*- coding:utf-8 -*-

from .mudCmd import MudCommand, TriggerDefinition

# sc/score
class CmdScore(MudCommand):
    _triList = (TriggerDefinition('sc_start', r'^≡━━━━◎人物详情◎━━━━━━━━━━━━━━━━━━━━━━━━━━≡', '_onStartCapture', 1),
                TriggerDefinition('sc_title', r'^[> ]*【.*】(\S+)\s(\S+)\((.*)\)', '_onTitleCapture', 1),
                TriggerDefinition('sc_prop', r'^\s*膂力：\[\s*(\d+)\]  悟性：\[\s*(\d+)\]  根骨：\[\s*(\d+)\]  身法：\[\s*(\d+)\]', '_onPropCapture', 1),
                TriggerDefinition('sc_money', r'^\s*存\s*款：\s*(\S+)$', '_onMoneyCapture', 1),
                TriggerDefinition('sc_end', r'^≡━━━━━━━━━━━━━━━━━━━━━━━━◎北大侠客行◎━━━━≡', '_onSuccess', 1))
    
    def __init__(self, group, **options):
        super().__init__(group, **options)
        self.info = {}
    
    # def _onStartCapture(self, name, line, wildcards):
    def _onStartCapture(self, tri):
        name, line, wildcards = tri.info
        self._triggers['sc_title'].Enabled = True
        self._triggers['sc_prop'].Enabled = True
        self._triggers['sc_money'].Enabled = True
        self._triggers['sc_end'].Enabled = True
    
    # def _onTitleCapture(self, name, line, wildcards):
    def _onTitleCapture(self, tri):
        name, line, wildcards = tri.info
        self.info['name'] = wildcards[1].strip()
        self.info['id'] = wildcards[2].strip().lower()
        title = wildcards[0]
        
        if title.find('丐帮') >= 0:
            self.info['menpai'] = 'GB'
        elif title.find('天龙寺') >= 0:
            self.info['menpai'] = 'TL'
        elif title.find('武当') >= 0:
            self.info['menpai'] = 'WD'
        elif title.find('桃花岛') >= 0:
            self.info['menpai'] = 'TH'
        elif title.find('朝廷') >= 0:
            self.info['menpai'] = 'CT'
        else:
            self.info['menpai'] = 'NA'
        
    # def _onPropCapture(self, name, line, wildcards):
    def _onPropCapture(self, tri):
        name, line, wildcards = tri.info
        self.info['str'] = int(wildcards[0])
        self.info['int'] = int(wildcards[1])
        self.info['con'] = int(wildcards[2])
        self.info['dex'] = int(wildcards[3])
        
    # def _onMoneyCapture(self, name, line, wildcards):
    def _onMoneyCapture(self, tri):
        name, line, wildcards = tri.info
        self.info['money'] = wildcards[0].strip()
        
    def _beforeExecute(self, **params):
        '''
        default before execute:
          enable the group
        '''
        self.Enable(False)
        self._triggers['sc_start'].Enabled = True
        func = self._events['BeforeExecute']
        if callable(func):
            func(self)   
    
    def Execute(self, cmd='score', **params):
        super().Execute(cmd, **params)