# -*- coding:utf-8 -*-

from ..objects import MushObject, Alias, Trigger, Timer
from ..commands import TriggerDefinition, CommandState

class Job(MushObject):
    JOB_NAME = 'NONE'
    
    _initTriList = ()
    
    def __init__(self, owner, name, **options):
        super().__init__(owner)

        self._jobname = name
        self._options = options
        
        self._playerid = owner.playerID
        self._playername = owner.playerName
        
        self._cmdWait = self.owner.Commands["wait"]

        jobalimatch = '^{}(?:\s(.*))?$'.format(self._jobname)
        self._job_alias = Alias(self, self._jobname, jobalimatch, self._ali_job_command, name=self._jobname)
        
        self._total = self.mush.GetVariable('{}_total'.format(self._jobname))
        self._success = self.mush.GetVariable('{}_success'.format(self._jobname))
        self._failure = self.mush.GetVariable('{}_failure'.format(self._jobname))
        self._location = self.mush.GetVariable('{}_location'.format(self._jobname))
        
        if not self._total:
            self.total = 0
        else:
            self.total = int(self.total)
            
        if not self._success:
            self.success = 0
        else:
            self.success = int(self.success)
            
        if not self._failure:
            self.failure = 0
        else:
            self.failure = int(self.failure)
            
        if not self._location:
            self.location = '未知地点'
            
        self._initTriggers()
            
    def _initTriggers(self):
        '''
        初始化保存在元组（self._initTriList）中的触发器列表
        '''
        self._triggers = {}
        for tri in self._initTriList:
            if tri.lines > 1:
                self._triggers[tri.name] = Trigger(self, self._jobname, tri.regx, getattr(self, tri.func), multiline = True, lines = tri.lines, name = tri.name)
            else:
                self._triggers[tri.name] = Trigger(self, self._jobname, tri.regx, getattr(self, tri.func), name = tri.name)

    @property
    def total(self):
        return self._total
    
    @total.setter
    def total(self, value):
        self._total = value
        self.mush.SetVariable('{}_total'.format(self._jobname), self._total)
        
    @property
    def success(self):
        return self._success
    
    @success.setter
    def success(self, value):
        self._success = value
        self.mush.SetVariable('{}_success'.format(self._jobname), self._success)    
    
    @property
    def failure(self):
        return self._failure
    
    @failure.setter
    def failure(self, value):
        self._failure = value
        self.mush.SetVariable('{}_failure'.format(self._jobname), self._failure)    
    
    @property
    def location(self):
        return self._location
    
    @location.setter
    def location(self, value):
        self._location = value
        self.mush.SetVariable('{}_location'.format(self._jobname), self._location)   
    
    def _ali_job_command(self, name, line, wildcards):
        pass
    
