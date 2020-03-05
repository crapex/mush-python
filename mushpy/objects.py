# -*- coding:utf-8 -*-

from collections import namedtuple
from .const import Colors, SendTo, TriggerFlag, TimerFlag, AliasFlag
from .mush import MushHelper

class MushObject:
    def __init__(self, owner):
        self._owner = owner
        if owner:
            self._mushHelper = owner.mush

    @property
    def mush(self):
        if self._mushHelper:
            res = self._mushHelper
        elif self._owner:
            res = self._owner.mush
        else:
            res = None
            
        assert(isinstance(res, MushHelper), "未正确配置MushHelper，请检查！".format(self.name))
        return res
    
    @property
    def owner(self):
        return self._owner
    
TriggerEventArgs = namedtuple("TriggerEventArgs", ["name", "line", "wildcards"])
AliasEventArgs = namedtuple("AliasEventArgs", ["name", "line", "wildcards"])
TimerEventArgs = namedtuple("TimerEventArgs", ["name"])

class Trigger(MushObject):
    def __init__(self, owner, group, match, script = None, **options):
        super().__init__(owner)

        self._group = group
        self._match = match
        self._options = options
        if 'name' in options.keys():
            if self._group:
                self._name = '{}_{}'.format(self._group, options['name'])
            else:
                self._name = '{}_{}'.format(options['name'], self.mush.GetUniqueNumber)
        else:
            self._name = 'tri_{}'.format(self.mush.GetUniqueNumber)
        
        self._sendto = options.get('sendto', SendTo.World)
        self._multiline = options.get('multiline', False)
        self._lines = options.get('lines', 1)
        self._color = options.get('color', Colors.NOCHANGE)
        self._sequence = options.get('sequence', 100)
        self._flag = options.get('flag', None)
        self._flag = self._flag | TriggerFlag.ReplaceTemporaryRegularKeep if self._flag else TriggerFlag.ReplaceTemporaryRegularKeep
        
        self._callbacks = []
        if script and callable(script):
            self.AddCallback(script)
        
        self.mush.registerTrigger(self._name, self)
        self.mush.AddTriggerEx(self._name, self._match, '', self._flag, self._color, 0, '', self.mush.TriggerHandlerName, self._sendto, self._sequence)
        
        self.mush.SetTriggerOption(self._name, 'group', self._group)
        
        if self._multiline:
            self.mush.SetTriggerOption(self._name, 'multi_line', 1)
            self.mush.SetTriggerOption(self._name, 'lines_to_match', self._lines)
    
    @property
    def Enabled(self):
        val = self.mush.GetTriggerOption(self._name, 'enabled')
        return val
     
    @Enabled.setter
    def Enabled(self, value):
        self.mush.EnableTrigger(self._name, value)
    
    def AddCallback(self, callback):
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def RemoveCallback(self, callback):
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def __del__(self):
        self.mush.unregisterTrigger(self._name)
    
    def __call__(self, name, line, wildcards):
        sender, args = self, TriggerEventArgs(name, line, wildcards)
        
        for callback in self._callbacks:
            callback(sender, args)
            
class Alias(MushObject):
    def __init__(self, owner, group, match, script = None, **options):
        super().__init__(owner)
        self._group = group
        self._match = match
        self._options = options
        
        if 'name' in options.keys():
            if self._group:
                self._name = '{}_{}'.format(self._group, options['name'])
            else:
                self._name = '{}_{}'.format(options['name'], self.mush.GetUniqueNumber)
        else:
            self._name = 'ali_{}'.format(self.mush.GetUniqueNumber)
        
        self._flag = options.get('flag', None)
        self._flag = self._flag | AliasFlag.ReplaceTemporaryExpandRegularEnabled if self._flag else AliasFlag.ReplaceTemporaryExpandRegularEnabled
        
        self._callbacks = []
        if script and callable(script):
            self.AddCallback(script)
        
        self.mush.registerAlias(self._name, self)
        self.mush.AddAlias(self._name, self._match, '', self._flag, self.mush.AliasHandlerName)

        self.mush.SetAliasOption(self._name, 'group', self._group)
        
    @property
    def Enabled(self):
        val = self.mush.GetAliasOption(self._name, 'enabled')
        return val
     
    @Enabled.setter
    def Enabled(self, value):
        self.mush.EnableAlias(self._name, value)
    
    def AddCallback(self, callback):
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def RemoveCallback(self, callback):
        if callback not in self._callbacks:
            self._callbacks.remove(callback)
    
    def __del__(self):
        self.mush.unregisterAlias(self._name)
    
    def __call__(self, name, line, wildcards):
        sender, args = self, AliasEventArgs(name, line, wildcards)
        
        for callback in self._callbacks:
            callback(sender, args)
            
class Timer(MushObject):
    def __init__(self, owner, group, time_in_second, script = None, **options):
        super().__init__(owner)
        
        self._group = group
        self._options = options
        
        if 'name' in options.keys():
            if self._group:
                self._name = '{}_{}'.format(self._group, options['name'])
            else:
                self._name = '{}_{}'.format(options['name'], self.mush.GetUniqueNumber)
        else:
            self._name = 'timer_{}'.format(self.mush.GetUniqueNumber)
        
        self._time = time_in_second      
        self._hour = self._time // 3600
        self._second = self._time - self._hour * 3600
        self._minute = self._second // 60
        self._second = self._second - self._minute * 60
        
        self._flag = options.get('flag', None)
        self._flag = self._flag | TimerFlag.ReplaceTemporary if self._flag else TimerFlag.ReplaceTemporary
        
        self._callbacks = []
        if script and callable(script):
            self.AddCallback(script)
        
        self.mush.registerTimer(self._name, self)
        self.mush.AddTimer(self._name, self._hour, self._minute, self._second, '', self._flag, self.mush.TimerHandlerName)

        self.mush.SetTimerOption(self._name, 'group', self._group)

    def SetTimeout(self, time_in_second):
        self._time = time_in_second      
        self._hour = self._time // 3600
        self._second = self._time - self._hour * 3600
        self._minute = self._second // 60
        self._second = self._second - self._minute * 60
        
        self.mush.SetTimerOption(self._name, 'hour', self._hour)
        self.mush.SetTimerOption(self._name, 'minute', self._minute)
        self.mush.SetTimerOption(self._name, 'second', self._second)
    
    def GetTimeout(self):
        return self._hour * 3600 + self._minute * 60 + self._second
    
    def Reset(self):
        self.mush.EnableTimer(self._name, True)
        self.mush.ResetTimer(self._name)
   
    @property
    def Enabled(self):
        val = self.mush.GetTimerOption(self._name, 'enabled')
        return val
     
    @Enabled.setter
    def Enabled(self, value):
        self.mush.EnableTimer(self._name, value)
    
    def AddCallback(self, callback):
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def RemoveCallback(self, callback):
        if callback not in self._callbacks:
            self._callbacks.remove(callback)
    
    def __del__(self):
        self.mush.unregisterTimer(self._name)
    
    def __call__(self, name):
        sender, args = self, TimerEventArgs(name)
        for callback in self._callbacks:
            callback(sender, args)